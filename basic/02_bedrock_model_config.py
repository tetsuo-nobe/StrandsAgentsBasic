"""
basic/02_bedrock_model_config.py
Amazon Bedrock のモデルIDや推論パラメータを明示的に指定するサンプル。
"""

from strands import Agent
from strands.models.bedrock import BedrockModel

# BedrockModel でモデルIDと推論パラメータを明示的に指定
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-east-1",
    temperature=0.5,
    max_tokens=1024,
    top_p=0.9,
)

# モデル設定を確認
print(f"モデル設定: {bedrock_model.config}")

# システムプロンプト付きでエージェントを作成
agent = Agent(
    model=bedrock_model,
    system_prompt="あなたは親切な日本語アシスタントです。簡潔に回答してください。",
)

result = agent("Pythonの特徴を3つ教えてください。")
