"""
flows/build_skeleton.py — summaries.json → data/processed/skeleton.json
"""

import json
import logging

from config import PATHS, PROMPTS
from flows.text_parser import group_numbered_pipe_records, parse_pipe_description, parse_sections

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
        for description in s.get("descriptions", []):
            parts = [
                str(description.get("index", "")),
                description.get("title", ""),
                f"SCENE: {description.get('scene', '')}",
                "Characters: " + ",".join(description.get("characters", [])),
            ]
            location = description.get("location", {})
            if location.get("name") or location.get("description"):
                parts.append(f"Location: {location.get('name', '')},{location.get('description', '')}")
            for key, label in (
                ("intent", "Intent"),
                ("conflict", "Conflict"),
                ("state", "State"),
                ("relation", "Relation"),
                ("outcome", "Outcome"),
            ):
                if description.get(key):
                    parts.append(f"{label}: {description[key]}")
            if description.get("props"):
                parts.append("Props: " + ",".join(description["props"]))
            lines.append("|".join(parts))
        lines.append("")
    return "\n".join(lines)


def _write_debug_response(response: str) -> None:
    debug_dir = PATHS["skeleton"].parent
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_file = debug_dir / "debug_raw_skeleton.txt"
    debug_file.write_text(response, encoding="utf-8")
    logger.error(f"Сира відповідь збережена для аналізу: {debug_file}")


def _parse_skeleton_response(response: str) -> dict:
    if not response.strip():
        raise ValueError("Empty response")

    sections = parse_sections(response, {"SCENES"})
    scene_lines = group_numbered_pipe_records(sections["SCENES"] or response.splitlines())
    scenes = []
    for line in scene_lines:
        scene = parse_pipe_description(line, body_key="action")
        if scene is not None:
            scenes.append(scene)

    if not scenes:
        raise ValueError("No scenes found")

    for index, scene in enumerate(scenes, start=1):
        scene["index"] = index

    return {"scenes": scenes}


def _build_fallback_skeleton(summaries: list[dict]) -> dict:
    scenes = []
    for summary in summaries:
        if "error" in summary or "parse_error" in summary:
            continue
        for description in summary.get("descriptions", []):
            scenes.append(
                {
                    "index": len(scenes) + 1,
                    "title": description.get("title", ""),
                    "action": description.get("scene", ""),
                    "characters": description.get("characters", []),
                    "location": description.get("location", {"name": "", "description": ""}),
                    "intent": description.get("intent", ""),
                    "conflict": description.get("conflict", ""),
                    "state": description.get("state", ""),
                    "outfits": description.get("outfits", {}),
                    "props": description.get("props", []),
                    "relation": description.get("relation", ""),
                    "outcome": description.get("outcome", ""),
                }
            )
            if len(scenes) >= 500:
                return {"scenes": scenes}
    return {"scenes": scenes}


def build_skeleton() -> dict:
    summaries_file = PATHS["summaries"]
    if not summaries_file.exists():
        raise FileNotFoundError(f"summaries.json не знайдено: {summaries_file}")

    summaries = json.loads(summaries_file.read_text(encoding="utf-8"))
    logger.info(f"Завантажено {len(summaries)} summaries")

    logger.info("Створюю skeleton.json на основі summaries.json без моделі")
    skeleton = _build_fallback_skeleton(summaries)

    output_file = PATHS["skeleton"]
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"✔ skeleton.json збережено → {output_file}")
    return skeleton
