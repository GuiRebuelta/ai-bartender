import os
import json
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
from openai import OpenAI


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Bartender",
    page_icon="🍸",
    layout="wide",
)

COCKTAIL_DB_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1"


# -----------------------------------------------------------------------------
# API Clients
# -----------------------------------------------------------------------------

def get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def normalize_ingredient(text: str) -> str:
    return text.strip().lower()


def parse_ingredients(raw_input: str) -> List[str]:
    ingredients = [
        normalize_ingredient(item)
        for item in raw_input.split(",")
        if item.strip()
    ]
    return list(dict.fromkeys(ingredients))


def safe_get(url: str, timeout: int = 10) -> Optional[Dict]:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


# -----------------------------------------------------------------------------
# CocktailDB Integration
# -----------------------------------------------------------------------------

def get_cocktails_by_ingredient(ingredient: str) -> List[Dict]:
    url = (
        f"{COCKTAIL_DB_BASE_URL}/filter.php"
        f"?i={requests.utils.quote(ingredient)}"
    )

    data = safe_get(url)

    if not data or not data.get("drinks"):
        return []

    return data["drinks"]


def get_cocktail_details(cocktail_id: str) -> Optional[Dict]:
    url = f"{COCKTAIL_DB_BASE_URL}/lookup.php?i={cocktail_id}"

    data = safe_get(url)

    if not data or not data.get("drinks"):
        return None

    return data["drinks"][0]


def extract_cocktail_ingredients(drink: Dict) -> List[str]:
    ingredients = []

    for i in range(1, 16):
        ingredient = drink.get(f"strIngredient{i}")
        if ingredient:
            ingredients.append(ingredient.strip().lower())

    return ingredients


def calculate_match_score(
    user_ingredients: List[str],
    cocktail_ingredients: List[str],
) -> float:
    if not user_ingredients:
        return 0.0

    matches = 0

    for user_ing in user_ingredients:
        for cocktail_ing in cocktail_ingredients:
            if (
                user_ing in cocktail_ing
                or cocktail_ing in user_ing
            ):
                matches += 1
                break

    return round((matches / len(user_ingredients)) * 100, 1)


def find_best_cocktail_match(
    user_ingredients: List[str]
) -> Tuple[Optional[Dict], float]:
    candidate_ids = {}

    for ingredient in user_ingredients:
        cocktails = get_cocktails_by_ingredient(ingredient)

        for cocktail in cocktails:
            candidate_ids[cocktail["idDrink"]] = cocktail

    if not candidate_ids:
        return None, 0.0

    best_drink = None
    best_score = 0.0

    for cocktail_id in candidate_ids.keys():
        details = get_cocktail_details(cocktail_id)

        if not details:
            continue

        cocktail_ingredients = extract_cocktail_ingredients(details)

        score = calculate_match_score(
            user_ingredients,
            cocktail_ingredients,
        )

        if score > best_score:
            best_score = score
            best_drink = details

    return best_drink, best_score


# -----------------------------------------------------------------------------
# OpenAI Generation
# -----------------------------------------------------------------------------

def generate_ai_cocktail(
    ingredients: List[str]
) -> Dict:
    client = get_openai_client()

    fallback = {
        "drink_name": "Improvised House Cocktail",
        "ingredients": ingredients,
        "instructions": (
            "Combine all suitable ingredients over ice, stir or shake "
            "depending on texture, strain into a chilled glass, and garnish "
            "with any available citrus."
        ),
        "improvements": [
            "Add citrus for balance.",
            "Control dilution with proper ice.",
            "Use fresh ingredients whenever possible.",
        ],
        "ab_inbev": {
            "drink_name": "Corona Citrus Twist",
            "ingredients": ingredients + ["Corona"],
            "instructions": (
                "Build over ice and top with Corona. Stir gently."
            ),
            "reasoning": (
                "Corona contributes light malt notes and refreshing carbonation."
            ),
        },
    }

    if client is None:
        return fallback

    prompt = f"""
You are a world-class mixologist.

Available ingredients:
{", ".join(ingredients)}

Return ONLY valid JSON with this schema:

{{
  "drink_name": "...",
  "ingredients": ["..."],
  "instructions": "...",
  "improvements": [
    "...",
    "...",
    "..."
  ],
  "ab_inbev": {{
    "drink_name": "...",
    "ingredients": ["..."],
    "instructions": "...",
    "reasoning": "..."
  }}
}}

Rules:
- Create a realistic cocktail.
- Use the provided ingredients whenever possible.
- Always provide exactly 3 improvement suggestions.
- AB InBev variation must use exactly ONE brand:
  Budweiser, Corona, Stella Artois, or Beck's.
- Response must be valid JSON only.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        content = response.output_text.strip()

        return json.loads(content)

    except Exception:
        return fallback


def generate_classic_enhancements(
    cocktail: Dict,
    user_ingredients: List[str]
) -> Dict:
    client = get_openai_client()

    fallback = {
        "improvements": [
            "Use fresh citrus juice.",
            "Chill the serving glass before pouring.",
            "Measure ingredients precisely for consistency.",
        ],
        "ab_inbev": {
            "drink_name": f"{cocktail['strDrink']} Beer Twist",
            "ingredients": [
                cocktail["strDrink"],
                "Corona",
            ],
            "instructions": (
                "Prepare the original cocktail and finish with a splash "
                "of Corona."
            ),
            "reasoning": (
                "Corona adds refreshing carbonation and subtle malt character."
            ),
        },
    }

    if client is None:
        return fallback

    prompt = f"""
