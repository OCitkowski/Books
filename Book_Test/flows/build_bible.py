"""
flows/build_bible.py — summaries.json → data/processed/bible.json
"""

import json
import logging

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
from flows.text_parser import clean_bullet, parse_inline_value, parse_list, parse_sections, split_name_value

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
        for description in s.get("descriptions", []):
            lines.append(f"Сцена: {description.get('title', '')}")
            if description.get("scene"):
                lines.append(f"Опис: {description['scene']}")
            if description.get("characters"):
                lines.append("Персонажі: " + ", ".join(description["characters"]))
            location = description.get("location", {})
            if location.get("name") or location.get("description"):
                lines.append(f"Локація: {location.get('name', '')}, {location.get('description', '')}")
            for key, label in (
                ("intent", "Намір"),
                ("conflict", "Конфлікт"),
                ("state", "Стан"),
                ("relation", "Стосунки"),
                ("outcome", "Результат"),
            ):
                if description.get(key):
                    lines.append(f"{label}: {description[key]}")
            if description.get("outfits"):
                outfits = [f"{name}: {value}" for name, value in description["outfits"].items()]
                lines.append("Одяг: " + "; ".join(outfits))
            if description.get("props"):
                lines.append("Предмети: " + ", ".join(description["props"]))
            lines.append("")
        lines.append("")
    return "\n".join(lines)


def _write_debug_response(response: str) -> None:
    debug_dir = PATHS["bible"].parent
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_file = debug_dir / "debug_raw_bible.txt"
    debug_file.write_text(response, encoding="utf-8")
    logger.error(f"Сира відповідь збережена для аналізу: {debug_file}")


def _unique_values(summaries: list[dict], key: str, limit: int) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for summary in summaries:
        raw_values = summary.get(key, [])
        if isinstance(raw_values, str):
            raw_values = [raw_values]
        for value in raw_values:
            if not isinstance(value, str):
                continue
            value = value.strip()
            if value and value not in seen:
                values.append(value)
                seen.add(value)
            if len(values) >= limit:
                return values
    return values


def _summary_characters(summaries: list[dict], limit: int) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for summary in summaries:
        for description in summary.get("descriptions", []):
            for character in description.get("characters", []):
                if character and character not in seen:
                    values.append(character)
                    seen.add(character)
                if len(values) >= limit:
                    return values
    return values


def _build_fallback_bible(summaries: list[dict]) -> dict:
    characters = _summary_characters(summaries, 50)

    return {
        "genre": "Постапокаліптичне виживання з елементами переродження",
        "style": "Стиль напружений і практичний. Сюжет тримається на підготовці, дефіциті ресурсів, конфліктах за безпеку та різких катастрофічних змінах.",
        "language_features": [
            "Детальні описи запасів, укріплень і спорядження",
            "Сцени соціального тиску та боротьби за ресурси",
            "Контраст між побутовою конкретикою і масштабною катастрофою",
        ],
        "writing_rules": [
            "Показувати виживання через конкретні рішення та дії",
            "Підкреслювати дефіцит їжі, безпеки, тепла й довіри",
            "Тримати хронологію катастрофи послідовною",
            "Не пом'якшувати конфлікти, коли персонажі борються за ресурси",
        ],
        "themes": [
            "Виживання після краху звичного світу",
            "Помста та використання знань з минулого життя",
            "Розпад соціальної моралі під тиском катастрофи",
        ],
        "locations": {
            "Квартира-фортеця": "Головний безпечний простір героїні, захищений технікою, запасами та контролем доступу.",
            "Магічний простір": "Особистий вимір для зберігання, вирощування ресурсів і розвитку сил героїні.",
            "Затоплене місто": "Небезпечне середовище, де руйнуються правила, логістика і соціальний порядок.",
        },
        "world_building": [
            "Правила світу потребують уточнення на основі повного summaries.json.",
        ],
        "relationships": {},
        "characters": {
            name: {
                "role": "Важливий персонаж сюжету",
                "appearance_base": "Фізичні риси потребують уточнення під час написання сцен.",
                "outfits": [
                    {
                        "name": "Виживання",
                        "description": "Практичний одяг і спорядження, доречні для спеки, повені або холоду.",
                    }
                ],
                "speech_style": "Говорить відповідно до ролі в конфлікті та рівня довіри до героїні.",
                "behavior": "Діє під тиском небезпеки, дефіциту ресурсів і особистих мотивів.",
            }
            for name in characters
        },
    }


