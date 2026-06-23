from __future__ import annotations

from typing import Any

import requests


BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1"


def safe_get_json(url: str, timeout: int = 8) -> dict[str, Any] | None:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def search_by_ingredient(ingredient: str) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/filter.php?i={requests.utils.quote(ingredient)}"
    data = safe_get_json(url)

    if not data or not data.get("drinks"):
        return []

    return data["drinks"]


def lookup_cocktail(cocktail_id: str) -> dict[str, Any] | None:
    url = f"{BASE_URL}/lookup.php?i={cocktail_id}"
    data = safe_get_json(url)

    if not data or not data.get("drinks"):
        return None

    return data["drinks"][0]


def extract_ingredients(drink: dict[str, Any]) -> list[str]:
    ingredients = []

    for i in range(1, 16):
        ingredient = drink.get(f"strIngredient{i}")
        if ingredient:
            ingredients.append(ingredient.strip().lower())

    return ingredients


def fetch_cocktaildb_candidates(
    ingredients: list[str],
    max_candidates: int = 20,
) -> list[dict[str, Any]]:
    cocktail_ids = {}

    for ingredient in ingredients:
        for item in search_by_ingredient(ingredient):
            cocktail_ids[item["idDrink"]] = item

    candidates = []

    for cocktail_id in list(cocktail_ids.keys())[:max_candidates]:
        details = lookup_cocktail(cocktail_id)

        if not details:
            continue

        candidates.append(
            {
                "name": details.get("strDrink", "Unknown Cocktail"),
                "ingredients": extract_ingredients(details),
                "instructions": details.get("strInstructions") or "No instructions available.",
                "style": "Surprise Me",
                "flavor_profile": [],
                "occasions": ["Casual Night"],
                "popularity": 6,
                "strength": "Medium",
                "glass": details.get("strGlass") or "Glass",
                "difficulty": "Medium",
                "prep_time": "4 minutes",
                "source": "TheCocktailDB",
            }
        )

    return candidates
