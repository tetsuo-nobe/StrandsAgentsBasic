"""
multiagent/04_invocation_state.py
【ステートの共有】Graph で invocation_state を使い、全エージェント・全ツールで
「裏方の状態（ユーザーの使用言語・会社名など）」を共有するサンプル。

invocation_state とは:
- Graph（や Swarm）の呼び出し時に dict を渡すと、その内容がパターン内の全エージェント・
  全ツール・ツール関連フックに自動的に伝播する仕組み。
- 最大の特徴は「LLM のプロンプトには載せずに」コンテキストや設定を共有できること。
  例: 使用言語・会社名・user_id などの識別子、DB 接続オブジェクトなど。
- プロンプトに書くとトークンの無駄になったり、LLM が本文に混ぜてしまう恐れがある情報を、
  コードだけが参照する「サイドチャネル」として安全に受け渡せる。

どこに届くか:
- 各エージェント（**kwargs 経由）
- ツール（@tool(context=True) を付けた関数の ToolContext.invocation_state から読める）
- ツール関連フック（BeforeToolCallEvent / AfterToolCallEvent など）

このサンプルのシナリオ（書籍情報の提示）:
    書籍名を渡すと、「ユーザーの言語に翻訳された書籍情報」＋「そのユーザー向けの割引率」が
    返る、という2段階の処理を Graph で組む。

    - Agent#1 book_manager（書籍情報管理エージェント）
        * get_user_language … 共有ステートから使用言語を取得するツール
        * get_book_info     … 書籍名から書籍情報（定価を含む）を取得するツール（デモ用に固定データ）。
                              使用言語に応じて言語版（例: Japanese なら日本語版・円建て定価）を選ぶ。
    - Agent#2 discount_manager（ディスカウント管理エージェント）
        * get_company_name  … 共有ステートから会社名を取得するツール
        * get_discount_rate … 書籍IDと会社名から割引率を返すツール（デモ用に固定データ）。

    book_manager が選んだ書籍情報（書籍IDを含む）が discount_manager へ自動伝播し、
    discount_manager がその書籍IDと「共有ステートの会社名」から割引率を提示する。
    使用言語も会社名もプロンプトには一切書かず、invocation_state だけで共有している点がポイント。

    幻覚（ハルシネーション）対策:
    軽量モデル（Nova Lite）は、ツールが返したタイトルや金額を最終文で言い換えてしまう
    ことがある。そこで本サンプルでは「LLM に推論させる部分（どのツールをどう呼ぶか）」と
    「値を確定的に扱う部分（最終的な提示文）」を分離する。各ツールは戻り値を FACTS に記録し、
    最終回答は format_final_answer() が FACTS からコードで機械的に組み立てる。これにより
    タイトル・定価・割引率・割引後価格は LLM の言い換えに左右されず常に正確になる。

    確認方法: ツールが invocation_state から読み取った値を TOOL_LOG に記録し、実行後に
    まとめて表示する（共有できた確実な証拠）。LLM 自身の生成文も参考として併記するが、
    そこには幻覚が混じり得る。

参考: https://strandsagents.com/docs/user-guide/concepts/multi-agent/multi-agent-patterns/
"""

from strands import Agent, tool, ToolContext
from strands.models.bedrock import BedrockModel
from strands.multiagent import GraphBuilder

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)

# ツールが invocation_state から実際に読み取った値を記録する場所。
# （LLM の出力とは独立に「状態が届いたか」をコードで検証するために使う）
TOOL_LOG: list[str] = []

# ツールが返した「確定データ」を保持する場所。
# 最終的な提示文は LLM に作文させず、ここに溜めた値からコードで組み立てる。
# こうするとタイトルや金額が LLM の言い換え（幻覚）で変わることがなくなる。
FACTS: dict = {}


# ===========================================================================
# Agent#1（書籍情報管理エージェント）が使うツール
# ===========================================================================
@tool(context=True)
def get_user_language(tool_context: ToolContext) -> str:
    """
    ユーザーの使用言語を取得する。invocation_state の lang を参照する。
    （プロンプトには含まれない「裏方の状態」から読み取る点がポイント）

    Returns:
        str: 使用言語（例: "Japanese" / "English"）
    """
    lang = tool_context.invocation_state.get("lang", "English")
    TOOL_LOG.append(f"get_user_language が受け取った lang = {lang}")
    return lang


