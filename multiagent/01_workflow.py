"""
multiagent/01_workflow.py
【Workflow パターン】開発者がコードで実行順序を固定するシーケンシャルワークフロー。

特徴:
- 実行パスは開発者がコードで完全に固定する（決定的 / Deterministic）。
- 各エージェントの出力を、次のエージェントの入力として手動で受け渡す。
- LLM は「次にどこへ進むか」を判断しない。分岐もループもなし。

題材: あるトピックについて「調査 → 分析 → まとめ」を順番に処理する。
"""

from strands import Agent
from strands.models.bedrock import BedrockModel

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)

# 役割の異なる3つのエージェントを用意（出力抑制のため callback_handler=None）
researcher = Agent(
    model=model,
    system_prompt="あなたは調査担当です。トピックの重要な事実を箇条書きで3つ挙げてください。",
    callback_handler=None,
)
analyst = Agent(
    model=model,
    system_prompt="あなたは分析担当です。与えられた調査結果から、最も重要な示唆を1つ導いてください。",
    callback_handler=None,
)
writer = Agent(
    model=model,
    system_prompt="あなたは執筆担当です。与えられた分析を3行以内の日本語でまとめてください。",
    callback_handler=None,
)


def run_workflow(topic: str) -> str:
    """調査 → 分析 → まとめ を、コードで定めた順序どおりに実行する。"""
    # ステップ1: 調査
    research = researcher(f"次のトピックを調査してください: {topic}")
    print("\n--- ステップ1: 調査結果 ---")
    print(research)

    # ステップ2: 分析（ステップ1の出力を入力として渡す）
    analysis = analyst(f"次の調査結果を分析してください:\n{research}")
    print("\n--- ステップ2: 分析結果 ---")
    print(analysis)

    # ステップ3: まとめ（ステップ2の出力を入力として渡す）
    summary = writer(f"次の分析をまとめてください:\n{analysis}")
    print("\n--- ステップ3: 最終まとめ ---")
    print(summary)

    return str(summary)


if __name__ == "__main__":
    run_workflow("リモートワークが生産性に与える影響")
