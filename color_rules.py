COLOR_COMPATIBILITY = {
    "Blue": ["White", "Brown", "Black", "Grey"],
    "Black": ["White", "Grey", "Blue"],
    "Brown": ["White", "Blue", "Beige", "Grey"],
    "White": ["Blue", "Black", "Brown", "Grey", "Pink", "Green"],
    "Grey": ["White", "Black", "Blue"],
    "Green": ["White", "Black", "Grey"],
    "Pink": ["White", "Black", "Grey"],
    "Beige": ["White", "Brown", "Black"],
}

def is_color_compatible(top_color, bottom_color):
    return bottom_color in COLOR_COMPATIBILITY.get(top_color, [])
