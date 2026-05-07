"""
flows/build_skeleton.py — summaries.json → data/processed/skeleton.json
"""

import json
import logging

from langchain_ollama import OllamaLLM

from config import PATHS, PROMPTS, MODEL

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    path = PROMPTS["skeleton"]
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
        for ev in s.get("events", []):
            lines.append(f"- {ev}")
        if s.get("characters"):
            lines.append("Персонажі: " + ", ".join(s["characters"]))
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


def build_skeleton() -> dict:
    summaries_file = PATHS["summaries"]
    if not summaries_file.exists():
        raise FileNotFoundError(f"summaries.json не знайдено: {summaries_file}")

    summaries = json.loads(summaries_file.read_text(encoding="utf-8"))
    logger.info(f"Завантажено {len(summaries)} summaries")

    merged_text = _summaries_to_text(summaries)
    logger.info(f"Merged text для skeleton: {len(merged_text)} символів")

    prompt_template = _load_prompt()
    prompt = prompt_template.replace("{merged_text}", merged_text)

    # Ініціалізація з примусовим JSON форматом
    llm = OllamaLLM(
        model=MODEL["name"],
        repeat_penalty=1.2,
        format="json",  # <--- ЦЕ ВИПРАВИТЬ Unterminated string
        temperature=MODEL["temperature_skeleton"],
        num_ctx=MODEL["num_ctx"],
        num_predict=MODEL["num_predict"]
    )

    logger.info("Генерую skeleton.json...")
    response = llm.invoke(prompt)

    try:
        skeleton = _parse_json(response)
    except Exception as e:
        # ВИПРАВЛЕНО: використовуємо батьківську папку файлу skeleton
        debug_dir = PATHS["skeleton"].parent
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / "debug_raw_skeleton.txt"

        debug_file.write_text(response, encoding="utf-8")
        logger.error(f"❌ Помилка парсингу JSON: {e}")
        logger.error(f"Сира відповідь збережена для аналізу: {debug_file}")
        raise

    output_file = PATHS["skeleton"]
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"✔ skeleton.json збережено → {output_file}")
    return skeleton
