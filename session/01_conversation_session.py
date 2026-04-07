"""
session/01_conversation_session.py
セッション管理のサンプル。
同一の Agent インスタンスを使い回すことで会話履歴が保持されます。
"""

from strands import Agent

# エージェントを作成（同一インスタンスで会話を継続）
agent = Agent(
    system_prompt="あなたは親切な日本語アシスタントです。",
)

# --- 1回目の会話 ---
print("=" * 50)
print("【1回目の質問】")
print("=" * 50)
agent("私の名前は太郎です。覚えておいてください。")

# --- 2回目の会話（前の会話を覚えている） ---
print("\n" + "=" * 50)
print("【2回目の質問】")
print("=" * 50)
agent("私の名前を覚えていますか？")

# --- 会話履歴の確認 ---
print("\n" + "=" * 50)
print("【会話履歴の確認】")
print("=" * 50)
for i, msg in enumerate(agent.messages):
    role = msg.get("role", "unknown")
    # テキストコンテンツを抽出
    content = msg.get("content", [])
    if isinstance(content, list) and len(content) > 0:
        text = content[0].get("text", str(content[0]))
    else:
        text = str(content)
    # 長いテキストは省略
    display_text = text[:80] + "..." if len(text) > 80 else text
    print(f"  [{i}] {role}: {display_text}")
