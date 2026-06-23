from __future__ import annotations

import json
import re
from typing import Any


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_ingredients(raw_input: str) -> list[str]:
    if not raw_input:
        return []

    ingredients = [
        normalize_text(item)
        for item in raw_input.split(",")
        if normalize_text(item)
    ]

    return list(dict.fromkeys(ingredients))


def safe_json_loads(value: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if fallback is None:
        fallback = {}

    try:
        return json.loads(value)
    except Exception:
        return fallback


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(value, maximum))


def format_score(score: float) -> str:
    return f"{round(score)}%"


def quality_label(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Good"
    if score >= 40:
        return "Possible"
    return "Creative"


def deduplicate_by_name(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    for item in items:
        name = normalize_text(str(item.get("name", "")))
        if not name or name in seen:
            continue

        seen.add(name)
        result.append(item)

    return result
