"""
tool/04_remote_mcp_tool.py
リモートの MCP サーバー（Streamable HTTP）をツールとして使用するサンプル。

03_mcp_tool.py が stdio トランスポート（ローカルプロセス起動）を使うのに対し、
このサンプルでは HTTP 経由でリモートの MCP サーバーに接続します。

接続先: https://mcp.svelte.dev/mcp
  - Svelte 公式の MCP サーバー（認証不要）
  - Svelte / SvelteKit のドキュメント検索などのツールを提供
"""

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

# Streamable HTTP トランスポートでリモート MCP サーバーに接続
remote_mcp_client = MCPClient(
    lambda: streamablehttp_client("https://mcp.svelte.dev/mcp")
)

# MCPClient を直接 tools に渡す（ライフサイクル自動管理・推奨）
agent = Agent(
    tools=[remote_mcp_client],
    system_prompt="あなたは Svelte に詳しいアシスタントです。日本語で回答してください。",
)

result = agent("SvelteKit のルーティングの仕組みを簡潔に教えてください。")

# --- 別の方法: コンテキストマネージャで明示的に管理 ---
# with remote_mcp_client:
#     tools = remote_mcp_client.list_tools_sync()
#     print(f"利用可能なツール: {[t.tool_name for t in tools]}")
#
#     agent = Agent(tools=tools)
#     result = agent("SvelteKit のルーティングの仕組みを簡潔に教えてください。")
