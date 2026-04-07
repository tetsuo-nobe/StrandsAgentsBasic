"""
basic/01_simple_agent.py
Agentオブジェクトだけを使う最低限のサンプル。
デフォルトではAmazon Bedrock の Claude モデルが使用されます。
"""

from strands import Agent

# 最もシンプルなエージェント作成
agent = Agent()

# エージェントに質問する
result = agent("日本の首都はどこですか？簡潔に答えてください。")

# 結果の確認
print("\n--- AgentResult ---")
print(f"停止理由: {result.stop_reason}")
print(f"メッセージ: {result.message}")
