"""
tool/05_knowledge_base_retrieve.py
Amazon Bedrock ナレッジベースから情報を検索する RAG エージェントのサンプル。

事前準備:
  1. Amazon Bedrock でナレッジベースを作成し、S3 バケットのドキュメントと同期しておく
  2. 環境変数を設定する:
     set KNOWLEDGE_BASE_ID=XXXXXXXXXX     (ナレッジベースの ID)
     set AWS_REGION=us-west-2             (ナレッジベースのリージョン)

必要なパッケージ:
  pip install strands-agents strands-agents-tools
"""

import os
import sys

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import retrieve

# --- 設定 ---
# LLM モデルのリージョン（Bedrock のモデル呼び出し先）
MODEL_REGION = "us-west-2"
# ナレッジベースのリージョン（retrieve ツールが参照する先）
# retrieve ツールは環境変数 AWS_REGION を参照し、未設定時は us-west-2 をデフォルトとする
# ここで明示的に設定することで、ナレッジベースのリージョンを制御する
os.environ.setdefault("AWS_REGION", "us-west-2")
KB_REGION = os.environ["AWS_REGION"]

# ナレッジベース ID の確認
if not os.environ.get("KNOWLEDGE_BASE_ID"):
    print("エラー: 環境変数 KNOWLEDGE_BASE_ID が設定されていません。")
    print("  set KNOWLEDGE_BASE_ID=your_kb_id  (Windows)")
    print("  export KNOWLEDGE_BASE_ID=your_kb_id  (Linux/Mac)")
    sys.exit(1)

# Bedrock モデルの設定（LLM 呼び出し用のリージョンとモデルを明示的に指定）
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name=MODEL_REGION,
    temperature=0.3,
    max_tokens=2048,
)

# システムプロンプト: ナレッジベースの情報を活用して回答するよう指示
system_prompt = """
あなたはナレッジベースの情報を活用して質問に回答するアシスタントです。

ルール:
- ユーザーの質問に対して、AnyCompany社の社員の休暇規定に関する内容の場合はretrieve ツールを使ってナレッジベースから関連情報を検索してください。
- 検索結果に基づいて、正確で分かりやすい回答を日本語で提供してください。
- ナレッジベースに該当する情報がない場合は、その旨を正直に伝えてください。
- 回答の根拠となった情報源があれば、簡潔に言及してください。
- それ以外の質問の場合は、あなたがもつ一般的な知識に基づいて回答して下さい。
"""

# retrieve ツールを持つエージェントを作成（BedrockModel でリージョン・モデルを指定）
agent = Agent(
    model=bedrock_model,
    tools=[retrieve],
    system_prompt=system_prompt,
)

# 対話ループ
print("=" * 60)
print("Bedrock ナレッジベース検索エージェント")
print(f"  モデルリージョン     : {MODEL_REGION}")
print(f"  ナレッジベースリージョン: {KB_REGION}")
print(f"  ナレッジベース ID    : {os.environ['KNOWLEDGE_BASE_ID']}")
print("終了するには 'quit' または 'exit' と入力してください。")
print("=" * 60)

while True:
    try:
        question = input("\nあなた: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n終了します。")
        break

    if not question:
        continue
    if question.lower() in ("quit", "exit"):
        print("終了します。")
        break

    # エージェントに質問を投げる
    response = agent(question)
