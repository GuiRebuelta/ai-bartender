from __future__ import annotations

from typing import Any

from ai_generator import (
    generate_abinbev_alternative,
    generate_ai_cocktail,
    generate_bartender_tips,
)
from abinbev_portfolio import get_brands_for_country
from cocktaildb import fetch_cocktaildb_candidates
from cocktails import get_cocktails
from scoring import score_cocktails
from utils import deduplicate_by_name


def build_recommendations(
    ingredients: list[str],
    country: str,
    style: str,
    occasion: str,
) -> dict[str, Any]:
    local_candidates = get_cocktails()

    try:
        api_candidates = fetch_cocktaildb_candidates(ingredients)
    except Exception:
        api_candidates = []

    all_candidates = deduplicate_by_name(local_candidates + api_candidates)

    scored_candidates = score_cocktails(
        cocktails=all_candidates,
        user_ingredients=ingredients,
        selected_style=style,
        selected_occasion=occasion,
    )

    top_recommendations = scored_candidates[:2]

    ai_cocktail = generate_ai_cocktail(
        ingredients=ingredients,
        style=style,
        occasion=occasion,
    )

    tips = generate_bartender_tips(
        ingredients=ingredients,
        style=style,
        occasion=occasion,
        recommended_drinks=top_recommendations,
    )

    brands = get_brands_for_country(country)

    abinbev_alternative = generate_abinbev_alternative(
        ingredients=ingredients,
        country=country,
        brands=brands,
        style=style,
        occasion=occasion,
    )

    return {
        "top_recommendations": top_recommendations,
        "ai_cocktail": ai_cocktail,
        "tips": tips,
        "abinbev_alternative": abinbev_alternative,
        "candidate_count": len(scored_candidates),
        "brands": brands,
    }
