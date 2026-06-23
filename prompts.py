from __future__ import annotations

import json


def ai_cocktail_prompt(
    ingredients: list[str],
    style: str,
    occasion: str,
) -> str:
    return f"""
You are a professional mixologist.

Create one original cocktail using the available ingredients as much as possible.

Available ingredients:
{", ".join(ingredients)}

Preferred style:
{style}

Occasion:
{occasion}

Return ONLY valid JSON in this exact format:
{{
  "name": "...",
  "ingredients": ["..."],
  "instructions": "...",
  "reasoning": "..."
}}
"""


def bartender_tips_prompt(
    ingredients: list[str],
    style: str,
    occasion: str,
    recommended_drinks: list[dict],
) -> str:
    drinks_summary = [
        {
            "name": drink.get("name"),
            "ingredients": drink.get("ingredients"),
            "style": drink.get("style"),
        }
        for drink in recommended_drinks
    ]

    return f"""
You are a senior bartender.

Based on the user's ingredients, style, occasion, and recommendations, provide exactly 3 concise improvement suggestions.

Available ingredients:
{", ".join(ingredients)}

Style:
{style}

Occasion:
{occasion}

Recommended drinks:
{json.dumps(drinks_summary, ensure_ascii=False)}

Return ONLY valid JSON:
{{
  "tips": [
    "...",
    "...",
    "..."
  ]
}}
"""


def abinbev_alternative_prompt(
    ingredients: list[str],
    country: str,
    brands: list[str],
    style: str,
    occasion: str,
) -> str:
    return f"""
You are a professional mixologist creating a beer-based cocktail variation.

Country:
{country}

Available AB InBev brands for this country:
{", ".join(brands)}

Available ingredients:
{", ".join(ingredients)}

Preferred style:
{style}

Occasion:
{occasion}

Create one AB InBev beer-based alternative using exactly ONE brand from the list above.

Return ONLY valid JSON in this exact format:
{{
  "name": "...",
  "brand": "...",
  "ingredients": ["..."],
  "instructions": "...",
  "reasoning": "..."
}}
"""
