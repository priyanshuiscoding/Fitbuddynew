# outfit_engine.py

import re

from wardrobe_data import wardrobe
from color_rules import is_color_compatible


def get_items(items, styles):
    return [
        item for item in items
        if item["status"] == "available" and item["style"] in styles
    ]


TOP_KEYWORDS = ("shirt", "t-shirt", "tee", "top", "blouse", "tank")
BOTTOM_KEYWORDS = ("trouser", "trousers", "pants", "jeans", "chino", "shorts", "leggings")
SHOES_KEYWORDS = ("shoe", "shoes", "sneaker", "sneakers", "flats", "sandals")
COLOR_ALIASES = {
    "black": "Black",
    "blue": "Blue",
    "brown": "Brown",
    "green": "Green",
    "grey": "Grey",
    "gray": "Grey",
    "pink": "Pink",
    "white": "White",
    "beige": "Beige",
}

ITEM_KEYWORDS = {
    "top_colors": TOP_KEYWORDS + ("tshirt",),
    "bottom_colors": BOTTOM_KEYWORDS + ("pant",),
    "shoes_colors": SHOES_KEYWORDS + ("footwear", "loafer", "loafers", "boot", "boots"),
}

KEYWORD_TO_PREF = {}
for pref_key, keywords in ITEM_KEYWORDS.items():
    for keyword in keywords:
        KEYWORD_TO_PREF[keyword] = pref_key


def infer_item_color(item):
    if item.get("color"):
        return item["color"]
    name = item.get("name", "").lower()
    for alias, color in COLOR_ALIASES.items():
        if alias in name:
            return color
    return None


def parse_user_preferences(user_input):
    text = (user_input or "").lower()
    if not text.strip():
        return {}

    preferences = {
        "top_colors": set(),
        "bottom_colors": set(),
        "shoes_colors": set(),
    }
    compact_text = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text)).strip()
    if compact_text:
        all_keywords = sorted(KEYWORD_TO_PREF.keys(), key=len, reverse=True)
        keyword_pattern = "|".join(re.escape(k) for k in all_keywords)
        color_pattern = "|".join(re.escape(c) for c in COLOR_ALIASES.keys())

        color_then_item = re.compile(
            rf"\b(?P<color>{color_pattern})\b(?:\s+\w+){{0,1}}\s+\b(?P<item>{keyword_pattern})\b"
        )
        item_then_color = re.compile(
            rf"\b(?P<item>{keyword_pattern})\b(?:\s+\w+){{0,1}}\s+\b(?P<color>{color_pattern})\b(?!\s+(?:{keyword_pattern})\b)"
        )

        for match in color_then_item.finditer(compact_text):
            pref_key = KEYWORD_TO_PREF[match.group("item")]
            preferences[pref_key].add(COLOR_ALIASES[match.group("color")])

        for match in item_then_color.finditer(compact_text):
            pref_key = KEYWORD_TO_PREF[match.group("item")]
            preferences[pref_key].add(COLOR_ALIASES[match.group("color")])

    return preferences


def filter_by_color(items, allowed_colors):
    if not allowed_colors:
        return items
    return [item for item in items if infer_item_color(item) in allowed_colors]


def recommend_outfits(gender, occasion, user_input=None):
    outfits = []

    occasion_style_map = {
        "Formal Meeting": ["Formal"],
        "Interview": ["Formal"],
        "Casual Outing": ["Casual"],
        "Cafe / Movie": ["Casual"],
        "Gym": ["Sports"]
    }

    allowed_styles = occasion_style_map.get(occasion, ["Casual"])

    user_wardrobe = wardrobe[gender]

    tops = get_items(user_wardrobe["tops"], allowed_styles)
    bottoms = get_items(user_wardrobe["bottoms"], allowed_styles)
    shoes = get_items(user_wardrobe["shoes"], allowed_styles)
    preferences = parse_user_preferences(user_input)

    tops = filter_by_color(tops, preferences.get("top_colors"))
    bottoms = filter_by_color(bottoms, preferences.get("bottom_colors"))
    shoes = filter_by_color(shoes, preferences.get("shoes_colors"))

    if preferences.get("shoes_colors") and not shoes:
        return outfits

    shoe_options = shoes if shoes else [None]

    for top in tops:
        for bottom in bottoms:
            if not is_color_compatible(top["color"], bottom["color"]):
                continue
            for shoe in shoe_options:
                outfits.append({
                    "top": top,
                    "bottom": bottom,
                    "shoes": shoe,
                    "accessories": user_wardrobe["accessories"]
                })

    return outfits
