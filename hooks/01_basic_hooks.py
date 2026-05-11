"""
hooks/01_basic_hooks.py
Hooks（ライフサイクルイベント）の基本的な使い方のサンプル。
関数をフックとして登録し、エージェントの各ライフサイクルイベントを監視します。

v1.39.0 以降では、hooks パラメータに関数（callable）を直接渡せます。
関数の型ヒントでどのイベントに反応するかが自動判定されます。
"""

from strands import Agent, tool
from strands.hooks.events import (
    BeforeInvocationEvent,
    AfterInvocationEvent,
    BeforeModelCallEvent,
    AfterModelCallEvent,
    BeforeToolCallEvent,
    AfterToolCallEvent,
)


# --- フック関数の定義 ---
# 型ヒントでどのイベントに反応するかを指定します。
# Agent の hooks パラメータに直接渡すだけで登録完了です。


def on_before_invocation(event: BeforeInvocationEvent):
    """エージェント呼び出し開始時に実行されるフック"""
    print("\n🚀 [Hook] エージェント呼び出し開始")


def on_after_invocation(event: AfterInvocationEvent):
    """エージェント呼び出し完了時に実行されるフック"""
    if event.result:
        print(f"\n✅ [Hook] エージェント呼び出し完了 (停止理由: {event.result.stop_reason})")
    else:
        print("\n✅ [Hook] エージェント呼び出し完了")


def on_before_model_call(event: BeforeModelCallEvent):
    """モデル呼び出し前に実行されるフック"""
    print("\n🧠 [Hook] モデル呼び出し開始...")


def on_after_model_call(event: AfterModelCallEvent):
    """モデル呼び出し後に実行されるフック"""
    if event.stop_response:
        print(f"\n🧠 [Hook] モデル呼び出し完了 (停止理由: {event.stop_response.stop_reason})")
    elif event.exception:
        print(f"\n❌ [Hook] モデル呼び出し失敗: {event.exception}")


def on_before_tool_call(event: BeforeToolCallEvent):
    """ツール呼び出し前に実行されるフック"""
    tool_name = event.tool_use.get("name", "不明")
    print(f"\n🔧 [Hook] ツール呼び出し開始: {tool_name}")


def on_after_tool_call(event: AfterToolCallEvent):
    """ツール呼び出し後に実行されるフック"""
    tool_name = event.tool_use.get("name", "不明")
    print(f"\n🔧 [Hook] ツール呼び出し完了: {tool_name}")


# --- カスタムツールの定義 ---


@tool
def add_numbers(a: int, b: int) -> int:
    """
    2つの数値を足し算する。

    Args:
        a: 1つ目の数値
        b: 2つ目の数値

    Returns:
        int: 足し算の結果
    """
    return a + b


# --- エージェント作成 ---
# hooks パラメータにフック関数のリストを直接渡す（v1.39.0+）
agent = Agent(
    tools=[add_numbers],
    hooks=[
        on_before_invocation,
        on_after_invocation,
        on_before_model_call,
        on_after_model_call,
        on_before_tool_call,
        on_after_tool_call,
    ],
    system_prompt="あなたは計算が得意なアシスタントです。ツールを使って計算してください。",
)

# エージェントを実行
print("=" * 60)
print("Hooks（ライフサイクルイベント）の基本サンプル")
print("=" * 60)

result = agent("3 + 7 を計算してください。")

print("\n" + "=" * 60)
print(f"最終結果: {result.message}")
print("=" * 60)
