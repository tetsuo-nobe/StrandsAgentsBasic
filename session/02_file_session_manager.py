"""
session/02_file_session_manager.py
FileSessionManager を使ったセッション永続化のサンプル。

FileSessionManager を使うと、会話履歴がローカルファイルシステムに保存され、
プログラムを再起動しても前回の会話を復元できます。

ファイル構造:
  /<storage_dir>/
  └── session_<session_id>/
      ├── session.json          # セッションメタデータ
      └── agents/
          └── agent_<agent_id>/
              ├── agent.json    # エージェントメタデータ
              └── messages/
                  ├── message_0.json
                  └── message_1.json ...
"""

import os
import shutil

from strands import Agent
from strands.session.file_session_manager import FileSessionManager

# --- 設定 ---
# セッションデータの保存先ディレクトリ
STORAGE_DIR = os.path.join(os.path.dirname(__file__), ".sessions")
SESSION_ID = "demo-session-001"
AGENT_ID = "assistant-001"


def create_agent_with_session(session_id: str, agent_id: str) -> Agent:
    """FileSessionManager 付きのエージェントを作成する。

    同じ session_id と agent_id を指定すれば、
    前回の会話履歴が自動的に復元されます。
    """
    session_manager = FileSessionManager(
        session_id=session_id,
        storage_dir=STORAGE_DIR,
    )

    agent = Agent(
        agent_id=agent_id,
        session_manager=session_manager,
        system_prompt="あなたは親切な日本語アシスタントです。ユーザーとの会話内容を覚えておいてください。",
    )
    return agent


def show_messages(agent: Agent):
    """エージェントの会話履歴を表示する"""
    if not agent.messages:
        print("  （会話履歴なし）")
        return
    for i, msg in enumerate(agent.messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", str(content[0]))
        else:
            text = str(content)
        display_text = text[:80] + "..." if len(text) > 80 else text
        print(f"  [{i}] {role}: {display_text}")


# --- デモ実行 ---
print("=" * 60)
print("FileSessionManager（セッション永続化）サンプル")
print(f"  保存先: {STORAGE_DIR}")
print(f"  セッション ID: {SESSION_ID}")
print(f"  エージェント ID: {AGENT_ID}")
print("=" * 60)

# クリーンな状態から始める（デモ用にセッションデータを削除）
if os.path.exists(STORAGE_DIR):
    shutil.rmtree(STORAGE_DIR)
    print("\n🗑️  前回のセッションデータを削除しました")

# --- 1回目のエージェント作成と会話 ---
print("\n" + "-" * 40)
print("【1回目】エージェント作成 → 会話")
print("-" * 40)

agent1 = create_agent_with_session(SESSION_ID, AGENT_ID)
agent1("私の好きな食べ物はカレーライスです。覚えておいてください。")

print("\n📝 現在の会話履歴:")
show_messages(agent1)

# --- エージェントを破棄（プログラム再起動をシミュレート）---
del agent1
print("\n🔄 エージェントを破棄しました（再起動をシミュレート）")

# --- 2回目のエージェント作成（セッション復元）---
print("\n" + "-" * 40)
print("【2回目】エージェント再作成 → セッション復元 → 会話")
print("-" * 40)

agent2 = create_agent_with_session(SESSION_ID, AGENT_ID)

print("\n📝 復元された会話履歴:")
show_messages(agent2)

# 前回の会話を覚えているか確認
print("\n💬 復元後に質問:")
agent2("私の好きな食べ物は何でしたか？")

print("\n📝 最終的な会話履歴:")
show_messages(agent2)

# --- 保存されたファイルの確認 ---
print("\n" + "-" * 40)
print("【保存されたファイル構造】")
print("-" * 40)
for root, dirs, files in os.walk(STORAGE_DIR):
    level = root.replace(STORAGE_DIR, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    sub_indent = "  " * (level + 1)
    for file in files:
        print(f"{sub_indent}{file}")

# クリーンアップ（デモ用）
shutil.rmtree(STORAGE_DIR)
print(f"\n🧹 デモ用セッションデータを削除しました: {STORAGE_DIR}")
