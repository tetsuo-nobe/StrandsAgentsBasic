"""
structured_output/01_structured_output.py
構造化出力（Structured Output）のサンプル。

通常のエージェント呼び出し agent("...") は自由形式のテキストを返すが、
呼び出し時に structured_output_model=Model を渡すと、LLM の出力を
Pydantic モデルの型付きオブジェクトとして受け取れる。
（結果は AgentResult.structured_output フィールドに格納される）

メリット:
- 型安全: フィールドの型・必須/任意が保証され、後続コードで安心して使える。
- 幻覚（ハルシネーション）対策: 「どの項目を」「どの型で」返すかをスキーマで縛れる。
- 自由文のパース不要: 正規表現や文字列処理で値を抜き出す必要がない。

仕組み:
- Strands が Pydantic モデルから JSON スキーマを生成し、モデルに「このスキーマで
  出力せよ」と指示する（内部的にはツール呼び出しの仕組みを利用）。
- result.structured_output に、指定した Pydantic モデルのインスタンスが入るので、
  属性アクセスで値を扱える。バリデーションに失敗した場合は
  StructuredOutputException が送出される。

このサンプルの題材:
  問い合わせメールの本文から「氏名・会社名・問い合わせ種別・希望日・金額」を抽出し、
  型付きの InquiryTicket オブジェクトとして受け取る。

参考: https://strandsagents.com/docs/user-guide/concepts/agents/structured-output/
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from strands import Agent
from strands.models.bedrock import BedrockModel

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.2,
)


# ---------------------------------------------------------------------------
# 抽出先のスキーマ（Pydantic モデル）を定義する。
# Field の description は LLM への「この項目に何を入れるか」の指示にもなるため、
# 丁寧に書くほど抽出精度が上がる。
# ---------------------------------------------------------------------------
class InquiryType(str, Enum):
    """問い合わせ種別（列挙型で値を縛る）"""

    QUOTE = "見積もり"
    SUPPORT = "サポート"
    COMPLAINT = "クレーム"
    OTHER = "その他"


class InquiryTicket(BaseModel):
    """問い合わせ内容を構造化したチケット"""

    customer_name: str = Field(description="問い合わせ者の氏名")
    company_name: Optional[str] = Field(
        default=None, description="会社名。記載がなければ null"
    )
    inquiry_type: InquiryType = Field(description="問い合わせの種別")
    preferred_date: Optional[date] = Field(
        default=None, description="希望日（YYYY-MM-DD 形式）。記載がなければ null"
    )
    amount: Optional[int] = Field(
        default=None, description="金額（円、整数）。記載がなければ null"
    )
    summary: str = Field(description="問い合わせ内容の1文要約")


# エージェントを作成（構造化出力ではツールやシステムプロンプトは必須ではない）
agent = Agent(
    model=model,
    system_prompt="あなたは問い合わせメールから情報を正確に抽出するアシスタントです。",
    callback_handler=None,  # 内部のツール実行ログを抑制し、抽出結果の表示に集中する
)

# 抽出対象の問い合わせメール本文
inquiry_mail = """
株式会社サンプル商事の鈴木一郎と申します。
貴社の業務システム導入について、見積もりをお願いしたくご連絡しました。
予算は概ね300万円を想定しております。
打ち合わせは2026年11月20日を希望します。よろしくお願いいたします。
"""


if __name__ == "__main__":
    print("=" * 60)
    print("構造化出力（Structured Output）サンプル")
    print("=" * 60)
    print("\n--- 入力（問い合わせメール本文）---")
    print(inquiry_mail.strip())

    # 呼び出し時に structured_output_model を渡すと、結果の structured_output に
    # InquiryTicket のインスタンスが格納される。
    result = agent(
        f"次のメール本文から情報を抽出してください。\n\n{inquiry_mail}",
        structured_output_model=InquiryTicket,
    )
    ticket: InquiryTicket = result.structured_output

    # 以降は型付きオブジェクトとして安全に扱える（属性アクセス）。
    print("\n--- 抽出結果（型付き InquiryTicket オブジェクト）---")
    print(f"  氏名        : {ticket.customer_name}")
    print(f"  会社名      : {ticket.company_name}")
    print(f"  種別        : {ticket.inquiry_type.value}")
    print(f"  希望日      : {ticket.preferred_date}")
    print(f"  金額        : {ticket.amount} 円" if ticket.amount is not None else "  金額        : (記載なし)")
    print(f"  要約        : {ticket.summary}")

    # Pydantic の機能で JSON 文字列にも簡単に変換できる。
    print("\n--- JSON 形式（model_dump_json）---")
    print(ticket.model_dump_json(indent=2))

    # 型とバリデーションが効いていることの確認。
    print("\n--- 検証: 型情報 ---")
    print(f"  type(ticket)           = {type(ticket).__name__}")
    print(f"  type(ticket.amount)    = {type(ticket.amount).__name__}")
    print(f"  type(ticket.inquiry_type) = {type(ticket.inquiry_type).__name__}")
