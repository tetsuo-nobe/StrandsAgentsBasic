# Strands Agents SDK サンプル集

[Strands Agents SDK](https://strandsagents.com/) (Python) の基本的な使い方を学ぶためのサンプルコード集です。

## 前提条件

- Python 3.10 以上
- AWS 認証情報が設定済みであること（Amazon Bedrock へのアクセス権限）
- Bedrock で使用するモデル（Claude 等）のモデルアクセスが有効化済みであること

## セットアップ

```bash
# 仮想環境の作成と有効化
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate.bat     # Windows (CMD)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)

# パッケージのインストール
pip install -r requirements.txt
```

## サンプル実行方法

各サンプルは単体で実行できます。

```bash
python -u <フォルダ名>/<ファイル名>.py
```

## フォルダ構成

```
.
├── requirements.txt
├── README.md
├── basic/                  # 基本的なエージェント作成
├── tool/                   # ツールの活用
├── stream/                 # ストリーミング出力
├── session/                # セッション（会話履歴）管理
└── observability/          # ログ・メトリクス取得
```

## サンプル一覧

### basic/ — 基本

| ファイル | 内容 |
|---|---|
| `01_simple_agent.py` | Agent オブジェクトだけを使う最低限のコード。デフォルトの Bedrock モデルで動作 |
| `02_bedrock_model_config.py` | BedrockModel でモデル ID・リージョン・推論パラメータ（temperature, max_tokens 等）を明示的に指定 |

### tool/ — ツール活用

| ファイル | 内容 |
|---|---|
| `01_builtin_tools.py` | `strands_tools` の `calculator`, `current_time` をツールとして使用 |
| `02_custom_tool.py` | `@tool` デコレータで自作の Python 関数をツールとして定義・使用 |
| `03_mcp_tool.py` | MCP サーバー（stdio トランスポート / ローカルプロセス）をツールとして使用。`uvx` が必要 |
| `04_remote_mcp_tool.py` | リモート MCP サーバー（Streamable HTTP）をツールとして使用。Svelte 公式 MCP サーバーに接続 |

### stream/ — ストリーミング

| ファイル | 内容 |
|---|---|
| `01_callback_handler.py` | `callback_handler` でテキスト生成・ツール使用イベントをリアルタイム処理 |
| `02_async_stream.py` | `stream_async` による非同期ストリーミング。FastAPI 等との統合に適した方式 |

### session/ — セッション管理

| ファイル | 内容 |
|---|---|
| `01_conversation_session.py` | 同一 Agent インスタンスを使い回すことで会話履歴を保持。`agent.messages` で履歴を確認 |

### observability/ — 可観測性

| ファイル | 内容 |
|---|---|
| `01_debug_logging.py` | `logging` モジュールで Strands のデバッグログを有効化し、内部動作やメトリクスを確認 |

## 参考リンク

- [Strands Agents SDK ドキュメント](https://strandsagents.com/)
- [Strands Agents SDK (GitHub)](https://github.com/strands-agents/sdk-python)
- [strands-agents (PyPI)](https://pypi.org/project/strands-agents/)
- [strands-agents-tools (GitHub)](https://github.com/strands-agents/tools)
