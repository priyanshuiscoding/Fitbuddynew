"""
Image generation via NVIDIA API Catalog.
Create an API key at https://build.nvidia.com and set NVIDIA_API_KEY in .env.
"""
import os
import base64
import requests

NVIDIA_API_BASE = os.environ.get("NVIDIA_API_BASE", "https://ai.api.nvidia.com/v1/genai").rstrip("/")
NVIDIA_IMAGE_MODEL = os.environ.get("NVIDIA_IMAGE_MODEL", "stabilityai/stable-diffusion-xl").strip()


def _extract_error_message(response: requests.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            if "detail" in data and isinstance(data["detail"], str):
                return data["detail"]
            if "message" in data and isinstance(data["message"], str):
                return data["message"]
            if "error" in data and isinstance(data["error"], str):
                return data["error"]
    except Exception:
        pass
    return response.text.strip() or f"HTTP {response.status_code}"


def generate_outfit_image(prompt_data: dict) -> bytes:
    """
    Generate outfit image using NVIDIA image model API.
    Returns PNG image bytes.
    """
    token = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not token:
        raise RuntimeError(
            "NVIDIA_API_KEY not set. Create a key at https://build.nvidia.com, "
            "then add NVIDIA_API_KEY=your_key in .env and restart the app."
        )

    prompt = (prompt_data.get("prompt") or "").strip()
    if not prompt:
        raise RuntimeError("Prompt is empty; cannot generate image.")

    negative_prompt = (prompt_data.get("negative_prompt") or "").strip()
    model_url = f"{NVIDIA_API_BASE}/{NVIDIA_IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    text_prompts = [{"text": prompt, "weight": 1}]
    if negative_prompt:
        text_prompts.append({"text": negative_prompt, "weight": -1})

    payload = {
        "text_prompts": text_prompts,
        "sampler": "K_DPM_2_ANCESTRAL",
        "cfg_scale": 7,
        "steps": 35,
        "seed": 0,
    }

    r = requests.post(model_url, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        msg = _extract_error_message(r)
        if r.status_code in (401, 403):
            raise RuntimeError(
                f"NVIDIA API authentication failed: {msg}. "
                "Check NVIDIA_API_KEY and ensure the key has access to the selected model."
            )
        if r.status_code == 429:
            raise RuntimeError(
                f"NVIDIA API rate limit reached: {msg}. "
                "Wait for quota reset or reduce request frequency."
            )
        if r.status_code == 402:
            raise RuntimeError(f"NVIDIA API billing error: {msg}")
        raise RuntimeError(f"NVIDIA image generation failed: {msg}")

    data = r.json()
    artifacts = data.get("artifacts") if isinstance(data, dict) else None
    if not artifacts:
        raise RuntimeError("NVIDIA image generation failed: response did not include artifacts.")

    b64_data = artifacts[0].get("base64")
    if not b64_data:
        raise RuntimeError("NVIDIA image generation failed: image artifact did not include base64 data.")
    return base64.b64decode(b64_data)


def image_bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")
