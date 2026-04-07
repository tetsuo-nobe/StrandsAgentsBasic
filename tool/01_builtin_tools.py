"""
tool/01_builtin_tools.py
strands_tools の calculator, current_time を使うサンプル。
"""

from strands import Agent
from strands_tools import calculator, current_time

# ビルトインツールを渡してエージェントを作成
agent = Agent(
    tools=[calculator, current_time],
    system_prompt="あなたは計算と時刻の確認ができるアシスタントです。",
)

# 複数のツールを使う質問
result = agent(
    "今の時刻を教えてください。また、12345 × 6789 の計算結果も教えてください。"
)
