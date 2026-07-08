"""
basic/05_callback_handler_none.py
callback_handler の有無によるストリーム出力の違いを確認するサンプル。
デフォルトではトークンが生成されるたびにリアルタイムで出力されます（ストリーム出力）。
callback_handler=None を指定すると、ストリーム出力が無効になります。
"""

from strands import Agent

# 長い回答を引き出すプロンプト
prompt = "Pythonの主要なデータ型を5つ挙げて、それぞれ簡単なコード例付きで説明してください。"

# --- 1. callback_handler 指定なし（デフォルト: ストリーム出力あり）---
print("=" * 60)
print("【1】callback_handler 指定なし（ストリーム出力あり）")
print("=" * 60)

agent_with_stream = Agent()
result1 = agent_with_stream(prompt)

print(f"\n\n--- 停止理由: {result1.stop_reason} ---")

# --- 2. callback_handler=None（ストリーム出力なし）---
print("\n")
print("=" * 60)
print("【2】callback_handler=None（ストリーム出力なし）")
print("=" * 60)

agent_no_stream = Agent(callback_handler=None)
result2 = agent_no_stream(prompt)

# ストリーム出力がないため、結果は result.message からまとめて取得する
print(result2.message["content"][0]["text"])
print(f"\n--- 停止理由: {result2.stop_reason} ---")
