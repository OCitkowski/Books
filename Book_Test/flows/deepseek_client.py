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
    num_ctx: int,  # not used in DeepSeek, but kept for compatibility
    num_predict: int,
    temperature: float,
    repeat_penalty: float,  # not used
    top_p: float,
    api_key: str = None,
    system: str = None,
) -> str:
    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": num_predict,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }
    
    # Debug: save payload
    import os
    debug_dir = "/home/leksandro/Projects/Books/Book_Test/data/processed/debug_requests"
    os.makedirs(debug_dir, exist_ok=True)
    import time
    timestamp = int(time.time())
    debug_file = os.path.join(debug_dir, f"request_{timestamp}.json")
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
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