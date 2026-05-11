"""
hooks/02_hook_provider.py
HookProvider プロトコルを使ったクラスベースのフック実装サンプル。
複数のフックをクラスにまとめて管理し、状態を保持できます。
"""

from strands import Agent, tool
from strands.hooks.registry import HookProvider, HookRegistry
from strands.hooks.events import (
    BeforeInvocationEvent,
    AfterInvocationEvent,
    BeforeToolCallEvent,
    AfterToolCallEvent,
)
import time


class MetricsHookProvider(HookProvider):
    """エージェントの実行メトリクスを収集するフックプロバイダー。

    HookProvider プロトコルを実装することで、
    複数のフックをクラスにまとめて管理できます。
    クラスのインスタンス変数で状態を保持できるのが利点です。
    """

    def __init__(self):
        """メトリクス用の変数を初期化"""
        self.invocation_start_time: float = 0
        self.tool_call_count: int = 0
        self.tool_names: list[str] = []

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        """フックをレジストリに登録する。

        HookProvider プロトコルで必須のメソッド。
        registry.add_callback() でイベントとコールバックを紐付けます。
        """
        registry.add_callback(BeforeInvocationEvent, self._on_before_invocation)
        registry.add_callback(AfterInvocationEvent, self._on_after_invocation)
        registry.add_callback(BeforeToolCallEvent, self._on_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self._on_after_tool_call)

    def _on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """呼び出し開始時: タイマー開始"""
        self.invocation_start_time = time.time()
        self.tool_call_count = 0
        self.tool_names = []
        print("\n📊 [Metrics] 計測開始")

    def _on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """呼び出し完了時: メトリクスを表示"""
        elapsed = time.time() - self.invocation_start_time
        print("\n" + "=" * 50)
        print("📊 [Metrics] 実行メトリクス")
        print("=" * 50)
        print(f"  実行時間: {elapsed:.2f} 秒")
        print(f"  ツール呼び出し回数: {self.tool_call_count}")
        if self.tool_names:
            print(f"  使用ツール: {', '.join(self.tool_names)}")
        print("=" * 50)

    def _on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前: カウントとツール名を記録"""
        self.tool_call_count += 1
        tool_name = event.tool_use.get("name", "不明")
        self.tool_names.append(tool_name)

    def _on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール呼び出し後: 結果をログ出力"""
        tool_name = event.tool_use.get("name", "不明")
        if isinstance(event.result, Exception):
            print(f"  ❌ ツール '{tool_name}' がエラーで終了")
        else:
            print(f"  ✅ ツール '{tool_name}' が正常終了")


# --- カスタムツールの定義 ---


@tool
def multiply(a: int, b: int) -> int:
    """
    2つの数値を掛け算する。

    Args:
        a: 1つ目の数値
        b: 2つ目の数値

    Returns:
        int: 掛け算の結果
    """
    return a * b


@tool
def power(base: int, exponent: int) -> int:
    """
    べき乗を計算する。

    Args:
        base: 底
        exponent: 指数

    Returns:
        int: べき乗の結果
    """
    return base**exponent


# --- エージェント作成 ---
# HookProvider インスタンスを hooks パラメータに渡す
metrics_provider = MetricsHookProvider()

agent = Agent(
    tools=[multiply, power],
    hooks=[metrics_provider],
    system_prompt="あなたは計算が得意なアシスタントです。ツールを使って計算してください。",
)

# エージェントを実行
print("=" * 60)
print("HookProvider（クラスベースのフック）サンプル")
print("=" * 60)

result = agent("5の3乗を計算し、その結果に2を掛けてください。")

print(f"\n最終結果: {result.message}")
