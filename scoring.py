from __future__ import annotations

from typing import Any

from utils import clamp, normalize_text


INGREDIENT_WEIGHT = 45
POPULARITY_WEIGHT = 20
STYLE_WEIGHT = 15
OCCASION_WEIGHT = 10
SIMPLICITY_WEIGHT = 10


INGREDIENT_ALIASES = {
    "cachaça": ["cachaca"],
    "cachaca": ["cachaça"],
    "lime juice": ["lime"],
    "lemon juice": ["lemon"],
    "simple syrup": ["sugar", "syrup"],
    "soda": ["soda water", "club soda", "sparkling water"],
    "club soda": ["soda water", "soda", "sparkling water"],
    "orange liqueur": ["triple sec", "cointreau", "curacao"],
    "triple sec": ["orange liqueur", "cointreau", "curacao"],
    "bourbon": ["whiskey", "whisky"],
    "whiskey": ["bourbon", "rye", "whisky"],
    "whisky": ["whiskey", "scotch"],
    "rum": ["white rum", "dark rum", "gold rum"],
    "white rum": ["rum"],
    "dark rum": ["rum"],
    "gin": ["dry gin", "london dry gin"],
    "tequila": ["blanco tequila", "silver tequila"],
}


def expand_ingredient(ingredient: str) -> set[str]:
    normalized = normalize_text(ingredient)
    expanded = {normalized}

    for alias, equivalents in INGREDIENT_ALIASES.items():
        alias_norm = normalize_text(alias)

        if normalized == alias_norm or normalized in alias_norm or alias_norm in normalized:
            expanded.update(normalize_text(item) for item in equivalents)

    return expanded


def ingredient_matches(user_ingredient: str, cocktail_ingredient: str) -> bool:
    user_terms = expand_ingredient(user_ingredient)
    cocktail_terms = expand_ingredient(cocktail_ingredient)

    for user_term in user_terms:
        for cocktail_term in cocktail_terms:
            if (
                user_term == cocktail_term
                or user_term in cocktail_term
                or cocktail_term in user_term
            ):
                return True

    return False


def calculate_ingredient_score(
    user_ingredients: list[str],
    cocktail_ingredients: list[str],
) -> float:
    if not user_ingredients or not cocktail_ingredients:
        return 0.0

    matched = 0

    for user_ingredient in user_ingredients:
        if any(
            ingredient_matches(user_ingredient, cocktail_ingredient)
            for cocktail_ingredient in cocktail_ingredients
        ):
            matched += 1

    user_match_ratio = matched / len(user_ingredients)

    required_matched = 0

    for cocktail_ingredient in cocktail_ingredients:
        if any(
            ingredient_matches(user_ingredient, cocktail_ingredient)
            for user_ingredient in user_ingredients
        ):
            required_matched += 1

    recipe_match_ratio = required_matched / len(cocktail_ingredients)

    return clamp((user_match_ratio * 0.55 + recipe_match_ratio * 0.45) * 100)


def calculate_style_score(selected_style: str, cocktail: dict[str, Any]) -> float:
    if not selected_style or selected_style == "Surprise Me":
        return 75.0

    selected = normalize_text(selected_style)
    cocktail_style = normalize_text(str(cocktail.get("style", "")))
    flavor_profile = [
        normalize_text(item)
        for item in cocktail.get("flavor_profile", [])
    ]

    if selected == cocktail_style:
        return 100.0

    if selected in flavor_profile:
        return 90.0

    if selected in cocktail_style or cocktail_style in selected:
        return 85.0

    return 45.0


def calculate_occasion_score(selected_occasion: str, cocktail: dict[str, Any]) -> float:
    if not selected_occasion or selected_occasion == "Surprise Me":
        return 75.0

    selected = normalize_text(selected_occasion)
    occasions = [
        normalize_text(item)
        for item in cocktail.get("occasions", [])
    ]

    if selected in occasions:
        return 100.0

    return 50.0


def calculate_simplicity_score(
    user_ingredients: list[str],
    cocktail_ingredients: list[str],
) -> float:
    if not cocktail_ingredients:
        return 0.0

    missing = 0

    for cocktail_ingredient in cocktail_ingredients:
        if not any(
            ingredient_matches(user_ingredient, cocktail_ingredient)
            for user_ingredient in user_ingredients
        ):
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


def calculate_total_score(
    cocktail: dict[str, Any],
    user_ingredients: list[str],
    selected_style: str,
    selected_occasion: str,
) -> dict[str, float]:
    cocktail_ingredients = cocktail.get("ingredients", [])

    ingredient_score = calculate_ingredient_score(
        user_ingredients=user_ingredients,
        cocktail_ingredients=cocktail_ingredients,
    )

    popularity_score = clamp(float(cocktail.get("popularity", 5)) * 10)

    style_score = calculate_style_score(
        selected_style=selected_style,
        cocktail=cocktail,
    )

    occasion_score = calculate_occasion_score(
        selected_occasion=selected_occasion,
        cocktail=cocktail,
    )

    simplicity_score = calculate_simplicity_score(
        user_ingredients=user_ingredients,
        cocktail_ingredients=cocktail_ingredients,
    )

    total = (
        ingredient_score * INGREDIENT_WEIGHT
        + popularity_score * POPULARITY_WEIGHT
        + style_score * STYLE_WEIGHT
        + occasion_score * OCCASION_WEIGHT
        + simplicity_score * SIMPLICITY_WEIGHT
    ) / 100

    return {
        "total_score": clamp(total),
        "ingredient_score": clamp(ingredient_score),
        "popularity_score": clamp(popularity_score),
        "style_score": clamp(style_score),
        "occasion_score": clamp(occasion_score),
        "simplicity_score": clamp(simplicity_score),
    }


def score_cocktails(
    cocktails: list[dict[str, Any]],
    user_ingredients: list[str],
    selected_style: str,
    selected_occasion: str,
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []

    for cocktail in cocktails:
        scores = calculate_total_score(
            cocktail=cocktail,
            user_ingredients=user_ingredients,
            selected_style=selected_style,
            selected_occasion=selected_occasion,
        )

        scored.append({
            **cocktail,
            "scores": scores,
            "match_score": scores["total_score"],
        })

    return sorted(
        scored,
        key=lambda item: item["match_score"],
        reverse=True,
    )
