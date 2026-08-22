"""
multiagent/02_graph.py
【Graph パターン】GraphBuilder でノード（エージェント）とエッジ（依存関係）を定義する構造化フロー。

特徴:
- 開発者がノードとエッジを事前に定義する（構造は固定）。
- 依存関係（エッジ）に従って実行され、依存のないノードは並列実行される。
- あるノードの出力が、つながった次のノードの入力として自動的に渡される。
- Workflow と違い「手動で出力を受け渡す」コードは不要。SDK が伝播を担う。

題材: 「調査（2観点を並列）→ まとめ」。
    positive（利点）と negative（課題）を並列で調査し、writer で合流してまとめる。

    positive ─┐
              ├─▶ writer
    negative ─┘
"""

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent import GraphBuilder

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)

# 役割の異なるエージェントを用意
positive = Agent(
    name="positive",
    model=model,
    system_prompt="あなたは利点の調査担当です。トピックの利点を箇条書きで2つ挙げてください。",
)
negative = Agent(
    name="negative",
    model=model,
    system_prompt="あなたは課題の調査担当です。トピックの課題を箇条書きで2つ挙げてください。",
)
writer = Agent(
    name="writer",
    model=model,
    system_prompt="あなたは執筆担当です。渡された利点と課題を踏まえ、3行以内の日本語でまとめてください。",
)

# グラフを構築
builder = GraphBuilder()
builder.add_node(positive, "positive")
builder.add_node(negative, "negative")
builder.add_node(writer, "writer")

# エッジ（依存関係）を定義。positive と negative は依存がないため並列実行される。
# 両者が完了してから writer が実行される。
builder.add_edge("positive", "writer")
builder.add_edge("negative", "writer")

graph = builder.build()

if __name__ == "__main__":
    # タスクは entry point（positive / negative）に渡され、出力が writer へ自動伝播する
    result = graph("観葉植物を室内に置くこと")

    print("\n--- 実行順序 ---")
    print([node.node_id for node in result.execution_order])

    print("\n--- 最終まとめ（writer ノードの出力）---")
    print(result.results["writer"].result)
