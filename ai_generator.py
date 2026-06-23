from __future__ import annotations

import os
from typing import Any

import streamlit as st
from openai import OpenAI

from prompts import (
    abinbev_alternative_prompt,
    ai_cocktail_prompt,
    bartender_tips_prompt,
)
from utils import safe_json_loads


def get_openai_api_key() -> str | None:
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def get_client() -> OpenAI | None:
    api_key = get_openai_api_key()

    if not api_key:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def call_openai_json(prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
    client = get_client()

    if client is None:
        return fallback

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return safe_json_loads(response.output_text, fallback=fallback)

    except Exception:
        return fallback


def generate_ai_cocktail(
    ingredients: list[str],
    style: str,
    occasion: str,
) -> dict[str, Any]:
    fallback = {
        "name": "AI House Cocktail",
        "ingredients": ingredients,
        "instructions": "Shake suitable ingredients with ice, strain into a chilled glass, and adjust with citrus or sugar for balance.",
        "reasoning": "This drink is designed around the ingredients you already have, balancing freshness, sweetness and dilution.",
    }

    return call_openai_json(
        prompt=ai_cocktail_prompt(
            ingredients=ingredients,
            style=style,
            occasion=occasion,
        ),
        fallback=fallback,
    )


def generate_bartender_tips(
    ingredients: list[str],
    style: str,
    occasion: str,
    recommended_drinks: list[dict[str, Any]],
) -> list[str]:
    fallback = {
        "tips": [
            "Use fresh citrus whenever possible for better aroma and balance.",
            "Chill the glass before serving to keep the drink colder for longer.",
            "Measure ingredients consistently so the cocktail is balanced and repeatable.",
        ]
    }

    result = call_openai_json(
        prompt=bartender_tips_prompt(
            ingredients=ingredients,
            style=style,
            occasion=occasion,
            recommended_drinks=recommended_drinks,
        ),
        fallback=fallback,
    )

    tips = result.get("tips", fallback["tips"])

    if not isinstance(tips, list) or len(tips) < 3:
        return fallback["tips"]

    return tips[:3]


def generate_abinbev_alternative(
    ingredients: list[str],
    country: str,
    brands: list[str],
    style: str,
    occasion: str,
) -> dict[str, Any]:
    default_brand = brands[0] if brands else "Corona"

    fallback = {
        "name": f"{default_brand} Citrus Cooler",
        "brand": default_brand,
        "ingredients": ingredients + [default_brand],
        "instructions": f"Build the ingredients over ice, top gently with {default_brand}, and stir lightly.",
        "reasoning": f"{default_brand} adds carbonation, refreshment and a beer-based twist that works well for the selected occasion.",
    }

    return call_openai_json(
        prompt=abinbev_alternative_prompt(
            ingredients=ingredients,
            country=country,
            brands=brands,
            style=style,
            occasion=occasion,
        ),
        fallback=fallback,
    )
