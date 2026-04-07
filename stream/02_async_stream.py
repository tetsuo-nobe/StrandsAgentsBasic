"""
stream/02_async_stream.py
stream_async を使った非同期ストリーミングのサンプル。
FastAPI などの非同期フレームワークとの統合に適しています。
"""

import asyncio
from strands import Agent
from strands_tools import calculator

# コールバックハンドラを無効化（stream_async で直接イベントを処理するため）
agent = Agent(
    tools=[calculator],
    callback_handler=None,
)


async def process_streaming_response():
    """非同期イテレータでストリーミングイベントを処理する"""
    prompt = "42 + 7 の計算結果と、フランスの首都を教えてください。"

    async for event in agent.stream_async(prompt):
        # イベントループのライフサイクル
        if event.get("init_event_loop"):
            print("🔄 イベントループ初期化")
        elif event.get("start_event_loop"):
            print("▶️  イベントループ開始")

        # テキスト出力
        if "data" in event:
            print(event["data"], end="", flush=True)

        # ツール使用
        if "current_tool_use" in event and event["current_tool_use"].get("name"):
            print(f"\n🔧 ツール使用: {event['current_tool_use']['name']}")

        # 完了
        if "result" in event:
            print("\n✅ エージェント完了")


# 非同期処理を実行
asyncio.run(process_streaming_response())
