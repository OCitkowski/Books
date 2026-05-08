"""
config.py — всі налаштування пайплайну
"""

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# ── Коренева папка книги ─────────────────────────────────────
# Працює незалежно від поточної директорії запуску.
BOOK_DIR = Path(__file__).resolve().parent

# ── Шляхи ───────────────────────────────────────────────────
PATHS = {
    "input":       BOOK_DIR / "data/original/ProjectXranili.txt",
    "chunks_dir":  BOOK_DIR / "data/chunks",
    "summaries":   BOOK_DIR / "data/processed/summaries.json",
    "bible":       BOOK_DIR / "data/processed/bible.json",
    "skeleton":    BOOK_DIR / "data/processed/skeleton.json",
    "log":         BOOK_DIR / "pipeline.log",
}

# ── Промти ──────────────────────────────────────────────────
PROMPTS = {
    "summary":  BOOK_DIR / "prompts/summary.txt",
    "bible":    BOOK_DIR / "prompts/bible.txt",
    "skeleton": BOOK_DIR / "prompts/skeleton.txt",
}

# ── Модель ──────────────────────────────────────────────────
MODEL = {
    "summary": {
        "type": "deepseek",
        "name": "deepseek-v4-flash",
    },
    "writer": {
        "type": "ollama",
        "name": "gemma4:26b",
    },
    "ollama": {
        "num_ctx": 40000,
        "num_predict": 20000,
        "temperature": 0.25,
        "repeat_penalty": 1.35,
        "top_p": 0.8,
    },
    "deepseek": {
        "num_ctx": 25000,
        "num_predict": 2000,
        "temperature": 0.1,
        "repeat_penalty": 1.0,
        "top_p": 0.9,
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
    },
}

# ── Chunking ─────────────────────────────────────────────────
CHUNKING = {
    "chunk_size": 5000,
    "overlap":      300,
}