You are an expert mixologist.

Classic cocktail:
{cocktail['strDrink']}

Ingredients supplied by user:
{", ".join(user_ingredients)}

Return ONLY valid JSON:

{{
  "improvements": [
    "...",
    "...",
    "..."
  ],
  "ab_inbev": {{
    "drink_name": "...",
    "ingredients": ["..."],
    "instructions": "...",
    "reasoning": "..."
  }}
}}

Requirements:
- Exactly 3 improvement suggestions.
- AB InBev variation must use ONE of:
  Budweiser, Corona, Stella Artois, Beck's.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return json.loads(response.output_text)

    except Exception:
        return fallback


# -----------------------------------------------------------------------------
# UI Components
# -----------------------------------------------------------------------------

def render_recommended_drink(
    title: str,
    ingredients: List[str],
    instructions: str,
    image_url: Optional[str] = None,
):
    st.subheader("🍸 Recommended Drink")

    with st.container(border=True):
        st.success(title)

        if image_url:
            st.image(image_url, use_container_width=True)

        st.markdown("**Ingredients**")
        for item in ingredients:
            st.write(f"• {item}")

        st.markdown("**Instructions**")
        st.write(instructions)


def render_improvements(items: List[str]):
    st.subheader("✨ Improvement Suggestions")

    with st.container(border=True):
        st.info("Professional Mixology Recommendations")

        for item in items[:3]:
            st.write(f"• {item}")


def render_ab_inbev(alternative: Dict):
    st.subheader("🍺 AB InBev Alternative")

    with st.container(border=True):
        st.warning(alternative.get("drink_name", "AB InBev Variation"))

        st.markdown("**Ingredients**")
        for ingredient in alternative.get("ingredients", []):
            st.write(f"• {ingredient}")

        st.markdown("**Instructions**")
        st.write(alternative.get("instructions", ""))

        st.markdown("**Why this brand works**")
        st.write(alternative.get("reasoning", ""))


# -----------------------------------------------------------------------------
# Main App
# -----------------------------------------------------------------------------

st.title("🍸 AI Bartender")
st.caption(
    "Enter your ingredients and get a classic cocktail recommendation "
    "or an AI-generated creation."
)

ingredients_input = st.text_input(
    "Ingredients (comma-separated)",
    placeholder="vodka, lime, sugar",
)

generate = st.button(
    "Recommend a Drink",
    type="primary",
    use_container_width=True,
)

if generate:

    ingredients = parse_ingredients(ingredients_input)

    if not ingredients:
        st.error("Please provide at least one ingredient.")
        st.stop()

    with st.spinner("Creating your recommendation..."):

        cocktail, score = find_best_cocktail_match(ingredients)

        is_classic = cocktail is not None and score > 60

        if is_classic:

            enhancements = generate_classic_enhancements(
                cocktail,
                ingredients,
            )

            recommendation_type = "Classic"

            cocktail_ingredients = []

            for i in range(1, 16):
                ingredient = cocktail.get(f"strIngredient{i}")
                measure = cocktail.get(f"strMeasure{i}")

                if ingredient:
                    text = ingredient
                    if measure:
                        text = f"{measure.strip()} {ingredient}"
                    cocktail_ingredients.append(text)

            recommendation = {
                "name": cocktail["strDrink"],
                "ingredients": cocktail_ingredients,
                "instructions": cocktail.get(
                    "strInstructions",
                    "No instructions available."
                ),
                "image": cocktail.get("strDrinkThumb"),
                "improvements": enhancements["improvements"],
                "ab_inbev": enhancements["ab_inbev"],
            }

        else:

            ai_result = generate_ai_cocktail(ingredients)

            recommendation_type = "AI-generated"

            recommendation = {
                "name": ai_result["drink_name"],
                "ingredients": ai_result["ingredients"],
                "instructions": ai_result["instructions"],
                "image": None,
                "improvements": ai_result["improvements"],
                "ab_inbev": ai_result["ab_inbev"],
            }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Number of Ingredients",
            len(ingredients),
        )

    with col2:
        st.metric(
            "Match Score (%)",
            f"{score:.1f}",
        )

    with col3:
        st.metric(
            "Recommendation Type",
            recommendation_type,
        )

    st.divider()

    render_recommended_drink(
        title=recommendation["name"],
        ingredients=recommendation["ingredients"],
        instructions=recommendation["instructions"],
        image_url=recommendation["image"],
    )

    st.markdown("")

    render_improvements(
        recommendation["improvements"],
    )

    st.markdown("")

    render_ab_inbev(
        recommendation["ab_inbev"],
    )
