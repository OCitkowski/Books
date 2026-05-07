"""
flows/build_bible.py — summaries.json → data/processed/bible.json
"""

import json
import logging
from pathlib import Path

from langchain_ollama import OllamaLLM

from config import PATHS, PROMPTS, MODEL

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    path = PROMPTS["bible"]
    if not path.exists():
        raise FileNotFoundError(f"Промт не знайдено: {path}")
    return path.read_text(encoding="utf-8")


def _summaries_to_text(summaries: list[dict]) -> str:
    lines = []
    for s in summaries:
        if "error" in s or "parse_error" in s:
            logger.warning(f"Пропускаємо чанк {s.get('chunk_index')} з помилкою")
            continue
        lines.append(f"=== Частина {s['chunk_index'] + 1} ===")
        if s.get("events"):
            lines.append("Події: " + "; ".join(s["events"]))
        if s.get("characters"):
            lines.append("Персонажі: " + ", ".join(s["characters"]))
        if s.get("tone"):
            lines.append(f"Тон: {s['tone']}")
        if s.get("key_details"):
            lines.append("Деталі: " + "; ".join(s["key_details"]))
        lines.append("")
    return "\n".join(lines)


def _parse_json(response: str) -> dict:
    clean = response.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else clean
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start != -1 and end > start:
        clean = clean[start:end]
    return json.loads(clean)


def build_bible() -> dict:
    summaries_file = PATHS["summaries"]
    if not summaries_file.exists():
        raise FileNotFoundError(f"summaries.json не знайдено: {summaries_file}")

    summaries = json.loads(summaries_file.read_text(encoding="utf-8"))
    logger.info(f"Завантажено {len(summaries)} summaries")

    merged_text = _summaries_to_text(summaries)
    logger.info(f"Merged text для bible: {len(merged_text)} символів")

    prompt_template = _load_prompt()
    #prompt = prompt_template.format(merged_text=merged_text)
    prompt = prompt_template.replace("{merged_text}", merged_text)

    #llm = OllamaLLM(model=MODEL["name"], temperature=MODEL["temperature_bible"])
    llm = OllamaLLM(
        model=MODEL["name"],
        temperature=MODEL["temperature_bible"],
        num_ctx=MODEL["num_ctx"],
        num_predict=MODEL["num_predict"]  # <--- Тепер модель не замовкне завчасно
    )

    logger.info("Генерую bible.json...")
    response = llm.invoke(prompt)
    bible = _parse_json(response)

    output_file = PATHS["bible"]
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(bible, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"✔ bible.json збережено → {output_file}")
    return bible
