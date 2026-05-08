#!/usr/bin/env python3
"""
test_deepseek.py — простий тест DeepSeek API
"""

import sys
import os

# Додаємо поточну директорію до sys.path для імпортів
sys.path.insert(0, os.path.dirname(__file__))

from config import MODEL
from flows.deepseek_client import generate_text

def test_deepseek():
    print("Тестую DeepSeek API...")

    # Простий запит
    prompt = "Привіт! Скажи 'Hello World' англійською."

    try:
        response = generate_text(
            prompt,
            model=MODEL["deepseek"]["name"],
            num_ctx=MODEL["deepseek"]["num_ctx"],
            num_predict=MODEL["deepseek"]["num_predict"],
            temperature=MODEL["deepseek"]["temperature"],
            repeat_penalty=MODEL["deepseek"]["repeat_penalty"],
            top_p=MODEL["deepseek"]["top_p"],
            api_key=MODEL["deepseek"]["api_key"],
        )
        print("Відповідь:", response)
        print("✅ Тест пройшов успішно!")
    except Exception as e:
        print("❌ Помилка:", str(e))
        return False

    return True

if __name__ == "__main__":
    test_deepseek()