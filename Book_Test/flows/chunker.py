"""
flows/chunker.py
"""

import logging
from pathlib import Path

from config import PATHS, CHUNKING

logger = logging.getLogger(__name__)


def load_text() -> str:
    path = PATHS["input"]
    if not path.exists():
        raise FileNotFoundError(f"Файл не знайдено: {path}")
    text = path.read_text(encoding="utf-8")
    logger.info(f"Завантажено: {len(text)} символів з {path}")
    return text


def split_into_chunks(text: str) -> list[str]:
    chunk_size = CHUNKING["chunk_size"]
    overlap    = CHUNKING["overlap"]

    # Пробуємо \n\n, якщо не дає результату — падаємо на \n
    paragraphs = text.split("\n\n")
    if len(paragraphs) < 5:
        logger.warning("Мало абзаців через \\n\\n, пробуємо розбиття по \\n")
        paragraphs = text.split("\n")

    logger.info(f"Абзаців для розбиття: {len(paragraphs)}")

    chunks = []
    current: list[str] = []
    current_size = 0

    for para in paragraphs:
        para_len = len(para)
        if not para.strip():
            continue

        if current_size + para_len > chunk_size and current:
            chunk_text = "\n".join(current)
            chunks.append(chunk_text)
            logger.info(f"Чанк {len(chunks)}: {len(chunk_text)} символів")

            tail = chunk_text[-overlap:]
            boundary = tail.find("\n")
            overlap_text = tail[boundary + 1:] if boundary != -1 else tail

            current = [overlap_text] if overlap_text.strip() else []
            current_size = len(overlap_text)

        current.append(para)
        current_size += para_len + 1

    if current:
        chunk_text = "\n".join(current)
        chunks.append(chunk_text)
        logger.info(f"Чанк {len(chunks)} (останній): {len(chunk_text)} символів")

    chunks_dir = PATHS["chunks_dir"]
    chunks_dir.mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(chunks):
        (chunks_dir / f"chunk_{i+1:03d}.txt").write_text(chunk, encoding="utf-8")

    logger.info(f"Всього чанків: {len(chunks)}, збережено в {chunks_dir}")
    return chunks
