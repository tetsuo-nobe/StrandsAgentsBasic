# multiagent/ — マルチエージェントの3パターン

Strands Agents SDK で複数のエージェントを連携させる代表的な3パターン、**Workflow / Graph / Swarm** のサンプルです。

3つとも同じ題材（トピックについて「調査 → 分析 → まとめ」）を扱っています。**同じ仕事を3通りのやり方で実装する**ことで、パターンの違いがわかるようにしています。使用モデルはトレーニングで使用するハンズオン環境での実行を考慮し、すべて Amazon Nova Lite 1.0 v1（`us.amazon.nova-lite-v1:0`）にしていますが、必要に応じて変更してください。

参考: [Multi-agent Patterns（公式ドキュメント）](https://strandsagents.com/docs/user-guide/concepts/multi-agent/multi-agent-patterns/)

## 3 パターンの主な違い

最大の違いは **「実行の経路（次にどのエージェントが動くか）を誰が決めるか」** です。

| | Workflow | Graph | Swarm |
|---|---|---|---|
| 経路を決めるのは | **開発者**（コードで固定） | **開発者**（ノード＋エッジで定義） | **エージェント自身**（自律的にハンドオフ） |
| 中心概念 | 手続きコードによるチェーン | ノードとエッジの有向グラフ | 自律的に協調するチーム |
| 実行の性質 | 決定的・逐次 | 決定的（依存のないノードは並列） | 創発的・自律的 |
| 出力の受け渡し | 開発者が手で次へ渡す | SDK がエッジに沿って自動伝播 | 共有コンテキストを全員が参照 |
| ループ | なし | あり（条件付きエッジで可能） | あり |
| 実装の入口 | 素の `Agent` をコードで連結 | `GraphBuilder` | `Swarm` |

ざっくり言うと:

- **Workflow** … 「1→2→3 と順番に呼ぶ」のを自分でコードに書く。一番シンプルで挙動が読みやすい。
- **Graph** … ノード（エージェント）とエッジ（依存関係）を宣言する。依存のないノードは自動で並列実行される。
- **Swarm** … エージェントの集まりを渡すだけ。誰が次に動くかはエージェントが自分で判断する。

## SDK による提供のされ方の違い（重要）

3つのパターンは「どこまで SDK が用意してくれるか」が異なります。ここを理解しておくと、コードの読み方がはっきりします。

| パターン | 提供のされ方 | インポート元 |
|---|---|---|
| **Graph** | SDK 本体の**組み込みオーケストレーター**。実行制御・状態共有などを SDK が担う | `strands.multiagent`（`strands-agents`） |
| **Swarm** | SDK 本体の**組み込みオーケストレーター**。ハンドオフや共有コンテキストを SDK が担う | `strands.multiagent`（`strands-agents`） |
| **Workflow** | 専用のオーケストレーターは**なく、エージェントをコードで連結して実装する「設計パターン」**。別途、依存解決や並列実行を自動化する既製の `workflow` ツールが `strands_tools` にある | パターン自体は素の `strands` / ツールは `strands_tools`（`strands-agents-tools`） |

- **Graph・Swarm** は、公式ドキュメントでも "built-in SDK orchestrators"（SDK の組み込みオーケストレーター）と説明されており、`GraphBuilder` / `Swarm` を import すればフレームワークが実行の面倒を見てくれます。
- **Workflow** は、公式ドキュメントで "a pattern you implement in code by chaining agents together"（エージェントをコードで連結して実装するパターン）と位置づけられています。本フォルダの `01_workflow.py` も、専用クラスを使わず素の `Agent` を順番に呼ぶだけの実装です。
- なお `strands-agents-tools` の `workflow` ツールを使えば、タスクの依存解決・並列実行・状態管理を自動化できます（本サンプルでは、パターンの本質を理解しやすいよう、あえて素の `Agent` を連結する方式にしています）。

## サンプル一覧

| ファイル | パターン | 内容 |
|---|---|---|
| `01_workflow.py` | Workflow | `researcher → analyst → writer` をコードで順番に呼び出す。各出力を手動で次の入力に渡す |
| `02_graph.py` | Graph | `GraphBuilder` で利点調査・課題調査を**並列**実行し、`writer` ノードで合流。エッジで依存を定義 |
| `03_swarm.py` | Swarm | エージェントのプールを渡すだけ。`researcher → analyst → writer` のハンドオフ経路はエージェントが自律的に決める |

## 実行方法

リポジトリのルートで、セットアップ（`pip install -r requirements.txt`）を済ませてから実行します。

```bash
python -u multiagent/01_workflow.py
python -u multiagent/02_graph.py
python -u multiagent/03_swarm.py
```

## 使い分けの目安

- 分岐・条件・ループを含む「業務プロセス」を決定的に組みたい → **Graph**
- 専門性の異なる視点で探索・ブレスト・情報統合をさせたい（経路が事前に決められない）→ **Swarm**
- 繰り返し使える定型処理を、単純で読みやすいコードにまとめたい → **Workflow**

> 各パターンが SDK でどう提供されているか（Graph・Swarm は組み込み、Workflow は設計パターン）は、上の「SDK による提供のされ方の違い」を参照してください。
