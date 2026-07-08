"""
basic/03_system_prompt.py
system_prompt を使ってエージェントの振る舞いを制御するサンプル。
system_prompt により、エージェントの役割・制約・回答スタイルを指定できます。
"""

from strands import Agent

# system_prompt でエージェントの役割と制約を定義
agent = Agent(
    system_prompt=(
        "あなたはプログラミング学習を支援する講師です。\n"
        "以下のルールに従ってください：\n"
        "- 初心者にもわかりやすい表現を使う\n"
        "- 回答は3行以内にまとめる\n"
        "- 必ず具体的なコード例を1つ含める"
    )
)

# system_prompt に従った回答が返される
result = agent("Pythonで変数を定義する方法を教えてください。")

print("\n--- AgentResult ---")
print(f"停止理由: {result.stop_reason}")
print(f"メッセージ: {result.message}")