@tool
def get_book_info(book_title: str, language: str) -> dict:
    """
    書籍名と言語から書籍情報を取得する（デモ用に固定データを返す）。
    language には get_user_language で取得した使用言語を渡すこと。
    指定言語版が無い場合は英語版にフォールバックする。

    Args:
        book_title: 書籍名（日本語名・英語名のどちらでも可）
        language: 表示に使う言語（例: "Japanese" / "English"）

    Returns:
        dict: 書籍情報（book_id / title / language / author / price / currency）
    """
    # デモ用の固定カタログ。book_id は言語をまたいで同一。
    # 言語版ごとに title と定価（price・通貨 currency）が変わる。
    catalog = {
        "B001": {
            "author": "Eric Evans",
            "titles": {
                "Japanese": "エリック・エヴァンスのドメイン駆動設計",
                "English": "Domain-Driven Design",
            },
            # 言語版ごとの定価（通貨込み）
            "prices": {
                "Japanese": {"price": 5720, "currency": "JPY"},
                "English": {"price": 54.99, "currency": "USD"},
            },
        },
    }
    # 書籍名（日英どちらでも）から book_id を引くための対応表。
    title_to_id = {
        "エリック・エヴァンスのドメイン駆動設計": "B001",
        "ドメイン駆動設計": "B001",
        "domain-driven design": "B001",
        "ddd": "B001",
    }

    book_id = title_to_id.get(book_title.strip().lower(), None)
    if book_id is None:
        # 完全一致しない場合も、デモなので既定の1冊にフォールバックする。
        book_id = "B001"

    entry = catalog[book_id]
    # 指定言語版が無ければ英語版にフォールバック（title・定価とも）。
    title = entry["titles"].get(language, entry["titles"]["English"])
    price_info = entry["prices"].get(language, entry["prices"]["English"])
    price = price_info["price"]
    currency = price_info["currency"]
    TOOL_LOG.append(
        f"get_book_info が返した book_id = {book_id}, language = {language}, "
        f"title = {title}, price = {price} {currency}"
    )
    book_info = {
        "book_id": book_id,
        "title": title,
        "language": language,
        "author": entry["author"],
        "price": price,        # 定価
        "currency": currency,  # 通貨
    }
    # 最終提示をコードで組み立てるため、確定データを保持しておく。
    FACTS["book"] = book_info
    return book_info


# ===========================================================================
# Agent#2（ディスカウント管理エージェント）が使うツール
# ===========================================================================
@tool(context=True)
def get_company_name(tool_context: ToolContext) -> str:
    """
    ユーザーの会社名を取得する。invocation_state の company を参照する。
    （プロンプトには含まれない「裏方の状態」から読み取る点がポイント）

    Returns:
        str: 会社名（例: "Acme Corp"）
    """
    company = tool_context.invocation_state.get("company", "unknown")
    TOOL_LOG.append(f"get_company_name が受け取った company = {company}")
    return company


@tool
def get_discount_rate(book_id: str, company: str) -> dict:
    """
    書籍IDと会社名から割引率を算出する（デモ用に固定データを返す）。
    book_id は Agent#1 の書籍情報から、company は get_company_name から渡すこと。

    Args:
        book_id: 対象書籍のID（例: "B001"）
        company: 顧客の会社名（例: "Acme Corp"）

    Returns:
        dict: 割引情報（book_id / company / discount_rate）
    """
    # デモ用の固定割引テーブル。(book_id, company) ごとに割引率を決める。
    discount_table = {
        ("B001", "Acme Corp"): 0.30,
        ("B001", "Globex"): 0.15,
    }
    rate = discount_table.get((book_id, company), 0.05)  # 既定は 5%
    TOOL_LOG.append(
        f"get_discount_rate が返した book_id = {book_id}, company = {company}, "
        f"discount_rate = {rate:.0%}"
    )
    discount_info = {"book_id": book_id, "company": company, "discount_rate": rate}
    # 最終提示をコードで組み立てるため、確定データを保持しておく。
    FACTS["discount"] = discount_info
    return discount_info


# ---------------------------------------------------------------------------
# 全エージェント・全ツールで共有したい「裏方の状態」。
#   使用言語も会社名もプロンプトには書かず、この dict だけで共有する。
# ---------------------------------------------------------------------------
shared_state = {
    "lang": "Japanese",      # ユーザーの使用言語（Agent#1 が参照）
    "company": "Acme Corp",  # ユーザーの会社名（Agent#2 が参照）
    "debug_mode": True,      # True の間はツールがデバッグログを出す想定（拡張用）
}

# shared_state = {
#     "lang": "English",      # ユーザーの使用言語（Agent#1 が参照）
#     "company": "Globex",  # ユーザーの会社名（Agent#2 が参照）
#     "debug_mode": True,      # True の間はツールがデバッグログを出す想定（拡張用）
# }

