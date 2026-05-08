"""
Helpers for parsing model text responses into Python data.
"""

from __future__ import annotations

import re


FIELD_RE = re.compile(
    r"(?P<label>SCENE|Action|Characters|Location|Intent|Conflict|State|Outfits|Props|Relation|Outcome):",
    re.IGNORECASE,
)
NUMBERED_PIPE_RE = re.compile(r"^\s*\d+\|")
OUTFIT_SPLIT_RE = re.compile(r",\s*(?=[^,=]{1,60}=)")

def _strip_wrapping(text: str) -> str:
    return text.strip().strip("*_` ")


def parse_sections(text: str, section_names: set[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {name: [] for name in section_names}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        possible_name = line.strip("#*_` ").rstrip(":").strip("*_` ").upper()
        if possible_name in section_names:
            current = possible_name
            continue

        if current is not None:
            lowered = line.lower()
            if lowered.startswith(("ось ", "якщо ", "*(я ", "(я ")):
                continue
            sections[current].append(line)

    return sections


def clean_bullet(line: str) -> str:
    line = _strip_wrapping(line)
    for prefix in ("- ", "* ", "• "):
        if line.startswith(prefix):
            return _strip_wrapping(line[len(prefix):])
    if len(line) > 1 and line[0] in {"-", "*", "•"}:
        return _strip_wrapping(line[1:])

    dot = line.find(". ")
    if dot != -1 and line[:dot].isdigit():
        return line[dot + 2:].strip()

    return _strip_wrapping(line)


def parse_list(lines: list[str], limit: int | None = None) -> list[str]:
    items = [clean_bullet(line) for line in lines]
    items = [item for item in items if item]
    return items[:limit] if limit is not None else items


def parse_inline_value(lines: list[str], default: str = "") -> str:
    if not lines:
        return default
    value = clean_bullet(lines[0])
    return value or default


def split_name_value(line: str) -> tuple[str, str]:
    line = clean_bullet(line)
    for separator in (":", " - ", " — "):
        if separator in line:
            name, value = line.split(separator, 1)
            return name.strip(), value.strip()
    return line.strip(), ""


def split_prefixed_value(text: str) -> tuple[str, str]:
    for separator in (":", "="):
        if separator in text:
            key, value = text.split(separator, 1)
            return key.strip().lower(), value.strip()
    return "", text.strip()


def split_csv(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def parse_outfits(text: str) -> dict[str, str]:
    outfits: dict[str, str] = {}
    for item in OUTFIT_SPLIT_RE.split(text):
        name, description = split_name_value(item.replace("=", ":", 1))
        if name:
            outfits[name] = description
    return outfits


def group_numbered_pipe_records(lines: list[str]) -> list[str]:
    records: list[str] = []
    current: list[str] = []

    for line in lines:
        if NUMBERED_PIPE_RE.match(line):
            if current:
                records.append("|".join(current))
            current = [line.strip()]
        elif current:
            current.append(line.strip())

    if current:
        records.append("|".join(current))

    return records


def parse_pipe_description(line: str, *, body_key: str) -> dict | None:
    line = clean_bullet(line)
    if not line or "|" not in line:
        return None

    parts = [part.strip() for part in line.split("|")]
    if len(parts) < 3:
        return None

    try:
        index = int(parts[0])
    except ValueError:
        return None

    record = {
        "index": index,
        "title": parts[1],
        body_key: "",
        "characters": [],
        "location": {"name": "", "description": ""},
        "intent": "",
        "conflict": "",
        "state": "",
        "outfits": {},
        "props": [],
        "relation": "",
        "outcome": "",
    }

    labelled_text = "|".join(parts[2:])
    matches = list(FIELD_RE.finditer(labelled_text))
    fields: list[tuple[str, str]] = []
    if matches:
        prefix = labelled_text[:matches[0].start()].strip(" |")
        if prefix:
            fields.append((body_key, prefix))
    for pos, match in enumerate(matches):
        start = match.end()
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(labelled_text)
        fields.append((match.group("label").lower(), labelled_text[start:end].strip(" |")))

    if not fields:
        fields = [split_prefixed_value(part) for part in parts[2:]]

    for key, value in fields:
        if key in {"scene", "action"}:
            record[body_key] = value
        elif key == "characters":
            record["characters"] = split_csv(value)
        elif key == "location":
            location_parts = split_csv(value)
            record["location"] = {
                "name": location_parts[0] if location_parts else value,
                "description": ", ".join(location_parts[1:]) if len(location_parts) > 1 else "",
            }
        elif key == "intent":
            record["intent"] = value
        elif key == "conflict":
            record["conflict"] = value
        elif key == "state":
            record["state"] = value
        elif key == "outfits":
            record["outfits"] = parse_outfits(value)
        elif key == "props":
            record["props"] = split_csv(value)
        elif key in {"relation", "relationships"}:
            record["relation"] = value
        elif key == "outcome":
            record["outcome"] = value

    return record
