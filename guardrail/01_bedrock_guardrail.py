"""
guardrail/01_bedrock_guardrail.py
Amazon Bedrock Guardrails をエージェントに適用するサンプル。

Bedrock Guardrails を使うことで、エージェントの入出力に対して
トピック制限・有害コンテンツフィルタ・PII検出などのポリシーを適用できる。

このサンプルでは、観光名所案内エージェントに対して
「医療・健康に関するアドバイスを受け付けない」ガードレールを適用する。

事前準備:
  1. Amazon Bedrock コンソールまたは API でガードレールを作成する
     - トピックポリシーで「医療・健康アドバイス」を DENY に設定
  2. 環境変数を設定する:
     set GUARDRAIL_ID=your_guardrail_id   (ガードレールの ID)
     set GUARDRAIL_VERSION=DRAFT          (バージョン。省略時は DRAFT)
     set AWS_REGION=us-west-2             (リージョン)

必要なパッケージ:
  pip install strands-agents
"""

import os
import sys

from strands import Agent
from strands.models.bedrock import BedrockModel

# --- 設定 ---
MODEL_REGION = os.environ.get("AWS_REGION", "us-west-2")
GUARDRAIL_ID = os.environ.get("GUARDRAIL_ID")
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION", "DRAFT")

# ガードレール ID の確認
if not GUARDRAIL_ID:
    print("エラー: 環境変数 GUARDRAIL_ID が設定されていません。")
    print("  set GUARDRAIL_ID=your_guardrail_id  (Windows)")
    print("  export GUARDRAIL_ID=your_guardrail_id  (Linux/Mac)")
    sys.exit(1)

# BedrockModel にガードレール設定を組み込む
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name=MODEL_REGION,
    temperature=0.3,
    max_tokens=1024,
    # --- ガードレール設定 ---
    guardrail_id=GUARDRAIL_ID,
    guardrail_version=GUARDRAIL_VERSION,
    guardrail_trace="enabled",  # トレース有効化（デバッグ時に便利）
    guardrail_redact_input=True,
    guardrail_redact_input_message="[ガードレール] 医療・健康に関するご質問にはお答えできません。",
    guardrail_redact_output=True,
    guardrail_redact_output_message="[ガードレール] 医療・健康に関する内容は提供できません。",
)

# システムプロンプト
system_prompt = """
あなたは日本の観光名所を案内するアシスタント「旅ナビ」です。

ルール:
- 日本各地の観光スポット、名所、グルメ、アクセス方法などについて回答してください。
- おすすめの季節や見どころ、周辺情報なども積極的に紹介してください。
- 回答の冒頭に「旅ナビ:」と付けてください。
"""

# エージェントを作成
agent = Agent(
    model=bedrock_model,
    system_prompt=system_prompt,
)

# --- デモ実行 ---
print("=" * 60)
print("Bedrock Guardrails デモ（観光名所案内エージェント）")
print(f"  リージョン       : {MODEL_REGION}")
print(f"  ガードレール ID  : {GUARDRAIL_ID}")
print(f"  バージョン       : {GUARDRAIL_VERSION}")
print("=" * 60)

# テストケース: 通常の質問とブロックされる質問
test_questions = [
    "京都でおすすめの観光スポットを教えてください。",
    "旅行中に頭痛がひどいのですが、どんな薬を飲めばいいですか？",
]

for question in test_questions:
    print(f"\n{'─' * 40}")
    print(f"質問: {question}")
    print(f"{'─' * 40}")
    response = agent(question)
    # 会話履歴をリセット（各質問を独立して評価するため）
    agent.messages.clear()