def format_final_answer() -> str:
    """
    ツールが返した確定データ（FACTS）から最終提示文を組み立てる。

    最終文を LLM に作文させると、タイトルや金額が言い換え（幻覚）で変わることがある。
    そこで「LLM に推論させる部分（どのツールをどう呼ぶか）」と「値を確定的に扱う部分
    （最終的な提示文）」を分け、提示文はツールの戻り値からコードで機械的に組み立てる。
    """
    book = FACTS.get("book")
    discount = FACTS.get("discount")
    if not book or not discount:
        return "（確定データが不足しているため、提示文を組み立てられませんでした）"

    title = book["title"]
    price = book["price"]
    currency = book["currency"]
    rate = discount["discount_rate"]
    # 割引後価格。通貨が JPY のときは整数（円）に丸める。
    discounted = price * (1 - rate)
    if currency == "JPY":
        price_str = f"{int(price):,} 円"
        discounted_str = f"{int(round(discounted)):,} 円"
    else:
        price_str = f"{price:.2f} {currency}"
        discounted_str = f"{discounted:.2f} {currency}"

    return (
        f"『{title}』（著者: {book['author']}）\n"
        f"  定価: {price_str}\n"
        f"  割引率: {rate:.0%}（{discount['company']} 向け）\n"
        f"  割引後価格: {discounted_str}"
    )


def build_graph():
    """
    Graph: book_manager → discount_manager。
    book_manager が選んだ書籍情報（book_id を含む）が discount_manager へ自動伝播し、
    discount_manager がその book_id と共有ステートの会社名から割引率を提示する。
    """
    book_manager = Agent(
        name="book_manager",
        model=model,
        tools=[get_user_language, get_book_info],
        system_prompt=(
            "あなたは書籍情報管理エージェントです。次の手順で処理してください。"
            "(1) get_user_language ツールでユーザーの使用言語を取得する。"
            "(2) get_book_info ツールに『依頼された書籍名』と『(1)の使用言語』を渡して書籍情報を取得する。"
            "(3) 取得した book_id・title・author・price（定価）・currency（通貨）を、"
            "後段の担当者にわかるように明記して報告する。"
            "ツールが返した値だけを使い、推測で内容を変えたり補ったりしないでください。"
        ),
        callback_handler=None,
    )
    discount_manager = Agent(
        name="discount_manager",
        model=model,
        tools=[get_company_name, get_discount_rate],
        system_prompt=(
            "あなたはディスカウント管理エージェントです。次の手順で処理してください。"
            "(1) get_company_name ツールで顧客の会社名を取得する。"
            "(2) get_discount_rate ツールに『前段から渡された book_id』と『(1)の会社名』を渡して割引率を取得する。"
            "(3) 取得できたことを一言だけ報告する（最終的な提示文はシステム側が組み立てるため、"
            "書籍名や金額をあなたが作文する必要はありません）。"
        ),
        callback_handler=None,
    )

    builder = GraphBuilder()
    builder.add_node(book_manager, "book_manager")
    builder.add_node(discount_manager, "discount_manager")
    # book_manager の出力（書籍情報・book_id）が discount_manager へ自動伝播する
    builder.add_edge("book_manager", "discount_manager")
    return builder.build()


if __name__ == "__main__":
    # 書籍名の情報提示をリクエストするだけ。使用言語・会社名はプロンプトに書かず、
    # invocation_state=shared_state で裏側から共有する。
    print("========== Graph 版: 書籍情報＋割引率の提示（invocation_state 共有）==========")
    graph = build_graph()
    graph_result = graph(
        "『ドメイン駆動設計』という書籍の情報を提示してください。",
        invocation_state=shared_state,
    )
    print("\n--- 実行順序 ---")
    print([node.node_id for node in graph_result.execution_order])

    # 最終提示はツールの確定データからコードで組み立てる（LLM に作文させない）。
    # これでタイトルや金額が言い換え（幻覚）で変わることがなくなる。
    print("\n--- 最終回答（確定データからコードで組み立て）---")
    print(format_final_answer())

    # 参考: LLM（discount_manager）自身の生成文。幻覚が混じり得るため参考扱い。
    print("\n--- 参考: discount_manager ノードの生成文 ---")
    print(graph_result.results["discount_manager"].result)

    print("\n--- 検証: ツールが invocation_state から実際に読み取った値／返した値 ---")
    for line in TOOL_LOG:
        print(f"  * {line}")