def _parse_locations(lines: list[str]) -> dict[str, str]:
    locations: dict[str, str] = {}
    for line in lines:
        name, description = split_name_value(line)
        if name:
            locations[name] = description or "Опис потребує уточнення."
        if len(locations) >= 5:
            break
    return locations


def _parse_characters(lines: list[str]) -> dict[str, dict]:
    characters: dict[str, dict] = {}
    for line in lines:
        parts = [part.strip() for part in line.lstrip("-*• ").split("|")]
        if not parts or not parts[0]:
            continue

        name = parts[0]
        role = parts[1] if len(parts) > 1 and parts[1] else "Важливий персонаж сюжету"
        appearance = parts[2] if len(parts) > 2 and parts[2] else "Фізичні риси потребують уточнення."
        speech = parts[3] if len(parts) > 3 and parts[3] else "Манера мовлення потребує уточнення."
        behavior = parts[4] if len(parts) > 4 and parts[4] else "Поведінка залежить від сюжетної ситуації."
        outfit_parts = parts[5:] if len(parts) > 5 else ["Виживання: практичне спорядження."]
        outfits = []
        for outfit in outfit_parts:
            outfit_name, outfit_description = split_name_value(outfit)
            if outfit_name:
                outfits.append(
                    {
                        "name": outfit_name,
                        "description": outfit_description or outfit,
                    }
                )

        characters[name] = {
            "role": role,
            "appearance_base": appearance,
            "outfits": outfits,
            "speech_style": speech,
            "behavior": behavior,
        }
        if len(characters) >= 50:
            break
    return characters


def _parse_relationships(lines: list[str]) -> dict[str, str]:
    relationships: dict[str, str] = {}
    for line in lines:
        name, description = split_name_value(line)
        if name:
            relationships[name] = description
    return relationships


def _parse_bible_response(response: str, summaries: list[dict]) -> dict:
    if not response.strip():
        raise ValueError("Empty response")

    sections = parse_sections(
        response,
        {
            "GENRE",
            "STYLE",
            "TONE",
            "LANGUAGE_FEATURES",
            "WRITING_RULES",
            "THEMES",
            "WORLD_BUILDING",
            "LOCATIONS",
            "CHARACTERS",
            "RELATIONSHIPS",
        },
    )

    bible = {
        "genre": parse_inline_value(sections["GENRE"]),
        "style": " ".join(clean_bullet(line) for line in sections["STYLE"]).strip(),
        "language_features": parse_list(sections["LANGUAGE_FEATURES"], limit=6),
        "writing_rules": parse_list(sections["WRITING_RULES"], limit=8),
        "themes": parse_list(sections["THEMES"], limit=6),
        "world_building": parse_list(sections["WORLD_BUILDING"], limit=8),
        "locations": _parse_locations(sections["LOCATIONS"]),
        "characters": _parse_characters(sections["CHARACTERS"]),
        "relationships": _parse_relationships(sections["RELATIONSHIPS"]),
    }

    fallback = _build_fallback_bible(summaries)
    for key in ("genre", "style"):
        if not bible[key]:
            bible[key] = fallback[key]
    for key in ("language_features", "writing_rules", "themes", "world_building"):
        if not bible[key]:
            bible[key] = fallback[key]
    if not bible["locations"]:
        bible["locations"] = fallback["locations"]
    if not bible["characters"]:
        bible["characters"] = fallback["characters"]
    if not bible["relationships"]:
        bible["relationships"] = fallback["relationships"]

    return bible


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

    output_file = PATHS["bible"]

    logger.info("Генерую bible.json...")
    full_config = get_full_model_config("writer")
    generate_func = get_generate_func(full_config)
    response = generate_func(
        prompt,
        model=full_config["name"],
        num_ctx=full_config["num_ctx"],
        num_predict=full_config["num_predict"],
        temperature=full_config["temperature"],
        repeat_penalty=full_config["repeat_penalty"],
        top_p=full_config["top_p"],
        **({"api_key": full_config.get("api_key")} if full_config.get("type") == "deepseek" else {}),
    )
    try:
        bible = _parse_bible_response(response, summaries)
    except ValueError as e:
        logger.error(f"Помилка парсингу bible секцій: {e}")
        _write_debug_response(response)
        logger.warning("Створюю fallback bible.json на основі summaries.json")
        bible = _build_fallback_bible(summaries)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(bible, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"✔ bible.json збережено → {output_file}")
    return bible
