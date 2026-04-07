"""
observability/01_debug_logging.py
詳細ログ（デバッグログ）を取得するサンプル。
Strands の内部動作（モデル呼び出し、ツール実行など）を確認できます。
"""

import logging
from strands import Agent

# --- Strands のデバッグログを有効化 ---
logging.getLogger("strands").setLevel(logging.DEBUG)

# ログフォーマットを設定し、stderr に出力
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
)

agent = Agent()

print("=" * 50)
print("デバッグログ付きでエージェントを実行します")
print("=" * 50)

result = agent("1+1は？")

# --- 結果のメトリクス確認 ---
print("\n" + "=" * 50)
print("【実行メトリクス】")
print("=" * 50)
print(f"停止理由: {result.stop_reason}")
if hasattr(result, "metrics") and result.metrics:
    print(f"メトリクス: {result.metrics}")
