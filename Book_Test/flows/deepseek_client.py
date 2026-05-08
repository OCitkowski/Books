"""
deepseek_client.py — DeepSeek API client for chat completions
"""

import json
import os
from urllib import request


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def generate_text(
    prompt: str,
    *,
    model: str,
    num_ctx: int = 4000,  # not used in DeepSeek, but kept for compatibility
    num_predict: int,
    temperature: float = 0.0,
    repeat_penalty: float = 1.2,  # not used
    top_p: float = 0.8,
    api_key: str = None,
) -> str:
    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that follows instructions precisely."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": num_predict,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        DEEPSEEK_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=600) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "error" in result:
        raise ValueError(f"DeepSeek API error: {result['error']}")

    content = result["choices"][0]["message"]["content"].strip()
    if not content:
        raise ValueError("DeepSeek API returned empty response")

    return content