from wardrobe_data import wardrobe


OCCASION_STYLE_MAP = {
    "Formal Meeting": "Formal",
    "Interview": "Formal",
    "Casual Outing": "Casual",
    "Cafe / Movie": "Casual",
    "Gym": "Sports",
}


ITEM_TYPE_TO_WARDROBE = {
    "tie": ("accessories", "ties"),
    "watch": ("accessories", "watches"),
    "belt": ("accessories", "belts"),
}


AFFILIATE_CATALOG = [
    {
        "item_type": "blazer",
        "styles": ["Formal"],
        "genders": ["Men"],
        "title": "NAVY BLUE BLAZER",
        "platform": "LOUIS PHILIPPE",
        "image_url": "/photos/navy_blue_blazer_men.png",
        "affiliate_url": "https://louisphilippe.abfrl.in/p/men-navy-slim-fit-check-formal-blazer-927139.html?source=plp",
        "color_hint": "Blue",
    },
    {
        "item_type": "cufflinks",
        "styles": ["Formal"],
        "genders": ["Men"],
        "title": "SILVER CUFFLINKS",
        "platform": "REGAL BLUESTONE",
        "image_url": "/photos/silver_cufflinks.png",
        "affiliate_url": "https://www.orionzjewels.com/products/regal-blue-stone-cufflinks?variant=43922842484993",
        "color_hint": "Silver",
    },
    {
        "item_type": "formal_bag",
        "styles": ["Formal"],
        "genders": ["Men"],
        "title": "LEATHER BAG",
        "platform": "MYNTRA",
        "image_url": "/photos/leather_bag_brown.png",
        "affiliate_url": "https://www.myntra.com/laptop-bag/leather+world/leather-world-unisex-brown-14-inch-solid-office-laptop-bag/7744029/buy",
        "color_hint": "Brown",
    },
    {
        "item_type": "blazer",
        "styles": ["Formal"],
        "genders": ["Women"],
        "title": "BLACK BLAZER",
        "platform": "MYNTRA",
        "image_url": "/photos/black_blazer_women.png",
        "affiliate_url": "https://www.myntra.com/blazers/h%26m/hm-collarless-jersey-blazer/39450143/buy",
        "color_hint": "Black",
    },
    {
        "item_type": "formal_bag",
        "styles": ["Formal"],
        "genders": ["Women"],
        "title": "BLACK BAG",
        "platform": "ALLEN SOLLY",
        "image_url": "/photos/black_bag_women.png",
        "affiliate_url": "https://allensolly.abfrl.in/p/women-black-formal-laptop-bag-39736799.html",
        "color_hint": "Black",
    },
    {
        "item_type": "jacket",
        "styles": ["Casual"],
        "genders": ["Men"],
        "title": "CASUAL JACKET",
        "platform": "JACK&JONES",
        "image_url": "/photos/casual_jacket_men_blue.png",
        "affiliate_url": "https://www.jackjones.in/products/900800001-light-blue-denim",
        "color_hint": "Blue",
    },
    {
        "item_type": "jacket",
        "styles": ["Casual"],
        "genders": ["Women"],
        "title": "CASUAL JACKET WOMEN",
        "platform": "MONTE CARLO",
        "image_url": "/photos/casual_jacket_women_black.png",
        "affiliate_url": "https://www.montecarlo.in/products/rockit-women-beige-solid-collar-full-sleeve-jacket-2250104803-2?_pos=1&_fid=acf45b26d&_ss=c",
        "color_hint": "Beige",
    },
    {
        "item_type": "casual_bag",
        "styles": ["Casual"],
        "genders": ["Men"],
        "title": "CASUAL BAG",
        "platform": "MYNTRA",
        "image_url": "/photos/casual_bag_men_black.png",
        "affiliate_url": "https://www.myntra.com/backpacks/provogue/provogue-unisex-black--grey-brand-logo-backpack-with-reflective-strip-31l/16775922/buy",
        "color_hint": "Black",
    },
    {
        "item_type": "sunglasses",
        "styles": ["Casual"],
        "genders": ["Men"],
        "title": "CASUAL MEN SUNGLASSES",
        "platform": "FASTRACK",
        "image_url": "/photos/casual_sunglasses_men_black.png",
        "affiliate_url": "https://www.fastrackeyewear.com/product/black-wayfarer-sunglasses-for-men-and-women-from-fastrack-p515bk3pv",
        "color_hint": "Black",
    },
    {
        "item_type": "casual_bag",
        "styles": ["Casual"],
        "genders": ["Women"],
        "title": "CASUAL BAG WOMEN",
        "platform": "MYNTRA",
        "image_url": "/photos/casual_bag_women_brown.png",
        "affiliate_url": "https://www.myntra.com/handbags/mini+wesst/mini-wesst-women-textured-structured-tote-bag/31918008/buy",
        "color_hint": "Brown",
    },
    {
        "item_type": "sunglasses",
        "styles": ["Casual"],
        "genders": ["Women"],
        "title": "CASUAL SUNGLASSES WOMEN",
        "platform": "LENSKART",
        "image_url": "/photos/casual_sunglasses_women_black.png",
        "affiliate_url": "https://www.lenskart.com/vincent-chase-vc-s14084-c2-c2-sunglasses.html",
        "color_hint": "Black",
    },
    {
        "item_type": "tracksuit",
        "styles": ["Sports"],
        "genders": ["Men"],
        "title": "TRACKSUIT MEN",
        "platform": "DECATHLON",
        "image_url": "/photos/tracksuit_men_grey.png",
        "affiliate_url": "https://www.decathlon.in/p/8841736/men-fitness-tracksuit-jacket-with-moisture-management-fja-100-concrete-grey",
        "color_hint": "Grey",
    },
    {
        "item_type": "gym_bag",
        "styles": ["Sports"],
        "genders": ["Men"],
        "title": "GYM BAG",
        "platform": "FLIPKART",
        "image_url": "/photos/gym_bag_blue.png",
        "affiliate_url": "https://www.flipkart.com/safari-slate-gym-duffel-bag/p/itmee5b974fe8b20?pid=DFBHDFNQGCYYMDHR&lid=LSTDFBHDFNQGCYYMDHRN0NG5L&marketplace=FLIPKART&store=reh%2F4d7%2F6aw&srno=b_1_37&otracker=browse&fm=organic&iid=en_GDAyKKyCYtxtjuPjBPnp_xl0POJFjgQJHSRZ0ufMbvC6UQXQWpqg-1x2sA0vxR7m3wOzEHfCZhXF33ElGynvQwAlvNo-tguW1XjLLiPm_o8%3D&ppt=None&ppn=None&ssid=t2ze8txyls0000001771423727049&ov_redirect=true",
        "color_hint": "Blue",
    },
    {
        "item_type": "shaker_bottle",
        "styles": ["Sports"],
        "genders": ["Men"],
        "title": "MENS SHAKER BOTTLE",
        "platform": "FLIPKART",
        "image_url": "/photos/shaker_men_black.png",
        "affiliate_url": "https://www.flipkart.com/boldfit-water-bottles-sipper-men-women-kids-girls-sports-gym-bottle-1000-ml-shaker/p/itm0109712ba11d7",
        "color_hint": "Black",
    },
    {
        "item_type": "tracksuit",
        "styles": ["Sports"],
        "genders": ["Women"],
        "title": "SPORTS WOMEN TRACKSUIT",
        "platform": "ADIDAS",
        "image_url": "/photos/tracksuit_women_black.png",
        "affiliate_url": "https://www.adidas.co.in/teamgeist-adicolor-oversized-woven-track-top/JY2585.html",
        "color_hint": "Black",
    },
    {
        "item_type": "gym_bag",
        "styles": ["Sports"],
        "genders": ["Women"],
        "title": "SPORTS WOMEN GYM BAG",
        "platform": "MYNTRA",
        "image_url": "/photos/gymbag_women_grey.png",
        "affiliate_url": "https://www.myntra.com/duffel-bag/gear/gear-unisex-shine-on-duffel-bag/22200282/buy",
        "color_hint": "Grey",
    },
    {
        "item_type": "shaker_bottle",
        "styles": ["Sports"],
        "genders": ["Women"],
        "title": "WOMEN SHAKER",
        "platform": "FLIPKART",
        "image_url": "/photos/shaker_women_white.png",
        "affiliate_url": "https://www.flipkart.com/shifter-gym-shaker-stainless-steel-white-bottle-protein-shake-100-leakproof-700-ml/p/itm53a54032ec87e",
        "color_hint": "White",
    },
]


