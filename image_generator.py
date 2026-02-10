"""
Free image generation via Hugging Face Inference Providers.
Get a token at https://huggingface.co/settings/tokens
"""
import os
import base64
import time
import requests

HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

# Try a configured model first, then known text-to-image models.
_configured_model = os.environ.get("HF_IMAGE_MODEL", "").strip()
HF_MODELS = [m for m in [
    _configured_model or "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-Krea-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
] if m]


def generate_outfit_image(prompt_data: dict) -> bytes:
    """
    Generate outfit image using Hugging Face free Inference API.
    Returns PNG image bytes.
    """
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise RuntimeError(
            "HUGGINGFACE_TOKEN not set. Get a free token at https://huggingface.co/settings/tokens "
            "then add it to a .env file: HUGGINGFACE_TOKEN=your_token"
        )

    prompt = prompt_data["prompt"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": prompt_data.get("negative_prompt", "")
        },
    }

    # HF may return 503 while model loads; retry once after a short wait.
    # If a model returns 404, try the next candidate model.
    last_error = None
    for model in HF_MODELS:
        model_url = f"{HF_ROUTER_BASE}/{model}"
        for attempt in range(2):
            r = requests.post(model_url, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                return r.content
            if r.status_code == 503 and attempt == 0:
                time.sleep(15)
                continue
            if r.status_code in (401, 403):
                msg = r.text.strip()
                if "sufficient permissions" in msg.lower() or "inference providers" in msg.lower():
                    raise RuntimeError(
                        "Hugging Face token lacks Inference Providers permission. "
                        "Create a new User Access Token with permission to call Inference Providers, "
                        "set HUGGINGFACE_TOKEN in .env, then restart the app."
                    )
            msg = r.text.strip() or f"HTTP {r.status_code}"
            msg_l = msg.lower()
            if r.status_code == 404:
                last_error = f"model not found or unsupported on router: {model}"
                break
            if "deprecated and no longer supported" in msg_l or "not supported by provider hf-inference" in msg_l:
                last_error = f"model deprecated/unsupported by hf-inference: {model}"
                break
            raise RuntimeError(f"Image generation failed: {msg}")

    if last_error:
        raise RuntimeError(
            f"Image generation failed: {last_error}. "
            f"Tried models: {', '.join(HF_MODELS)}. "
            "Set HF_IMAGE_MODEL in .env to a model that supports text-to-image via Inference Providers."
        )
    raise RuntimeError("Image generation failed")


def image_bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")
