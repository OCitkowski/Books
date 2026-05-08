"""
flows/summarizer.py — аналіз кожного чанка → data/processed/summaries.json
"""

import json
import logging
import time

from config import PATHS, PROMPTS, MODEL
from flows.ollama_client import generate_text as ollama_generate
from flows.deepseek_client import generate_text as deepseek_generate


def get_generate_func(model_config):
    model_type = model_config.get("type", "ollama")
    if model_type == "deepseek":
        return deepseek_generate
    else:
        return ollama_generate


def get_full_model_config(model_key):
    """Повертає повний config для моделі, об'єднуючи базові налаштування з типом."""
    base_config = MODEL[model_key].copy()
    model_type = base_config["type"]
    type_config = MODEL.get(model_type, {})
    # Об'єднуємо, але базові мають пріоритет для name, type
    full_config = {**type_config, **base_config}
    return full_config
from flows.text_parser import group_numbered_pipe_records, parse_pipe_description, parse_sections

logger = logging.getLogger(__name__)


def _load_prompt(var: str) -> str:
    path = PROMPTS["summary"]
    if not path.exists():
        raise FileNotFoundError(f"Промт не знайдено: {path}")
    return path.read_text(encoding="utf-8")


def _write_debug_response(chunk_num: int, attempt: int, response: str) -> None:
    debug_dir = PATHS["summaries"].parent / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_file = debug_dir / f"summary_chunk_{chunk_num:03d}_attempt_{attempt}.txt"
    debug_file.write_text(response, encoding="utf-8")
    logger.warning(f"[{chunk_num}] Сира відповідь збережена: {debug_file}")


def _save_summary_response(chunk_num: int, attempt: int, response: str) -> None:
    response_dir = PATHS["summaries"].parent / "summary_responses"
    response_dir.mkdir(parents=True, exist_ok=True)
    response_file = response_dir / f"summary_chunk_{chunk_num:03d}_attempt_{attempt}.txt"
    response_file.write_text(response, encoding="utf-8")
    logger.info(f"[{chunk_num}] Summary response saved: {response_file}")


def _parse_summary(response: str) -> dict:
    if not response.strip():
        raise ValueError("Empty response")

    sections = parse_sections(
        response,
        {"DESCRIPTIONS"},
    )
    descriptions = [
        description
        for line in group_numbered_pipe_records(sections["DESCRIPTIONS"])
        if (description := parse_pipe_description(line, body_key="scene")) is not None
    ]

    if not descriptions:
        raise ValueError("No DESCRIPTIONS records found")

    characters = sorted(
        {
            character
            for description in descriptions
            for character in description.get("characters", [])
        }
    )

    return {
        "descriptions": descriptions,
        "characters": characters,
    }


def _fallback_summary(chunk_index: int, chunk: str) -> dict:
    text_preview = " ".join(chunk.split())[:220]
    return {
        "descriptions": [
            {
                "index": 1,
                "title": f"Чанк {chunk_index + 1} потребує повторного аналізу",
                "scene": text_preview,
                "characters": [],
                "location": {"name": "", "description": ""},
                "intent": "",
                "conflict": "",
                "state": "невизначений",
                "outfits": {},
                "props": [],
                "relation": "",
                "outcome": "Модель не повернула валідні DESCRIPTIONS.",
            }
        ],
        "characters": [],
    }


def _retry_prompt(prompt: str) -> str:
    return (
        "ВАЖЛИВО: попередня відповідь була порожня або невалідна. "
        "Поверни тільки секцію DESCRIPTIONS у pipe-форматі з промту. "
        "Без JSON, без пояснень, без повторів.\n\n"
        f"{prompt}"
    )


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
                active_prompt = prompt if attempt == 1 else _retry_prompt(prompt)
                full_config = get_full_model_config("summary")
                generate_func = get_generate_func(full_config)
                response = generate_func(
                    active_prompt,
                    model=full_config["name"],
                    num_ctx=full_config["num_ctx"],
                    num_predict=full_config["num_predict"],
                    temperature=full_config["temperature"],
                    repeat_penalty=full_config["repeat_penalty"],
                    top_p=full_config["top_p"],
                    **({"api_key": full_config.get("api_key")} if full_config.get("type") == "deepseek" else {}),
                )
                _save_summary_response(num, attempt, response)
                elapsed = time.time() - t0
                logger.info(f"[{num}/{total}] Відповідь за {elapsed:.1f}s")

                parsed = _parse_summary(response)
                summary = {"chunk_index": i, "chunk_size": len(chunk), **parsed}
                logger.info(
                    f"[{num}/{total}] ✔ {len(parsed.get('descriptions', []))} описів, "
                    f"{len(parsed.get('characters', []))} персонажів"
                )
                break

            except Exception as e:
                logger.warning(f"[{num}/{total}] Спроба {attempt}: не вдалося розібрати відповідь — {e}")
                if attempt == 3:
                    logger.error(f"[{num}/{total}] ✘ Створюємо fallback summary")
                    parsed = _fallback_summary(i, chunk)
                    summary = {"chunk_index": i, "chunk_size": len(chunk),
                               **parsed, "parse_error": str(e)}
                else:
                    time.sleep(2)
            except Exception as e:
                logger.error(f"[{num}/{total}] Помилка: {e}")
                if attempt == 3:
                    parsed = _fallback_summary(i, chunk)
                    summary = {"chunk_index": i, "chunk_size": len(chunk),
                               **parsed, "error": str(e)}
                else:
                    time.sleep(5)

        summaries.append(summary)
        output_file.write_text(
            json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(f"[{num}/{total}] Збережено → {output_file}")

    logger.info(f"Аналіз завершено. Summaries: {len(summaries)}")
    return summaries
