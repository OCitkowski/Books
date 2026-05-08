"""
Small Ollama wrapper for Qwen thinking models.
"""

from __future__ import annotations

import re
import json
from urllib import request


SPECIAL_TOKEN_RE = re.compile(r"<\|[^>]+?\|>")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def generate_text(
    prompt: str,
    *,
    model: str,
    num_ctx: int,
    num_predict: int,
    temperature: float = 0.0,
    repeat_penalty: float = 1.2,
    top_p: float = 0.8,
) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "repeat_penalty": repeat_penalty,
            "top_p": top_p,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=600) as response:
        result = json.loads(response.read().decode("utf-8"))

    response = result.get("response") or ""
    return SPECIAL_TOKEN_RE.sub("", response).strip()
