"""
error_handling/01_error_handling.py
エラーハンドリングとフォールバックのサンプル。

実運用では、モデル呼び出しが常に成功するとは限らない。代表的な失敗:
- ModelThrottledException   … レート制限（スロットリング）。混雑時に発生。
- ContextWindowOverflowException … 入力がモデルのコンテキスト上限を超過。
- ClientError (AccessDeniedException 等) … 権限不足やモデル未有効化など（boto3 由来）。

このサンプルで示すパターン:
  (1) 例外を種類ごとに捕捉し、ユーザー向けの日本語メッセージを出し分ける。
  (2) 主モデルが失敗したら、別の「フォールバックモデル」へ自動的に切り替えて
      再試行する（可用性を上げる定番パターン）。

このサンプルで実演する3ケース:
  - 正常系             … 主モデルがそのまま回答する。
  - フォールバック成功 … 主モデルに無効なモデルIDを設定して故意に失敗させ、
                         フォールバックモデルで回答できることを示す。
  - コンテキスト超過   … 巨大な入力を渡し、超過エラーを捕捉して案内する。

補足（SDK 標準のリトライについて）:
- Strands の既定のリトライ戦略は ModelThrottledException を自動でリトライする。
  そのため通常は一時的なスロットリングは SDK 内部で吸収される。
- 本サンプルは「SDK のリトライでも回復しなかった場合」や「別モデルへ切り替えたい
  場合」に、アプリ側でどう守るかを示すもの。

参考:
- https://strandsagents.com/docs/api/python/strands.types.exceptions/
- https://strandsagents.com/docs/user-guide/sdk/agents/retry-strategies/
"""

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.types.exceptions import (
    ContextWindowOverflowException,
    ModelThrottledException,
)

try:
    # boto3（AWS SDK）由来のエラー。認証・権限・モデル未有効化などで発生する。
    from botocore.exceptions import ClientError
except ImportError:  # botocore が無い環境でも import エラーで落ちないように
    ClientError = None


# --- 主モデルとフォールバックモデル ---
# 主モデル: 通常使うモデル。
primary_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)
# フォールバックモデル: 主モデルが失敗したときに切り替える控えのモデル。
# （実運用では別リージョン・別モデルにして可用性を高めるとよい）
fallback_model = BedrockModel(
    model_id="us.amazon.nova-micro-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)

SYSTEM_PROMPT = "あなたは親切な日本語アシスタントです。簡潔に回答してください。"


def ask_with_handling(prompt: str, model: BedrockModel) -> str:
    """
    指定モデルでエージェントを実行し、エラーを種類ごとに捕捉して
    ユーザー向けの日本語メッセージを返す。

    主モデルがスロットリングや権限／モデルIDエラーで失敗した場合は、
    フォールバックモデルへ切り替えて1回だけ再試行する。

    Args:
        prompt: ユーザーからの入力
        model: 使用する主モデル

    Returns:
        str: 回答テキスト、またはユーザー向けのエラーメッセージ
    """
    try:
        agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, callback_handler=None)
        result = agent(prompt)
        return result.message["content"][0]["text"]

    except ModelThrottledException as e:
        # スロットリング: 混雑が原因。フォールバックモデルへ切り替えて再試行する。
        print(f"  [警告] 主モデルがスロットリングされました: {e}")
        print("  [情報] フォールバックモデルに切り替えて再試行します…")
        return _retry_with_fallback(prompt)

    except ContextWindowOverflowException as e:
        # コンテキスト超過: 入力や会話履歴が長すぎる。ユーザーに短縮を促す。
        print(f"  [警告] コンテキスト長を超過しました: {type(e).__name__}")
        return (
            "入力が長すぎて処理できませんでした。"
            "内容を短くするか、分割して再度お試しください。"
        )

    except Exception as e:  # noqa: BLE001  デモのため広めに捕捉
        msg = str(e)
        # 入力トークン超過は、環境により ContextWindowOverflowException ではなく
        # Bedrock の生エラー（"Input Tokens Exceeded" 等）として届くことがある。
        # メッセージ内容からも超過を判定し、ユーザーに短縮を促す。
        if "Input Tokens Exceeded" in msg or "input tokens exceeds" in msg.lower():
            print("  [警告] 入力トークンが上限を超過しました")
            return (
                "入力が長すぎて処理できませんでした。"
                "内容を短くするか、分割して再度お試しください。"
            )

        # 権限不足・モデル未有効化・無効なモデルID などの AWS 由来エラーを判定する。
        # （エラーコードは ValidationException / validationException と大小ゆらぎがある）
        if ClientError is not None and isinstance(e, ClientError):
            code = e.response.get("Error", {}).get("Code", "Unknown")
            print(f"  [警告] 主モデルの呼び出しに失敗しました（エラーコード: {code}）")
            if code.lower() in ("accessdeniedexception", "unrecognizedclientexception"):
                return (
                    "モデルへのアクセスが拒否されました。"
                    "Amazon Bedrock でモデルが有効化されているか、"
                    "IAM 権限が付与されているかをご確認ください。"
                    f"（エラーコード: {code}）"
                )
            # それ以外（無効なモデルID 等）はフォールバックモデルで再試行する。
            print("  [情報] フォールバックモデルに切り替えて再試行します…")
            return _retry_with_fallback(prompt)
        # 想定外のエラーは、原因が分かる形で返す（ログには詳細を残す想定）。
        return f"想定外のエラーが発生しました: {type(e).__name__}: {e}"


