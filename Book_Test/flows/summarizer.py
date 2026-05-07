"""
flows/summarizer.py — аналіз кожного чанка → data/processed/summaries.json
"""

import json
import logging
import time
from pathlib import Path

from langchain_ollama import OllamaLLM

from config import PATHS, PROMPTS, MODEL

logger = logging.getLogger(__name__)


def _load_prompt(var: str) -> str:
    path = PROMPTS["summary"]
    if not path.exists():
        raise FileNotFoundError(f"Промт не знайдено: {path}")
    return path.read_text(encoding="utf-8")


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


def analyze_chunks(chunks: list[str]) -> list[dict]:
    """
    Аналізує кожен чанк, зберігає summaries.json після кожного кроку.
    Resume: пропускає вже оброблені чанки.
    """
    output_file = PATHS["summaries"]
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Resume
    summaries: list[dict] = []
    if output_file.exists():
        try:
            summaries = json.loads(output_file.read_text(encoding="utf-8"))
            logger.info(f"Resume: знайдено {len(summaries)} готових summaries")
        except Exception as e:
            logger.warning(f"Не вдалося завантажити summaries: {e}")

    prompt_template = _load_prompt("summary")
    #llm = OllamaLLM(model=MODEL["name"], temperature=MODEL["temperature_summary"])
    llm = OllamaLLM(
        model=MODEL["name"],
        temperature=MODEL["temperature_summary"],
        num_ctx=MODEL["num_ctx"],
        num_predict=MODEL["num_predict"]  # <--- Тепер модель не замовкне завчасно
    )

    start_index = len(summaries)
    total = len(chunks)

    if start_index >= total:
        logger.info("Всі чанки вже оброблені")
        return summaries

    logger.info(f"Починаємо з чанка {start_index + 1}/{total}")

    for i, chunk in enumerate(chunks[start_index:], start=start_index):
        num = i + 1
        logger.info(f"[{num}/{total}] Аналізую чанк ({len(chunk)} символів)...")

        # Виправлено: використовуємо replace замість format, 
        # щоб уникнути KeyError через фігурні дужки у JSON-промті
        prompt = prompt_template.replace("{chunk}", chunk)
        summary = None

        for attempt in range(1, 4):
            try:
                t0 = time.time()
                response = llm.invoke(prompt)
                elapsed = time.time() - t0
                logger.info(f"[{num}/{total}] Відповідь за {elapsed:.1f}s")

                parsed = _parse_json(response)
                summary = {"chunk_index": i, "chunk_size": len(chunk), **parsed}
                logger.info(
                    f"[{num}/{total}] ✔ {len(parsed.get('events', []))} подій, "
                    f"{len(parsed.get('characters', []))} персонажів"
                )
                break

            except json.JSONDecodeError as e:
                logger.warning(f"[{num}/{total}] Спроба {attempt}: помилка JSON — {e}")
                if attempt == 3:
                    logger.error(f"[{num}/{total}] ✘ Зберігаємо raw відповідь")
                    summary = {"chunk_index": i, "chunk_size": len(chunk),
                               "raw_response": response, "parse_error": str(e)}
            except Exception as e:
                logger.error(f"[{num}/{total}] Помилка: {e}")
                if attempt == 3:
                    summary = {"chunk_index": i, "chunk_size": len(chunk), "error": str(e)}
                else:
                    time.sleep(5)

        summaries.append(summary)
        output_file.write_text(
            json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(f"[{num}/{total}] Збережено → {output_file}")

    logger.info(f"Аналіз завершено. Summaries: {len(summaries)}")
    return summaries
