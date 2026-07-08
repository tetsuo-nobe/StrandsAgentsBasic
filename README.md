# Strands Agents SDK サンプル集

[Strands Agents SDK](https://strandsagents.com/) (Python) の基本的な使い方を学ぶためのサンプルコード集です。

## 前提条件

- Python 3.10 以上
- Amazon Bedrock を使用するために必要なポリシーを許可されていること

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
├── hooks/                  # フック（ライフサイクルイベント）
├── guardrail/              # ガードレール（入出力制御）
├── stream/                 # ストリーミング出力
├── session/                # セッション（会話履歴）管理・永続化
└── observability/          # ログ・メトリクス取得
```

## サンプル一覧

### basic/ — 基本

| ファイル | 内容 |
|---|---|
| `01_simple_agent.py` | Agent オブジェクトだけを使う最低限のコード。デフォルトの Bedrock モデルで動作 |
| `02_bedrock_model_config.py` | BedrockModel でモデル ID（Amazon Nova Lite）・リージョン・推論パラメータ（temperature, max_tokens 等）を明示的に指定 |
| `03_system_prompt.py` | system_prompt でエージェントの役割・制約・回答スタイルを制御 |
| `04_multimodal_input.py` | ContentBlock を使い、テキストと画像ファイル（cat.jpg）を組み合わせたマルチモーダル入力 |
| `05_callback_handler_none.py` | callback_handler の有無によるストリーム出力の違いを確認。None 指定で出力を抑制 |

### tool/ — ツール活用

| ファイル | 内容 |
|---|---|
| `01_builtin_tools.py` | `strands_tools` の `calculator`, `current_time` をツールとして使用 |
| `02_custom_tool.py` | `@tool` デコレータで自作の Python 関数をツールとして定義・使用 |
| `03_mcp_tool.py` | MCP サーバー（stdio トランスポート / ローカルプロセス）をツールとして使用。`uvx` が必要 |
| `04_remote_mcp_tool.py` | リモート MCP サーバー（Streamable HTTP）をツールとして使用。Svelte 公式 MCP サーバーに接続 |
| `05_knowledge_base_retrieve.py` | Amazon Bedrock ナレッジベースから情報を検索する RAG エージェント。`retrieve` ツールを使用 |

### hooks/ — フック（ライフサイクルイベント）

| ファイル | 内容 |
|---|---|
| `01_basic_hooks.py` | 関数ベースのフックで各ライフサイクルイベント（呼び出し前後・モデル呼び出し前後・ツール呼び出し前後）を監視 |
| `02_hook_provider.py` | `HookProvider` プロトコルを実装したクラスベースのフック。状態を保持してメトリクスを収集 |
| `03_tool_guard_hook.py` | `cancel_tool` を使ったツール実行のガード。特定条件でツール呼び出しをキャンセルするパターン |

### guardrail/ — ガードレール

| ファイル | 内容 |
|---|---|
| `01_bedrock_guardrail.py` | Amazon Bedrock Guardrails をエージェントに適用。トピック制限（医療・健康アドバイスのブロック）のデモ |

### stream/ — ストリーミング

| ファイル | 内容 |
|---|---|
| `01_callback_handler.py` | `callback_handler` でテキスト生成・ツール使用イベントをリアルタイム処理 |
| `02_async_stream.py` | `stream_async` による非同期ストリーミング。FastAPI 等との統合に適した方式 |

### session/ — セッション管理

| ファイル | 内容 |
|---|---|
| `01_conversation_session.py` | 同一 Agent インスタンスを使い回すことで会話履歴を保持。`agent.messages` で履歴を確認 |
| `02_file_session_manager.py` | `FileSessionManager` で会話履歴をファイルに永続化。プログラム再起動後もセッションを復元 |

### observability/ — 可観測性

| ファイル | 内容 |
|---|---|
| `01_debug_logging.py` | `logging` モジュールで Strands のデバッグログを有効化し、内部動作やメトリクスを確認 |

## 参考リンク

- [Strands Agents SDK ドキュメント](https://strandsagents.com/)
- [Strands Agents SDK (GitHub)](https://github.com/strands-agents/sdk-python)
- [strands-agents (PyPI)](https://pypi.org/project/strands-agents/)
- [strands-agents-tools (GitHub)](https://github.com/strands-agents/tools)

---

## CloudShell で試す場合

1. インストラクターのガイドに基づき、AWS マネジメントコンソールを開きます。
1. **オレゴン (米国)**　リージョンを選択します。
1. ページ左下にある「CloudShell」のリンクをクリックします。
1. リポジトリをクローンして、移動します。
    ```
    git clone https://github.com/tetsuo-nobe/StrandsAgentsBasic.git
    ```

    ```
    cd StrandsAgentsBasic
    ```
    
1. 仮想環境を有効にして必要なパッケージをインストールします。
    
    ```bash
    # 仮想環境の作成と有効化
    python -m venv .venv
    source .venv/bin/activate     

    # パッケージのインストール
    pip install -r requirements.txt
    ```
1. GitHub のページをみて、実行するサンプルのコードを確認します。
1. CloudShell からサンプルを実行します。(下記は例)

    ```bash
    python -u basic/01_simple_agent.py
    ```

1. 仮想環境を終了する場合は、以下のコマンドを実行します。

    ```bash
    deactivate
    ```

1. 不要になったら、仮想環境とリポジトリを削除します。

    ```bash
    cd ~
    rm -rf StrandsAgentsBasic
    ```

1. CloudShell を閉じます。