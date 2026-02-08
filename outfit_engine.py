# outfit_engine.py

from wardrobe_data import wardrobe
from color_rules import is_color_compatible


def get_items(items, styles):
    return [
        item for item in items
        if item["status"] == "available" and item["style"] in styles
    ]


def recommend_outfits(gender, occasion):
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

    for top in tops:
        for bottom in bottoms:
            if is_color_compatible(top["color"], bottom["color"]):
                outfits.append({
                    "top": top,
                    "bottom": bottom,
                    "shoes": shoes[0] if shoes else None,
                    "accessories": user_wardrobe["accessories"]
                })

    return outfits
