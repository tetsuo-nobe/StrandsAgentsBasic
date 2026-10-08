"""
conversation_management/02_summarizing.py
会話履歴の管理戦略②：要約（Summarizing）方式のサンプル。

SlidingWindowConversationManager（01）は古いメッセージを「捨てる」ため、
押し出された情報は失われる。SummarizingConversationManager は、古いメッセージを
「捨てる」代わりに「LLM で要約して1件に置き換える」ことで、
トークン上限内に収めつつ、過去のやり取りの要点を文脈に残せる。

SummarizingConversationManager（要約方式）の主なパラメータ:
- summary_ratio（既定 0.3）: コンテキスト削減時に、古い方から何割を要約対象にするか
  （内部的に 0.1〜0.8 にクランプされる）。
- preserve_recent_messages（既定 10）: 直近の何件は常に要約せず残すか。
- summarization_agent（任意）: 要約生成に使う別エージェント。未指定なら本体と同じモデル。
- summarization_system_prompt（任意）: 要約用のシステムプロンプト。
  （summarization_agent と同時指定は不可）

このサンプルで確認すること:
- 会話を数ターン重ねたあとにコンテキスト削減を実行すると、古いメッセージが
  「要約メッセージ1件」に置き換わる様子。
- 01（スライディングウィンドウ）と異なり、最初に伝えた情報が要約として
  文脈に残り、削減後も参照できること。

削減が走るタイミングについて:
- 実運用では、履歴がモデルのコンテキスト上限を超えそうになったときに
  SDK が自動で削減（要約）を実行する。
- 本サンプルでは短い会話でも挙動を確実に見せるため、
  conversation_manager.reduce_context(agent) を明示的に呼んで要約を強制する。

注意:
- 要約は LLM 呼び出しを伴うため、削減が走るタイミングで追加のモデル実行が発生する。

参考: https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/
"""

from strands import Agent
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models.bedrock import BedrockModel

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)


def show_messages(agent: Agent):
    """エージェントの現在の会話履歴を表示する"""
    if not agent.messages:
        print("  （会話履歴なし）")
        return
    for i, msg in enumerate(agent.messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", str(content[0]))
        else:
            text = str(content)
        display_text = text[:70] + "..." if len(text) > 70 else text
        print(f"  [{i}] {role}: {display_text}")


# 要約方式のマネージャを作成。
# 挙動を観察しやすいよう、直近の保持件数を小さめに設定する。
conversation_manager = SummarizingConversationManager(
    summary_ratio=0.5,            # 削減時、古い方の50%を要約対象にする
    preserve_recent_messages=2,  # 直近2件は常に残す
    # summarization_system_prompt を省略すると、
    # 「要点を箇条書きで三人称でまとめる」既定プロンプトが使われる。
)

agent = Agent(
    model=model,
    conversation_manager=conversation_manager,
    system_prompt="あなたは親切な日本語アシスタントです。簡潔に1〜2文で回答してください。",
    callback_handler=None,  # 途中のストリーム出力は抑制し、履歴の変化に注目する
)


if __name__ == "__main__":
    print("=" * 60)
    print("要約方式（SummarizingConversationManager）")
    print(f"  summary_ratio            = {conversation_manager.summary_ratio}")
    print(f"  preserve_recent_messages = {conversation_manager.preserve_recent_messages}")
    print("=" * 60)

    # 最初に覚えてほしい情報を伝え、その後は別の話題を続ける。
    turns = [
        "私の名前は太郎で、好きな食べ物はカレーライスです。覚えておいてください。",
        "日本の首都はどこですか？",
        "富士山の高さは何メートルですか？",
        "日本で一番大きい湖は何ですか？",
    ]

    for n, text in enumerate(turns, start=1):
        print(f"\n{'-' * 50}")
        print(f"【ターン{n}】ユーザー: {text}")
        print(f"{'-' * 50}")
        result = agent(text)
        print(f"アシスタント: {result.message['content'][0]['text']}")

    print(f"\n■ 削減前の履歴（{len(agent.messages)} 件）")
    show_messages(agent)

    # --- コンテキスト削減（要約）を明示的に実行する ---
    # 実運用ではトークン上限が近づくと SDK が自動で呼ぶ処理。ここでは挙動を
    # 確実に見せるため手動で呼び出す。古い方のメッセージが要約1件に置き換わる。
    print("\n" + "*" * 50)
    print("コンテキスト削減（要約）を実行します…")
    print("*" * 50)
    conversation_manager.reduce_context(agent)

    print(f"\n■ 削減後の履歴（{len(agent.messages)} 件）")
    show_messages(agent)

    # --- 削減後も、最初に伝えた情報を覚えているか確認 ---
    print(f"\n{'-' * 50}")
    final_q = "私の名前と好きな食べ物を覚えていますか？"
    print(f"【確認】ユーザー: {final_q}")
    print(f"{'-' * 50}")
    result = agent(final_q)
    print(f"アシスタント: {result.message['content'][0]['text']}")

    print("\n" + "=" * 60)
    print("ポイント:")
    print("  コンテキスト削減が走ると、古いメッセージは『捨てられる』のではなく")
    print("  LLM による要約メッセージに置き換えられる（履歴の先頭が要約に変わる）。")
    print("  これにより、最初に伝えた名前や好みが要約として文脈に残り、")
    print("  削減後も参照できる。（要約生成のため追加の LLM 呼び出しが発生する）")
    print("=" * 60)
