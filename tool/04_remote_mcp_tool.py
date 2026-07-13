"""
tool/04_remote_mcp_tool.py
リモートの MCP サーバー（Streamable HTTP）をツールとして使用するサンプル。

03_mcp_tool.py が stdio トランスポート（ローカルプロセス起動）を使うのに対し、
このサンプルでは HTTP 経由でリモートの MCP サーバーに接続します。

接続先: https://knowledge-mcp.global.api.aws
  - AWS Knowledge MCP Server（認証不要・レート制限あり）
  - AWS ドキュメント検索、リージョン情報、CDK/CloudFormation ガイダンス等を提供
  - 参考: https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server
"""

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

# Streamable HTTP トランスポートで AWS Knowledge MCP Server に接続
remote_mcp_client = MCPClient(
    lambda: streamablehttp_client("https://knowledge-mcp.global.api.aws")
)

# MCPClient を直接 tools に渡す（ライフサイクル自動管理・推奨）
agent = Agent(
    tools=[remote_mcp_client],
    system_prompt="あなたは AWS に詳しいアシスタントです。日本語で回答してください。",
)

result = agent("Amazon Bedrock の概要と主な機能を簡潔に教えてください。")

# --- 別の方法: コンテキストマネージャで明示的に管理 ---
# with remote_mcp_client:
#     tools = remote_mcp_client.list_tools_sync()
#     print(f"利用可能なツール: {[t.tool_name for t in tools]}")
#
#     agent = Agent(tools=tools)
#     result = agent("Amazon Bedrock の概要と主な機能を簡潔に教えてください。")
