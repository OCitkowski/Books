"""
config.py — всі налаштування пайплайну
"""

from pathlib import Path

# ── Коренева папка книги ─────────────────────────────────────
# main.py запускається з папки Book_<назва>/
BOOK_DIR = Path(".")

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
    "name":                "gemma4:26b",
    "num_ctx":             20000,
    "num_predict":         5000,           # <--- Дозволяємо довгі відповіді
    "temperature_summary":  0.1,
    "temperature_bible":    0.2,
    "temperature_skeleton": 0.1,
}

# ── Chunking ─────────────────────────────────────────────────
CHUNKING = {
    "chunk_size": 30000,   # символів (~6-10 чанків на 700k)
    "overlap":     1500,   # ~7.5% overlap
}
