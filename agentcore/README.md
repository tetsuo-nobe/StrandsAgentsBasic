
## Strands Agents のエージェントを AgentCore ランタイムへデプロイ

> [!NOTE]
> このリポジトリのテーマとは少し違う内容ですが、Agentic AI Foundations トレーニングで Strands Agents SDK のワークに続いて実施する想定なので、このリポジトリに含めています。

* インストラクターのガイドに基づき、マネジメントコンソールにサインインします。

* **注意:** 手順上、US のリージョンを使用します。マネジメントコンソールで **オレゴン (us-west-2) リージョン** を選択します。

---
### 1. CloudShell の起動


* ページ左下の CloudShell のアイコンをクリックして起動します。

* 以後、CloudShell のターミナルにコマンドを貼り付けて実行していきます。

---
### 2. uv のインストール

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---
### 3. Git リポジトリのクローン（もしまだの場合）

```
git clone https://github.com/tetsuo-nobe/StrandsAgentsBasic.git
```

* フォルダの移動

```
cd  ~/StrandsAgentsBasic/agentcore
```

---
### 4. AgentCore CLI のインストール

> [!NOTE]
> CloudShell では容量が限られているためインストール先やキャッシュにあえて /tmp を指定しています。 またインストール後に不要なファイルを削除します。
 
```
npm install -g @aws/agentcore@latest --prefix /tmp/npm-global --cache /tmp/npm-cache
export PATH=/tmp/npm-global/bin:$PATH
```

```
rm -rf ~/.npm ~/.cache /tmp/npm-cache
```

---
### 5. AgentCore プロジェクトの作成

```
agentcore create
```

* 対話モードで下記を選択
    - Project name: `handson` を **入力**
    - What would you like to build?: `Agent` を選択 
    - Agent name: `MyAgent` (デフォルト) を選択
    - Select agent type: `Create new agent` を選択
    - Language: `Python` を選択
    - Build: `Direct Code Deploy` を選択
    - Protocol: `HTTP` を選択
    - Framework: `Strands Agents SDK` を選択
    - Model: `Amazon Bedrock (us.anthropic.claude-sonnet-4-5-20250514-v1:0)` を選択
    - Memory: `None` を選択
    - Customiza advanced settings: (何も選択せず Enter)
    - 最後にもう一度 Enter


```
cd handson
```

---
### 6. main.py の編集

* GitHub リポジトリで main.py の内容を確認します。
    - trands Agents SDK のエージェントを AgentCore のエンドポイントとして指定した関数から呼び出すコードです。

* AgentCore プロジェクトで作成された main.py に上書きコピーします。

```
cp ~/StrandsAgentsBasic/agentcore/main.py  ~/StrandsAgentsBasic/agentcore/handson/app/MyAgent/main.py
```
---

### 7. AgentCore ラインタイムへのデプロイ

* handson フォルダにいることを確認します。

```
pwd
```

* agentcore deploy コマンドでデプロイを実行します。

```
agentcore deploy
```

> [!NOTE]
> 途中、CDK の bootstrap 実行の確認が求められたら、Enter キーを押してください。

---

### 8. AgentCore ラインタイムの ARN の取得

```
agentcore status
```

下記のような出力の中で ARN の値をメモしておきます。

```
Agents
  MyAgent: Deployed - Runtime: READY (arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/handson_MyAgent-suHGqe9XiS)
  URL: https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A123456789012%3Aruntime%2Fhandson_MyAgent-suHGqe9XiS/invocations
```

---
### 9. (オプション）マネジメントコンソールでの確認

* マネジメントコンソールの検索で `agentcore` を入力して、AgentCore のページを表示します。
* 左側のナビゲーションメニューで [**構築**] - [**ランタイム**] をクリックします。
* [**ランタイムリソース**] に [**handson_MyAgent**] が表示され、[**ステータス**] が [**準備完了**] になっていることを確認します。

<img width="1417" height="809" alt="image" src="https://github.com/user-attachments/assets/e70ec4c9-2e87-452b-af4e-3ab208ea14bd" />

 
---
### 10. デプロイしたエージェントの呼び出し


```
rm -rf ~/.npm ~/.cache /tmp/npm-cache
```


```
uv init --python 3.14
uv add "boto3[crt]==1.42.96"
```

* handson フォルダにいることを確認して下さい。

```
pwd
```

* エージェントを呼び出すコード (invoke.py) の用意

```
cp ~/StrandsAgentsBasic/agentcore/invoke.py  ~/StrandsAgentsBasic/agentcore/handson/invoke.py
```

* invoke.py の編集

```
ARN=メモしたARN
```

```
sed -i "s|YOUR_AGENT_RUNTIME_ARN|$ARN|g" invoke.py
```

* ARN が正しく設定されていることを確認します。

```
cat invoke.py
```
 

* 呼び出し実行

```
uv run invoke.py
```

* エージェントから回答が返ってくることを確認します。(下記は例です。）

```
こんにちは！😊

お元気ですか？何かお手伝いできることはあります
```

---
## クリーンアップ手順

* 作成した AgentCore ランタイムの削除

```
agentcore remove
```

   - `Agent` を選択
   - `MyAgent` を選択
   - 確認の Enter キーを押す

```
agentcore deploy
```


* CDKTookit スタックの削除

```
aws cloudformation delete-stack --stack-name CDKToolkit
```

* CloudShell で作成したファイルの削除

```
cd ~
rm -rf ~/* ~/.[!.]* ~/..?*
```

* CloudShell を閉じ、マネジメントコンソールからサインアウトします。

---

### お疲れさまでした！ 
#### AgentCore CLI を使用し、Strands Agents SDK で作成したエージェントを AgentCore ランタイムへデプロイして使用できることを確認しました。




