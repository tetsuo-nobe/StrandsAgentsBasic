
## Strands Agents のエージェントを AgentCore ランタイムへデプロイ

> [!NOTE]
> このリポジトリのテーマとは少し違う内容ですが、Agentic AI Foundations トレーニングで Strands Agents SDK のワークに続いて実施する想定なので、このリポジトリに含めています。

* インストラクターのガイドに基づき、マネジメントコンソールにサインインします。

* **注意:** 手順上、US のリージョンを使用します。マネジメントコンソールで **オレゴン (us-west-2) リージョン** を選択します。

### CloudShell の起動


* ページ左下の CloudShell のアイコンをクリックして起動します。

* 以後、CloudShell のターミナルにコマンドを貼り付けて実行していきます。

### Git リポジトリのクローン（もしまだの場合）

```
git clone https://github.com/tetsuo-nobe/StrandsAgentsBasic.git
```

### フォルダの移動

```
cd  ~/StrandsAgentsBasic/agentcore
```

### AgentCore CLI のインストール

> [!NOTE]
> CloudShell では容量が限られているためインストール先やキャッシュにあえて /tmp を指定しています。 

```
npm install -g @aws/agentcore@latest --prefix /tmp/npm-global --cache /tmp/npm-cache
export PATH=/tmp/npm-global/bin:$PATH
```

### AgentCore プロジェクトの作成

```
agentcore create
```

* 対話的モードで下記を選択
    - Project name: `handson`
    - What would you like to build?: `Agent` 
    - Agent name: `MyAgent` (デフォルト)
    - Select agent type: `Create new agent` 
    - Language: `Python` 
    - Build: `Direct Code Deploy`
    - Protocol: `HTTP`
    - Framework: `Strands Agents SDK`
    - Model: `us.anthropic.claude-sonnet-4-5-20250514-v1:0`
    - Memory: `None`
    - Customiza advanced settings: (何も選択せず Enter)
    - 最後にもう一度 Enter


```
cd handson
```

### main.py の編集

* GitHub リポジトリで main.py の内容を確認します。
    - trands Agents SDK のエージェントを AgentCore のエンドポイントとして指定した関数から呼び出すコードです。

* AgentCore プロジェクトで作成された main.py に上書きコピーします。

```
cp ~/StrandsAgentsBasic/agentcore/main.py  ~/StrandsAgentsBasic/agentcore/handson/app/MyAgent/main.py
```


### AgentCore ラインタイムへのデプロイ

```
agentcore deploy
```

### AgentCore ラインタイムの ARN の取得

```
agentcore status
```

下記のような出力の中で ARN の値をメモしておきます。

```
Agents
  MyAgent: Deployed - Runtime: READY (arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/handson_MyAgent-suHGqe9XiS)
  URL: https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A123456789012%3Aruntime%2Fhandson_MyAgent-suHGqe9XiS/invocations
```
 

### デプロイしたエージェントの呼び出し

```
uv init --python 3.14
uv add "boto3[crt]==1.42.96
```

* handson フォルダにいることを確認して下さい。

```
pwd
```

* エージェントを呼び出すコード (invoke.py) の用意

```
cp ../invoke.py  ./invoke.py
```

* invoke.py の編集

```
ARN=メモしたARN
```

```
sed -i "s|YOUR_AGENT_RUNTIME_ARN|$ARN|g" invoke.py
```

* 呼び出し実行

```
uv run invoke.py
```

* エージェントから回答が返ってくることを確認します。
