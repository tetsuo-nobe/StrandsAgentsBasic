
## Strands Agents のエージェントを AgentCore ランタイムへデプロイ

> [!NOTE]
> このリポジトリのテーマとは少し違う内容ですが、Agentic AI Foundations トレーニングで Strands Agents SDK のワークに続いて実施する想定なので、このリポジトリに含めています。

* インストラクターのガイドに基づき、マネジメントコンソールにサインインします。

* **注意:** 手順上、US のリージョンを使用します。マネジメントコンソールで **オレゴン (us-west-2) リージョン** を選択します。

---

## 手順

---
### 1. VPC とサブネットの情報を取得


1. ページ左下の CloudShell のアイコンをクリックして起動してホームディレクトリに移動します。

   ```
   cd ~
   ```

1. 下記のコマンドで、デフォルトの VPC の ID と Public サブネットの ID を表示します。

     ```
   export AWS_REGION=us-west-2
   
   # デフォルト VPC の ID を取得して環境変数へ
   export VPC_ID=$(aws ec2 describe-vpcs \
     --filters "Name=isDefault,Values=true" \
     --query "Vpcs[0].VpcId" --output text --region $AWS_REGION)
   
   # その VPC のパブリックサブネットを1つ取得して環境変数へ
   export SUBNET_ID=$(aws ec2 describe-subnets \
     --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" \
     --query "Subnets[0].SubnetId" --output text --region $AWS_REGION)
   
   echo "VPC_ID=$VPC_ID"
   echo "SUBNET_ID=$SUBNET_ID"
     ```


---
### 2. CloudFormation で コマンド実行用の EC2 インスタンスを作成

* 引き続き CloudShell を使用します。

1. 下記のコマンドで、CloudFormation スタックを作成します。

     ```
    aws cloudformation create-stack \
      --stack-name agentcore-ec2 \
      --template-url https://tnobep-work-public.s3.ap-northeast-1.amazonaws.com/agentcore_work/ec2-agentcore.yaml \
      --capabilities CAPABILITY_IAM \
      --parameters ParameterKey=VpcId,ParameterValue=$VPC_ID ParameterKey=SubnetId,ParameterValue=$SUBNET_ID \
      --region $AWS_REGION
     ```

1. 下記のような出力を確認します。

    ```
    {
        "StackId": "arn:aws:cloudformation:us-west-2:418295696229:stack/agentcore-ec2/bd5ade10-9a0c-11f1-9296-06611a0e8ebd",
        "OperationId": "bd5c64b0-9a0c-11f1-9296-06611a0e8ebd"
    }
    ```

1. CloudShell を閉じます。

1. CloudFormation のページを表示し、**agentcore-ec2** スタックのステータスが **CREATE_COMPLETE** になるまで待機します。

---
### 3. EC2 インスタンスにセッションマネージャーでアクセス

1. EC2 のページを表示します。

1. 左側のメニューから「**インスタンス**」- 「**インスタンス**」をクリックします。

1. **agentcore-workstation** というインスタンス名の左横のチェックボックスをチェックします。

1. 「**接続**」をクリックします。

1. 「**SSM セッションマネージャー**」をクリックして、「**接続**」をクリックします。

1. ターミナルが表示されることを確認します。

---
### 4. AgentCore CLI でエージェントのデプロイ

* 以後、SSM セッションマネージャーのターミナルにコマンドを貼り付けて実行していきます。

---
#### 4-1. uv のインストール

```
cd ~
```

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```
source $HOME/.local/bin/env
```

---
#### 4-2. Git リポジトリのクローン

```
git clone https://github.com/tetsuo-nobe/StrandsAgentsBasic.git
```

* フォルダの移動

```
cd  ~/StrandsAgentsBasic/agentcore
```

---
#### (オプション) 4-3. AgentCore CLI のインストール

* 通常は 下記のコマンドで AgentCore CLI をインストールしますが、このワークの環境では EC2 インスタンスのユーザーデータですでにインストール済です。

* 参考：AgentCore CLI のインストールコマンドは下記です。 **実行する必要はありません**

  ```
  npm install -g @aws/agentcore@latest 
   ```

---
#### 4-4. AgentCore プロジェクトの作成

```
aws configure set region us-west-2
```

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

* プロジェクト作成が完了するまで少し待ち、完了後に下記でプロジェクトフォルダに移動します。
  
```
cd handson
```

---
#### 4-5. main.py の編集

* GitHub リポジトリで main.py の内容を確認します。
    - Strands Agents SDK のエージェントを AgentCore のエンドポイントとして指定した関数から呼び出すコードです。

* AgentCore プロジェクトで作成された main.py に上書きコピーします。

```
cp ~/StrandsAgentsBasic/agentcore/main.py  ~/StrandsAgentsBasic/agentcore/handson/app/MyAgent/main.py
```
---

#### 4-6. AgentCore ラインタイムへのデプロイ

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

#### 4-7. AgentCore ラインタイムの ARN の取得

```
agentcore status
```

下記のような出力の中で ARN の値をメモしておきます。

```
Agents
  MyAgent: Deployed - Runtime: READY (arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/handson_MyAgent-suHGqe9XiS)
  URL: https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-west-2%3A123456789012%3Aruntime%2Fhandson_MyAgent-suHGqe9XiS/invocations
```

---
#### 4-8. (オプション）マネジメントコンソールでの確認

* マネジメントコンソールの検索で `agentcore` を入力して、AgentCore のページを表示します。
* 左側のナビゲーションメニューで [**構築**] - [**ランタイム**] をクリックします。
* [**ランタイムリソース**] に [**handson_MyAgent**] が表示され、[**ステータス**] が [**準備完了**] になっていることを確認します。

<img width="1417" height="809" alt="image" src="https://github.com/user-attachments/assets/e70ec4c9-2e87-452b-af4e-3ab208ea14bd" />

 
---
#### 4-9. デプロイしたエージェントの呼び出し


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
### クリーンアップ手順

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

   - 確認の Enter キーを押す

* CDKTookit スタックの削除

```
aws cloudformation delete-stack --stack-name CDKToolkit
```

* ファイルの削除

```
cd ~
rm -rf ~/* ~/.[!.]* ~/..?*
```

* SSM セッションマネージャーを閉じ、マネジメントコンソールからサインアウトします。

---

### お疲れさまでした！ 
#### AgentCore CLI を使用し、Strands Agents SDK で作成したエージェントを AgentCore ランタイムへデプロイして使用できることを確認しました。


---

## 環境のクリアについて
* (講師が行います。）
* CloudShell から下記を実行
    ```
    curl -L -o bedrock-s3-clear.sh https://tnobep-demo-public.s3.amazonaws.com/bedrock-s3-clear.sh && bash bedrock-s3-clear.sh us-west-2
    ```




