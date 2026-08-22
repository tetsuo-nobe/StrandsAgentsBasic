"""
multiagent/03_swarm.py
【Swarm パターン】エージェントのチームが自律的にハンドオフしながら協調するパターン。

特徴:
- 開発者はエージェントの「集まり（プール）」を渡すだけ。エッジや順序は定義しない。
- 実行パスはエージェント自身が決める（創発的 / Emergent）。
- 各エージェントは共有コンテキスト（元の依頼・作業履歴・他エージェントの知見）を参照できる。
- 自分より適任がいると判断すると、handoff_to_agent ツールで制御を渡す。

題材: 「調査 → 分析 → まとめ」を、誰がいつ担当するかはエージェントが自律的に決める。
    Workflow / Graph が「開発者が経路を決める」のに対し、Swarm は「エージェントが経路を決める」。
"""

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent import Swarm

# 共通で使う Amazon Nova Lite モデル
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)

# 役割の異なるエージェントを用意。description は他エージェントが適任を選ぶ手がかりになる。
# callback_handler=None で各エージェントの途中経過（<thinking> やツール呼び出し）の
# ストリーム出力を抑制し、最終結果だけを表示できるようにする。
researcher = Agent(
    name="researcher",
    model=model,
    description="トピックの事実や情報を調査する担当",
    system_prompt=(
        "あなたは調査担当です。トピックの重要な事実を簡潔に挙げてください。"
        "調査が済んだら analyst にハンドオフしてください。"
    ),
    callback_handler=None,
)
analyst = Agent(
    name="analyst",
    model=model,
    description="調査結果から示唆を導く分析担当",
    system_prompt=(
        "あなたは分析担当です。調査結果から重要な示唆を1つに絞って導いてください。"
        "分析が済んだら writer にハンドオフしてください。"
    ),
    callback_handler=None,
)
writer = Agent(
    name="writer",
    model=model,
    description="最終的な文章をまとめる執筆担当",
    system_prompt=(
        "あなたは執筆担当です。これまでの内容を3行以内の日本語でまとめてください。"
        "あなたが最後の担当なので、他エージェントにハンドオフせず、まとめを出力して完了してください。"
    ),
    callback_handler=None,
)

# エージェントのプールを渡すだけ。順序やエッジは指定しない。
swarm = Swarm(
    [researcher, analyst, writer],
    entry_point=researcher,  # 最初に受け取るエージェント（省略時は先頭）
    max_handoffs=10,
    max_iterations=10,
)

if __name__ == "__main__":
    result = swarm("リモートワークが生産性に与える影響")

    print("\n--- ハンドオフの履歴（誰がどの順で担当したか）---")
    print([node.node_id for node in result.node_history])

    # result をそのまま print するとメトリクス等まで出て冗長になるため、
    # 最後に担当した writer の出力テキストだけを取り出して表示する。
    print("\n--- 最終まとめ（writer の出力）---")
    print(result.results["writer"].result)
