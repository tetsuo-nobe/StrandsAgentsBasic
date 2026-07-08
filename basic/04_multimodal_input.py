"""
basic/04_multimodal_input.py
プロンプトに画像ファイルを添付してエージェントに送信するサンプル。
ContentBlock を使い、テキストと画像を組み合わせたマルチモーダル入力を行います。
"""

from pathlib import Path

from strands import Agent
# ContentBlock はテキスト・画像・ドキュメントなど、モデルに送る入力の1単位を表す型。
# 複数の ContentBlock をリストで渡すことで、マルチモーダルな入力を構成できる。
from strands.types.content import ContentBlock

# エージェントを作成
agent = Agent(
    system_prompt="あなたは画像分析アシスタントです。画像の内容を日本語で簡潔に説明してください。"
)

# --- 画像ファイルの読み込み ---
image_path = Path(__file__).parent / "cat.jpg"
image_bytes = image_path.read_bytes()

# --- マルチモーダル入力（テキスト + 画像）---
# ContentBlock を使い、テキストと画像を組み合わせてエージェントに送信
content_blocks = [
    ContentBlock(text="この画像に何が写っていますか？簡潔に説明してください。"),
    ContentBlock(image={"format": "jpeg", "source": {"bytes": image_bytes}}),
]

result = agent(content_blocks)

print("\n--- AgentResult ---")
print(f"停止理由: {result.stop_reason}")
print(f"メッセージ: {result.message}")
