# wardrobe_data.py

wardrobe = {

    # ===================== MEN =====================
    "Men": {

        "tops": [
            # Formal
            {"name": "White Formal Shirt", "style": "Formal", "color": "White", "status": "available"},
            {"name": "Light Blue Formal Shirt", "style": "Formal", "color": "Blue", "status": "available"},
            {"name": "Grey Formal Shirt", "style": "Formal", "color": "Grey", "status": "available"},

            # Casual / Outing / Movie
            {"name": "Black Casual T-Shirt", "style": "Casual", "color": "Black", "status": "available"},
            {"name": "Olive Green Casual Shirt", "style": "Casual", "color": "Green", "status": "available"},
            {"name": "White Printed T-Shirt", "style": "Casual", "color": "White", "status": "available"},

            # Gym
            {"name": "Black Gym T-Shirt", "style": "Sports", "color": "Black", "status": "available"},
            {"name": "Grey Sleeveless Gym Tee", "style": "Sports", "color": "Grey", "status": "available"},
        ],

        "bottoms": [
            # Formal
            {"name": "Navy Blue Formal Trousers", "style": "Formal", "color": "Blue", "status": "available"},
            {"name": "Black Formal Trousers", "style": "Formal", "color": "Black", "status": "available"},

            # Casual / Outing
            {"name": "Blue Denim Jeans", "style": "Casual", "color": "Blue", "status": "available"},
            {"name": "Black Slim Fit Jeans", "style": "Casual", "color": "Black", "status": "available"},
            {"name": "Brown Chino Pants", "style": "Casual", "color": "Brown", "status": "available"},

            # Gym
            {"name": "Grey Track Pants", "style": "Sports", "color": "Grey", "status": "available"},
            {"name": "Black Gym Shorts", "style": "Sports", "color": "Black", "status": "available"},
        ],

        "shoes": [
            {"name": "Black Leather Formal Shoes", "style": "Formal", "status": "available"},
            {"name": "Brown Formal Shoes", "style": "Formal", "status": "available"},
            {"name": "White Sneakers", "style": "Casual", "status": "available"},
            {"name": "Black Casual Sneakers", "style": "Casual", "status": "available"},
            {"name": "Running Sports Shoes", "style": "Sports", "status": "available"},
        ],

        "accessories": {
            "watches": [
                {"name": "Silver Analog Watch", "style": "Formal"},
                {"name": "Black Leather Strap Watch", "style": "Formal"},
                {"name": "Digital Sports Watch", "style": "Sports"},
            ],
            "belts": [
                {"name": "Black Leather Belt", "style": "Formal"},
                {"name": "Brown Leather Belt", "style": "Formal"},
            ],
            "ties": [
                {"name": "Navy Blue Silk Tie", "style": "Formal"},
                {"name": "Black Formal Tie", "style": "Formal"},
            ]
        }
    },

    # ===================== WOMEN =====================
    "Women": {

        "tops": [
            # Formal
            {"name": "White Formal Blouse", "style": "Formal", "color": "White", "status": "available"},
            {"name": "Light Blue Office Top", "style": "Formal", "color": "Blue", "status": "available"},

            # Casual / Movie / Outing
            {"name": "Pink Casual Top", "style": "Casual", "color": "Pink", "status": "available"},
            {"name": "Black Casual T-Shirt", "style": "Casual", "color": "Black", "status": "available"},
            {"name": "Floral Summer Top", "style": "Casual", "color": "White", "status": "available"},

            # Gym
            {"name": "Black Gym T-Shirt", "style": "Sports", "color": "Black", "status": "available"},
            {"name": "Grey Workout Tank Top", "style": "Sports", "color": "Grey", "status": "available"},
        ],

        "bottoms": [
            # Formal
            {"name": "Black Formal Pants", "style": "Formal", "color": "Black", "status": "available"},

            # Casual
            {"name": "Blue Denim Jeans", "style": "Casual", "color": "Blue", "status": "available"},
            {"name": "Light Blue Skinny Jeans", "style": "Casual", "color": "Blue", "status": "available"},

            # Gym
            {"name": "Grey Yoga Pants", "style": "Sports", "color": "Grey", "status": "available"},
            {"name": "Black Gym Leggings", "style": "Sports", "color": "Black", "status": "available"},
        ],

        "shoes": [
            {"name": "Black Formal Flats", "style": "Formal", "status": "available"},
            {"name": "Beige Office Sandals", "style": "Formal", "status": "available"},
            {"name": "White Casual Sneakers", "style": "Casual", "status": "available"},
            {"name": "Pink Casual Shoes", "style": "Casual", "status": "available"},
            {"name": "Training Sports Shoes", "style": "Sports", "status": "available"},
        ],

        "accessories": {
            "watches": [
                {"name": "Rose Gold Analog Watch", "style": "Formal"},
                {"name": "Minimal Casual Watch", "style": "Casual"},
                {"name": "Fitness Smart Watch", "style": "Sports"},
            ],
            "belts": [
                {"name": "Slim Black Belt", "style": "Formal"},
                {"name": "Brown Casual Belt", "style": "Casual"},
            ],
            "ties": []  # Not applicable
        }
    }
}
