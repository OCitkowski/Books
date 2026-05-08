#!/usr/bin/env python3
"""
test_deepseek_summary.py — тест DeepSeek з summary prompt
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import MODEL
from flows.deepseek_client import generate_text
from flows.summarizer import _load_prompt

def test_deepseek_summary():
    print("Тестую DeepSeek з summary prompt...")

    # Завантажити prompt
    prompt_template = _load_prompt("summary")
    print(f"Prompt length: {len(prompt_template)} chars")

    # Простий chunk
    chunk = "Це тестовий уривок. Герой входить в кімнату і бачить сюрприз."

    # Повний prompt
    prompt = prompt_template.replace("{chunk}", chunk)
    print(f"Full prompt length: {len(prompt)} chars")

    try:
        response = generate_text(
            prompt,
            model="deepseek-v4-flash",
            num_ctx=32000,
            num_predict=4000,
            temperature=0.1,
            repeat_penalty=1.0,
            top_p=0.9,
            api_key=MODEL["deepseek"]["api_key"],
        )
        print("Відповідь:")
        print(repr(response))
        print("Довжина відповіді:", len(response))
    except Exception as e:
        print("❌ Помилка:", str(e))

if __name__ == "__main__":
    test_deepseek_summary()