def _wardrobe_has_item(gender, style, item_type):
    map_data = ITEM_TYPE_TO_WARDROBE.get(item_type)
    if not map_data:
        return False
    section, sub_section = map_data
    user_data = wardrobe.get(gender, {})
    if section != "accessories":
        return False
    items = user_data.get("accessories", {}).get(sub_section, [])
    if not items:
        return False
    return any(item.get("style") == style for item in items)


def _get_outfit_colors(outfit):
    colors = set()
    for key in ("top", "bottom", "shoes"):
        item = outfit.get(key) or {}
        color = item.get("color")
        if color:
            colors.add(color)
    return colors


def recommend_affiliate_items(gender, occasion, outfit, limit=6):
    style = OCCASION_STYLE_MAP.get(occasion, "Casual")
    outfit_colors = _get_outfit_colors(outfit or {})
    candidates = []

    for item in AFFILIATE_CATALOG:
        if style not in item["styles"]:
            continue
        if gender not in item["genders"]:
            continue
        if _wardrobe_has_item(gender, style, item["item_type"]):
            continue
        score = 10
        if item.get("color_hint") in outfit_colors:
            score += 4
        candidates.append((score, item))

    candidates.sort(key=lambda x: x[0], reverse=True)

    selected = []
    seen_types = set()

    for _, item in candidates:
        if item["item_type"] in seen_types:
            continue
        selected.append(item)
        seen_types.add(item["item_type"])
        if len(selected) == limit:
            break

    return selected
