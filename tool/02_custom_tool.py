"""
tool/02_custom_tool.py
自作のPython関数を @tool デコレータでツールとして使用するサンプル。
"""

from strands import Agent, tool


@tool
def word_counter(text: str) -> dict:
    """
    テキストの文字数と単語数をカウントする。

    Args:
        text: 分析対象のテキスト

    Returns:
        dict: 文字数と単語数を含む辞書
    """
    char_count = len(text)
    word_count = len(text.split())
    return {
        "文字数": char_count,
        "単語数（スペース区切り）": word_count,
    }


@tool
def reverse_string(text: str) -> str:
    """
    文字列を逆順にする。

    Args:
        text: 逆順にする文字列

    Returns:
        str: 逆順にした文字列
    """
    return text[::-1]


# カスタムツールを渡してエージェントを作成
agent = Agent(
    tools=[word_counter, reverse_string],
    system_prompt="あなたはテキスト分析ができるアシスタントです。ツールを活用して回答してください。",
)

result = agent(
    "「Hello World from Strands Agent」の文字数と単語数を教えてください。"
    "また、この文字列を逆順にしてください。"
)
