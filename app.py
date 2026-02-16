# FitBuddy — Flask backend
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from wardrobe_data import wardrobe
from outfit_engine import recommend_outfits
from prompt_builder import build_outfit_prompt
from image_generator import generate_outfit_image, image_bytes_to_base64

# Load .env from the folder where this file lives (so it works from any cwd)
_app_dir = Path(__file__).resolve().parent
load_dotenv(_app_dir / ".env")
load_dotenv(_app_dir / ".env.txt")  # fallback if you saved as .env.txt

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/wardrobe/<gender>")
def api_wardrobe(gender):
    if gender not in wardrobe:
        return jsonify({"error": "Invalid gender"}), 400
    return jsonify(wardrobe[gender])


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json() or {}
    gender = data.get("gender")
    occasion = data.get("occasion")
    user_input = data.get("user_input", "")
    if not gender or not occasion:
        return jsonify({"error": "gender and occasion required"}), 400
    if gender not in wardrobe:
        return jsonify({"error": "Invalid gender"}), 400
    outfits = recommend_outfits(gender, occasion, user_input=user_input)
    return jsonify({"outfits": outfits})


@app.route("/api/generate-image", methods=["POST"])
def api_generate_image():
    data = request.get_json() or {}
    outfit = data.get("outfit")
    gender = data.get("gender")
    if not outfit or not gender:
        return jsonify({"error": "outfit and gender required"}), 400
    try:
        prompt_data = build_outfit_prompt(outfit, gender)
        image_bytes = generate_outfit_image(prompt_data)
        b64 = image_bytes_to_base64(image_bytes)
        return jsonify({"image": f"data:image/png;base64,{b64}"})
    except Exception as e:
        msg = str(e)
        msg_l = msg.lower()
        if "credit balance is depleted" in msg_l or "billing error" in msg_l:
            return jsonify({
                "error_code": "insufficient_credits",
                "error": "Image generation temporarily unavailable due to provider credits.",
                "details": msg,
            }), 402
        if "rate limit" in msg_l or "too many requests" in msg_l:
            return jsonify({
                "error_code": "rate_limited",
                "error": "Image generation temporarily rate-limited. Please retry shortly.",
                "details": msg,
            }), 429
        if "authentication failed" in msg_l or "not set" in msg_l:
            return jsonify({
                "error_code": "provider_auth_error",
                "error": "Image generation is not configured correctly.",
                "details": msg,
            }), 500
        return jsonify({"error": msg}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
