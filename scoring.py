from __future__ import annotations

from typing import Any

from utils import clamp, normalize_text


ALIASES = {
    "lime juice": ["lime"],
    "lemon juice": ["lemon"],
    "simple syrup": ["sugar", "syrup"],
    "orange liqueur": ["triple sec", "cointreau", "curacao"],
    "triple sec": ["orange liqueur", "cointreau"],
    "cachaca": ["cachaça"],
    "bourbon": ["whiskey", "whisky"],
    "rye whiskey": ["whiskey", "whisky"],
    "white rum": ["rum"],
    "dark rum": ["rum"],
    "soda water": ["club soda", "sparkling water", "soda"],
}


def expand(value: str) -> set[str]:
    normalized = normalize_text(value)
    values = {normalized}

    for key, aliases in ALIASES.items():
        key_norm = normalize_text(key)
        if normalized == key_norm or normalized in key_norm or key_norm in normalized:
            values.update(normalize_text(item) for item in aliases)

    return values


def ingredient_match(user_ingredient: str, recipe_ingredient: str) -> bool:
    user_values = expand(user_ingredient)
    recipe_values = expand(recipe_ingredient)

    for user_value in user_values:
        for recipe_value in recipe_values:
            if (
                user_value == recipe_value
                or user_value in recipe_value
                or recipe_value in user_value
            ):
                return True

    return False


def ingredient_score(user_ingredients: list[str], recipe_ingredients: list[str]) -> float:
    if not user_ingredients or not recipe_ingredients:
        return 0.0

    matched_user = sum(
        1
        for user_ingredient in user_ingredients
        if any(ingredient_match(user_ingredient, recipe_ingredient) for recipe_ingredient in recipe_ingredients)
    )

    matched_recipe = sum(
        1
        for recipe_ingredient in recipe_ingredients
        if any(ingredient_match(user_ingredient, recipe_ingredient) for user_ingredient in user_ingredients)
    )

    user_ratio = matched_user / len(user_ingredients)
    recipe_ratio = matched_recipe / len(recipe_ingredients)

    return clamp((user_ratio * 0.55 + recipe_ratio * 0.45) * 100)


def style_score(selected_style: str, cocktail: dict[str, Any]) -> float:
    if selected_style == "Surprise Me":
        return 75.0

    selected = normalize_text(selected_style)
    style = normalize_text(str(cocktail.get("style", "")))
    flavors = [normalize_text(item) for item in cocktail.get("flavor_profile", [])]

    if selected == style:
        return 100.0

    if selected in flavors:
        return 90.0

    return 45.0


def occasion_score(selected_occasion: str, cocktail: dict[str, Any]) -> float:
    if selected_occasion == "Surprise Me":
        return 75.0

    selected = normalize_text(selected_occasion)
    occasions = [normalize_text(item) for item in cocktail.get("occasions", [])]

    return 100.0 if selected in occasions else 50.0


def simplicity_score(user_ingredients: list[str], recipe_ingredients: list[str]) -> float:
    missing = 0

    for recipe_ingredient in recipe_ingredients:
        if not any(ingredient_match(user_ingredient, recipe_ingredient) for user_ingredient in user_ingredients):
            missing += 1

    if missing == 0:
        return 100.0
    if missing == 1:
        return 85.0
    if missing == 2:
        return 65.0
    if missing == 3:
        return 40.0

    return 20.0


def score_cocktail(
    cocktail: dict[str, Any],
    user_ingredients: list[str],
    selected_style: str,
    selected_occasion: str,
) -> dict[str, Any]:
    recipe_ingredients = cocktail.get("ingredients", [])

    ingredient = ingredient_score(user_ingredients, recipe_ingredients)
    popularity = clamp(float(cocktail.get("popularity", 5)) * 10)
    style = style_score(selected_style, cocktail)
    occasion = occasion_score(selected_occasion, cocktail)
    simplicity = simplicity_score(user_ingredients, recipe_ingredients)

    total = (
        ingredient * 0.45
        + popularity * 0.20
        + style * 0.15
        + occasion * 0.10
        + simplicity * 0.10
    )

    return {
        **cocktail,
        "match_score": clamp(total),
        "score_details": {
            "ingredient": ingredient,
            "popularity": popularity,
            "style": style,
            "occasion": occasion,
            "simplicity": simplicity,
        },
    }


def score_cocktails(
    cocktails: list[dict[str, Any]],
    user_ingredients: list[str],
    selected_style: str,
    selected_occasion: str,
) -> list[dict[str, Any]]:
    scored = [
        score_cocktail(
            cocktail=cocktail,
            user_ingredients=user_ingredients,
            selected_style=selected_style,
            selected_occasion=selected_occasion,
        )
        for cocktail in cocktails
    ]

    return sorted(scored, key=lambda item: item["match_score"], reverse=True)
