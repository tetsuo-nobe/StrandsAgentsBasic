"""
tool/03_mcp_tool.py
MCP (Model Context Protocol) サーバーのツールを使用するサンプル。
事前に uvx がインストールされている必要があります。
"""

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# stdio トランスポートで MCP クライアントを作成
# この例では AWS ドキュメント MCP サーバーを使用
mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"],
        )
    )
)

# MCPClient を直接 tools に渡す方法（ライフサイクル自動管理）
agent = Agent(tools=[mcp_client])
result = agent("Amazon Bedrock とは何ですか？日本語で簡潔に説明してください。")

# --- 別の方法: コンテキストマネージャで明示的に管理 ---
# with mcp_client:
#     tools = mcp_client.list_tools_sync()
#     agent = Agent(tools=tools)
#     result = agent("Amazon Bedrock とは何ですか？")
