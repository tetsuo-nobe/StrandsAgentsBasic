"""
conversation_management/01_sliding_window.py
会話履歴の管理戦略①：スライディングウィンドウ方式のサンプル。

会話が長くなると、履歴（messages）がモデルのコンテキストウィンドウ（トークン上限）
を超えてしまう。ConversationManager は、履歴が膨らんでもコンテキストを上限内に
保つために、古いメッセージを「自動的に」整理する仕組み（エージェントループ内で動く）。

SlidingWindowConversationManager（スライディングウィンドウ方式）:
- 直近のメッセージを「固定件数（window_size）」だけ残し、古いものから捨てる。
- Agent にマネージャを指定しない場合の「デフォルト」もこの方式。
- 捨てた古い内容は復元されない（＝要約方式との最大の違い。要約は 02 を参照）。

このサンプルで確認すること:
- window_size を小さく設定し、会話を重ねると古いメッセージが落ちていく様子。
- そのため「最初に伝えた名前」は、ウィンドウから押し出されると忘れられること。

セッション管理（session/）との違い:
- session/ … 会話履歴を「保持・永続化」して再起動後も復元する話。
- conversation_management/ … 履歴が「大きくなりすぎないよう上限内に抑える」話。
  両者は目的が異なり、組み合わせて使うこともできる。

参考: https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
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
        display_text = text[:60] + "..." if len(text) > 60 else text
        print(f"  [{i}] {role}: {display_text}")


# スライディングウィンドウ方式のマネージャを作成。
# window_size を小さく設定し、履歴がすぐ押し出される様子を観察する。
conversation_manager = SlidingWindowConversationManager(
    window_size=4,  # 保持する最大メッセージ件数（user/assistant 合わせて4件）
    should_truncate_results=True,  # 1件が大きすぎる場合にツール結果を切り詰める
)

agent = Agent(
    model=model,
    conversation_manager=conversation_manager,
    system_prompt="あなたは親切な日本語アシスタントです。簡潔に1〜2文で回答してください。",
    callback_handler=None,  # 途中のストリーム出力は抑制し、履歴の変化に注目する
)


if __name__ == "__main__":
    print("=" * 60)
    print("スライディングウィンドウ方式（SlidingWindowConversationManager）")
    print(f"  window_size = {conversation_manager.window_size}")
    print("=" * 60)

    # わざと多めに会話を重ねる。最初に名前を伝え、その後は無関係な話題を続ける。
    turns = [
        "私の名前は太郎です。覚えておいてください。",
        "日本の首都はどこですか？",
        "富士山の高さは何メートルですか？",
        "1 + 1 はいくつですか？",
        "私の名前を覚えていますか？",  # この頃には最初の発言はウィンドウ外の想定
    ]

    for n, text in enumerate(turns, start=1):
        print(f"\n{'-' * 50}")
        print(f"【ターン{n}】ユーザー: {text}")
        print(f"{'-' * 50}")
        result = agent(text)
        print(f"アシスタント: {result.message['content'][0]['text']}")
        print(f"\n現在の履歴件数: {len(agent.messages)} 件")
        show_messages(agent)

    print("\n" + "=" * 60)
    print("ポイント:")
    print("  window_size を超えた古いメッセージは自動的に捨てられるため、")
    print("  最初に伝えた『名前』はウィンドウから押し出されると忘れられる。")
    print("  （古い内容も残したい場合は、要約方式 02_summarizing.py を参照）")
    print("=" * 60)
