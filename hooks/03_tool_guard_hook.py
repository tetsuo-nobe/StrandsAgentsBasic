"""
hooks/03_tool_guard_hook.py
BeforeToolCallEvent の cancel_tool を使ってツール呼び出しを制御するサンプル。
特定の条件でツール実行をキャンセル（ガード）する実用的なパターンです。

cancel_tool にメッセージを設定すると、ツール実行がキャンセルされ、
そのメッセージがエラーとしてモデルに返されます。
モデルはエラーメッセージを参考に別のアプローチを試みます。
"""

from strands import Agent, tool
from strands.hooks.events import BeforeToolCallEvent


# --- ガードフックの定義 ---


def tool_guard(event: BeforeToolCallEvent):
    """ツール呼び出し前にバリデーションを行うガードフック。

    cancel_tool にメッセージを設定すると、ツール実行がキャンセルされ、
    そのメッセージがエラーとしてモデルに返されます。
    """
    tool_name = event.tool_use.get("name", "")
    tool_input = event.tool_use.get("input", {})

    # delete_file ツールの呼び出しをブロック
    if tool_name == "delete_file":
        event.cancel_tool = "セキュリティポリシーにより、ファイル削除は禁止されています。"
        print(f"🚫 [Guard] ツール '{tool_name}' の実行をブロックしました")
        return

    # write_file ツールで禁止パスへの書き込みをブロック
    if tool_name == "write_file":
        path = tool_input.get("path", "")
        forbidden_paths = ["/etc/", "/system/", "C:\\Windows\\"]
        for forbidden in forbidden_paths:
            if path.startswith(forbidden):
                event.cancel_tool = (
                    f"セキュリティポリシーにより、'{forbidden}' 配下への書き込みは禁止されています。"
                )
                print(f"🚫 [Guard] パス '{path}' への書き込みをブロックしました")
                return

    print(f"✅ [Guard] ツール '{tool_name}' の実行を許可しました")


# --- カスタムツールの定義 ---


@tool
def write_file(path: str, content: str) -> str:
    """
    ファイルにテキストを書き込む（デモ用のダミー実装）。

    Args:
        path: 書き込み先のファイルパス
        content: 書き込む内容

    Returns:
        str: 結果メッセージ
    """
    # 実際には書き込まず、成功メッセージを返す（デモ用）
    return f"ファイル '{path}' に書き込みました（{len(content)}文字）"


@tool
def delete_file(path: str) -> str:
    """
    ファイルを削除する（デモ用のダミー実装）。

    Args:
        path: 削除するファイルパス

    Returns:
        str: 結果メッセージ
    """
    # 実際には削除しない（デモ用）
    return f"ファイル '{path}' を削除しました"


@tool
def read_file(path: str) -> str:
    """
    ファイルを読み込む（デモ用のダミー実装）。

    Args:
        path: 読み込むファイルパス

    Returns:
        str: ファイルの内容
    """
    return f"（デモ）ファイル '{path}' の内容: Hello, World!"


# --- エージェント作成 ---
# 関数を直接 hooks に渡す（v1.39.0+）
agent = Agent(
    tools=[write_file, delete_file, read_file],
    hooks=[tool_guard],
    system_prompt=(
        "あなたはファイル操作ができるアシスタントです。"
        "ツールを使ってファイルの読み書きや削除を行ってください。"
        "ツールがエラーを返した場合は、その理由をユーザーに説明してください。"
    ),
)

# エージェントを実行
print("=" * 60)
print("ツールガードフック（cancel_tool）サンプル")
print("=" * 60)

# テスト1: 許可される操作
print("\n--- テスト1: 許可される操作（ファイル読み込み）---")
result = agent("test.txt を読み込んでください。")
print(f"結果: {result.message}")

# テスト2: ブロックされる操作
print("\n--- テスト2: ブロックされる操作（ファイル削除）---")
result = agent("important.txt を削除してください。")
print(f"結果: {result.message}")
