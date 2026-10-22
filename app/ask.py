"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask "LoRAとは何ですか？" 0.7
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    # 続けて質問し、/exit または /quit で終了

質問のたびに会話履歴を引き継ぐ、ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from google import genai
from google.genai.chats import Chat
from google.genai import errors, types

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat(client: genai.Client, temperature: float) -> Chat:
    return client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(temperature=temperature),
    )


def ask(question: str, temperature: float = 1.0, *, chat: Chat | None = None) -> str:
    if chat is None:
        client = genai.Client(api_key=get_api_key())
        try:
            chat = create_chat(client, temperature)
            response = chat.send_message(question)
        finally:
            client.close()
    else:
        response = chat.send_message(question)

    usage = response.usage_metadata
    if usage is not None:
        print(
            f"[usage] input_tokens={usage.prompt_token_count} "
            f"output_tokens={usage.candidates_token_count}"
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("temperature", nargs="?", default="1.0")
    args = parser.parse_args()

    try:
        temperature = float(args.temperature)
    except ValueError:
        print("Invalid temp")
        return
    if not 0.0 <= temperature <= 2.0:
        print("Invalid temp")
        return
    print(f"[model] {MODEL}")
    client = genai.Client(api_key=get_api_key())
    try:
        chat = create_chat(client, temperature)
        question = args.question
        while True:
            print(f"[質問] {question}\n")
            started = time.perf_counter()
            answer = ask(question, temperature, chat=chat)
            elapsed = time.perf_counter() - started
            print(f"{answer}\n[RT] {elapsed:.2f}秒\n")

            try:
                question = input("質問> ")
            except EOFError:
                break
            if question.strip() in {"/exit", "/quit"}:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