def _retry_with_fallback(prompt: str) -> str:
    """フォールバックモデルで1回だけ再試行する。"""
    try:
        agent = Agent(model=fallback_model, system_prompt=SYSTEM_PROMPT, callback_handler=None)
        result = agent(prompt)
        return "[フォールバックモデルの回答] " + result.message["content"][0]["text"]
    except Exception as e:  # noqa: BLE001
        return f"フォールバックモデルでも失敗しました: {type(e).__name__}: {e}"


if __name__ == "__main__":
    print("=" * 60)
    print("エラーハンドリングとフォールバックのサンプル")
    print(f"  主モデル        : {primary_model.config['model_id']}")
    print(f"  フォールバック  : {fallback_model.config['model_id']}")
    print("=" * 60)

    # --- ケース1: 正常系。主モデルがそのまま回答する ---
    print("\n【ケース1】正常系")
    question = "Python の list と tuple の違いを1つ挙げてください。"
    print(f"質問: {question}")
    print("-" * 50)
    answer = ask_with_handling(question, primary_model)
    print(f"回答: {answer}")

    # --- ケース2: 主モデルを故意に失敗させてフォールバックを実演 ---
    # 存在しないモデルIDを指定すると ClientError (ValidationException) が発生する。
    # それを捕捉してフォールバックモデルで回答できることを示す。
    print("\n【ケース2】主モデル失敗 → フォールバック")
    broken_model = BedrockModel(
        model_id="us.amazon.nonexistent-model-v9:0",  # 存在しない無効なID
        region_name="us-west-2",
    )
    print(f"質問: {question}")
    print("-" * 50)
    answer = ask_with_handling(question, broken_model)
    print(f"回答: {answer}")

    # --- ケース3: コンテキスト超過を実演 ---
    # 巨大な入力を渡し、ContextWindowOverflowException を捕捉して案内する。
    print("\n【ケース3】コンテキスト超過")
    huge_prompt = "あ" * 2_000_000  # わざと巨大な入力でコンテキスト上限を超えさせる
    print(f"質問: 「あ」を {len(huge_prompt):,} 文字（巨大な入力）")
    print("-" * 50)
    answer = ask_with_handling(huge_prompt, primary_model)
    print(f"回答: {answer}")

    print("\n" + "=" * 60)
    print("ポイント:")
    print("  - 例外を種類ごとに捕捉し、ユーザー向けメッセージを出し分ける。")
    print("  - 主モデルが失敗したらフォールバックモデルへ切り替えて再試行する。")
    print("  - SDK 既定のリトライ戦略も ModelThrottledException を自動リトライする。")
    print("=" * 60)
