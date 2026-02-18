# FitBuddy

Outfit ideas from your wardrobe + an AI preview image using NVIDIA API Catalog.

## Run locally

1. Open a terminal in this folder:
```bash
cd D:\Neurodrobe-wardrobe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a NVIDIA API key at:
`https://build.nvidia.com`

4. Create `.env` in the project root (`app.py` folder):
```env
NVIDIA_API_KEY=nvapi_your_key_here
```

5. Start the app:
```bash
python app.py
```

6. Open:
`http://localhost:5000`

## Optional env vars

```env
# Defaults shown below
NVIDIA_IMAGE_MODEL=stabilityai/stable-diffusion-xl
NVIDIA_API_BASE=https://ai.api.nvidia.com/v1/genai
```

## Behavior when key is missing

Recommendations still work.
Only image preview generation fails until `NVIDIA_API_KEY` is configured.

## Deployment note

For Render/Railway/Docker deploys, set `NVIDIA_API_KEY` as an environment variable in the platform dashboard.

## Affiliate suggestion demo

Outfit cards can display "Complete this look" product links with image previews.
Current links are configured in `affiliate_recommender.py` and are demo placeholders.
Replace `affiliate_url` values with your real affiliate links for Myntra/Amazon/Flipkart.
