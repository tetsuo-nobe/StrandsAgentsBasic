"""
stream/01_callback_handler.py
コールバックハンドラを使ったストリーミング出力のサンプル。
テキスト生成やツール使用のイベントをリアルタイムで処理します。
"""

from strands import Agent
from strands_tools import calculator


def my_callback_handler(**kwargs):
    """カスタムコールバックハンドラ"""
    # テキストチャンクの出力
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)

    # ツール使用の検出
    if "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        if tool.get("name"):
            print(f"\n🔧 ツール使用: {tool['name']}")

    # 完了イベント
    if kwargs.get("complete"):
        print("\n✅ 応答完了")


# コールバックハンドラを指定してエージェントを作成
agent = Agent(
    tools=[calculator],
    callback_handler=my_callback_handler,
)

agent("100の階乗を計算してください。")
