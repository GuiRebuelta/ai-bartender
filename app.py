from __future__ import annotations

from typing import Any

import streamlit as st

from abinbev_portfolio import get_countries
from cocktail_engine import build_recommendations
from utils import format_score, parse_ingredients, quality_label


STYLES = [
    "Refreshing",
    "Strong",
    "Sweet",
    "Citrusy",
    "Bitter",
    "Tropical",
    "Surprise Me",
]

OCCASIONS = [
    "Casual Night",
    "BBQ",
    "Beach Day",
    "Dinner Party",
    "Date Night",
    "Celebration",
    "Watching Sports",
    "Brunch",
    "Surprise Me",
]


st.set_page_config(
    page_title="AI Bartender",
    page_icon="🍸",
    layout="wide",
)

st.title("🍸 AI Bartender")
st.caption("Find classic cocktails, AI creations, and AB InBev beer-based alternatives.")

with st.sidebar:
    st.header("Your Preferences")

    country = st.selectbox(
        "Country",
        get_countries(),
        index=get_countries().index("Brazil") if "Brazil" in get_countries() else 0,
    )

    occasion = st.selectbox(
        "Occasion",
        OCCASIONS,
        index=0,
    )

    style = st.selectbox(
        "Drink Style",
        STYLES,
        index=0,
    )

ingredients_input = st.text_input(
    "Available ingredients",
    placeholder="vodka, lime, sugar",
)

generate = st.button(
    "Find My Cocktail",
    type="primary",
    use_container_width=True,
)


def render_drink_card(title: str, drink: dict[str, Any], rank_label: str | None = None) -> None:
    score = drink.get("match_score")

    with st.container(border=True):
        if rank_label:
            st.markdown(f"### {rank_label}")

        if score is not None:
            st.success(f"{drink.get('name', 'Cocktail')} — {format_score(score)} · {quality_label(score)} Match")
            st.progress(min(float(score) / 100, 1.0))
        else:
            st.info(drink.get("name", "Cocktail"))

        cols = st.columns(4)
        cols[0].metric("Style", drink.get("style", "N/A"))
        cols[1].metric("Strength", drink.get("strength", "N/A"))
        cols[2].metric("Difficulty", drink.get("difficulty", "N/A"))
        cols[3].metric("Prep Time", drink.get("prep_time", "N/A"))

        st.markdown("**Ingredients**")
        for ingredient in drink.get("ingredients", []):
            st.write(f"• {ingredient}")

        st.markdown("**Instructions**")
        st.write(drink.get("instructions", "No instructions available."))


def render_ai_cocktail(drink: dict[str, Any]) -> None:
    with st.container(border=True):
        st.info(f"🤖 {drink.get('name', 'AI Signature Cocktail')}")

        st.markdown("**Ingredients**")
        for ingredient in drink.get("ingredients", []):
            st.write(f"• {ingredient}")

        st.markdown("**Instructions**")
        st.write(drink.get("instructions", ""))

        st.markdown("**Why it works**")
        st.write(drink.get("reasoning", ""))


def render_abinbev_card(alternative: dict[str, Any], country: str) -> None:
    with st.container(border=True):
        st.warning(f"🍺 {alternative.get('name', 'AB InBev Alternative')}")

        st.markdown(f"**Country:** {country}")
        st.markdown(f"**Brand used:** {alternative.get('brand', 'N/A')}")

        st.markdown("**Ingredients**")
        for ingredient in alternative.get("ingredients", []):
            st.write(f"• {ingredient}")

        st.markdown("**Instructions**")
        st.write(alternative.get("instructions", ""))

        st.markdown("**Why this brand works**")
        st.write(alternative.get("reasoning", ""))


if generate:
    ingredients = parse_ingredients(ingredients_input)

    if not ingredients:
        st.error("Please enter at least one ingredient.")
        st.stop()

    with st.spinner("Searching classic cocktails, checking databases, and asking the AI mixologist..."):
        result = build_recommendations(
            ingredients=ingredients,
            country=country,
            style=style,
            occasion=occasion,
        )

    top_recommendations = result["top_recommendations"]
    best_score = top_recommendations[0]["match_score"] if top_recommendations else 0

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Ingredients", len(ingredients))
    metric_2.metric("Best Match", format_score(best_score))
    metric_3.metric("Cocktails Found", result["candidate_count"])
    metric_4.metric("Country", country)

    st.divider()

    st.subheader("🏆 Top Classic Recommendations")

    if top_recommendations:
        render_drink_card("Best Match", top_recommendations[0], "Best Match")

    if len(top_recommendations) > 1:
        render_drink_card("Alternative", top_recommendations[1], "Alternative Recommendation")

    st.subheader("🤖 AI Signature Cocktail")
    render_ai_cocktail(result["ai_cocktail"])

    st.subheader("✨ Improvement Suggestions")
    with st.container(border=True):
        for tip in result["tips"]:
            st.write(f"• {tip}")

    st.subheader("🍺 AB InBev Alternative")
    render_abinbev_card(result["abinbev_alternative"], country)
else:
    st.info("Select your country, occasion, style, and ingredients to get started.")
