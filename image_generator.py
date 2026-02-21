"""
Image generation via NVIDIA API Catalog.
Create an API key at https://build.nvidia.com and set NVIDIA_API_KEY in .env.
"""
import os
import base64
import requests
import time

DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("NVIDIA_REQUEST_TIMEOUT_SECONDS", "240"))
DEFAULT_MAX_RETRIES = int(os.environ.get("NVIDIA_REQUEST_MAX_RETRIES", "3"))
DEFAULT_STEPS_FALLBACKS = os.environ.get("NVIDIA_STEPS_FALLBACKS", "14,10,6,4")
DEFAULT_SIZE_FALLBACKS = os.environ.get("NVIDIA_SIZE_FALLBACKS", "640x640,512x512,384x384")
DEFAULT_MODELS_FALLBACKS = os.environ.get("NVIDIA_IMAGE_MODELS_FALLBACKS", "")

NVIDIA_API_BASE = os.environ.get("NVIDIA_API_BASE", "https://ai.api.nvidia.com/v1/genai").rstrip("/")
NVIDIA_IMAGE_MODEL = os.environ.get("NVIDIA_IMAGE_MODEL", "stabilityai/stable-diffusion-xl").strip()


def _parse_steps_fallbacks(value: str):
    parsed = []
    for chunk in (value or "").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            step_value = int(chunk)
            if step_value > 0:
                parsed.append(step_value)
        except ValueError:
            continue
    return parsed or [30, 24, 18]


def _is_deadline_exceeded(text: str) -> bool:
    msg = (text or "").lower()
    return "deadline exceeded" in msg or "statuscode.deadline_exceeded" in msg


def _is_model_not_found_for_account(text: str) -> bool:
    msg = (text or "").lower()
    return "not found for account" in msg or ("function" in msg and "not found" in msg)


def _parse_size_fallbacks(value: str):
    parsed = []
    for chunk in (value or "").split(","):
        chunk = chunk.strip().lower()
        if "x" not in chunk:
            continue
        width_text, height_text = chunk.split("x", 1)
        try:
            width = int(width_text.strip())
            height = int(height_text.strip())
        except ValueError:
            continue
        if width > 0 and height > 0:
            parsed.append((width, height))
    return parsed or [(768, 768), (640, 640), (512, 512)]


def _parse_model_fallbacks(primary_model: str, value: str):
    models = [primary_model]
    for model in (value or "").split(","):
        m = model.strip()
        if m and m not in models:
            models.append(m)
    return models


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
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    text_prompts = [{"text": prompt, "weight": 1}]
    if negative_prompt:
        text_prompts.append({"text": negative_prompt, "weight": -1})

    base_payload = {
        "text_prompts": text_prompts,
        "sampler": "K_EULER_ANCESTRAL",
        "cfg_scale": 6,
        "seed": 0,
    }

    timeout_seconds = max(30, DEFAULT_TIMEOUT_SECONDS)
    max_retries = max(1, DEFAULT_MAX_RETRIES)
    steps_fallbacks = _parse_steps_fallbacks(DEFAULT_STEPS_FALLBACKS)
    size_fallbacks = _parse_size_fallbacks(DEFAULT_SIZE_FALLBACKS)
    model_fallbacks = _parse_model_fallbacks(NVIDIA_IMAGE_MODEL, DEFAULT_MODELS_FALLBACKS)

    last_error = None
    r = None
    total_profiles = len(model_fallbacks) * len(size_fallbacks) * len(steps_fallbacks)
    profile_index = 0
    for model_name in model_fallbacks:
        model_url = f"{NVIDIA_API_BASE}/{model_name}"
        model_unavailable = False
        for width, height in size_fallbacks:
            for step_value in steps_fallbacks:
                profile_index += 1
                payload = dict(base_payload)
                payload["steps"] = step_value
                payload["width"] = width
                payload["height"] = height
                payload["samples"] = 1
                for attempt in range(1, max_retries + 1):
                    try:
                        r = requests.post(model_url, headers=headers, json=payload, timeout=timeout_seconds)
                    except requests.exceptions.Timeout as exc:
                        last_error = exc
                        if attempt == max_retries and profile_index == total_profiles:
                            raise RuntimeError(
                                f"NVIDIA image generation timed out after {max_retries} attempts "
                                f"(timeout {timeout_seconds}s per attempt). Try again or lower generation complexity."
                            ) from exc
                        time.sleep(min(2 * attempt, 6))
                        continue
                    except requests.exceptions.RequestException as exc:
                        last_error = exc
                        if attempt == max_retries and profile_index == total_profiles:
                            raise RuntimeError(f"NVIDIA image generation request failed: {exc}") from exc
                        time.sleep(min(2 * attempt, 6))
                        continue

                    if r.status_code == 200:
                        break

                    msg = _extract_error_message(r)
                    if _is_deadline_exceeded(msg):
                        last_error = RuntimeError(msg)
                        break
                    if _is_model_not_found_for_account(msg):
                        last_error = RuntimeError(msg)
                        model_unavailable = True
                        break

                    if 500 <= r.status_code < 600:
                        last_error = RuntimeError(msg)
                        if attempt < max_retries:
                            time.sleep(min(2 * attempt, 6))
                            continue

                    break

                if r is not None and r.status_code == 200:
                    break
                if model_unavailable:
                    break
            if r is not None and r.status_code == 200:
                break
            if model_unavailable:
                break
        if r is not None and r.status_code == 200:
            break

    if r is None:
        raise RuntimeError(f"NVIDIA image generation failed before receiving a response: {last_error}")

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
        if _is_model_not_found_for_account(msg):
            raise RuntimeError(
                "Selected NVIDIA model is not enabled for this API key. "
                "Set NVIDIA_IMAGE_MODEL to a model available in your NVIDIA account."
            )
        if _is_deadline_exceeded(msg):
            raise RuntimeError(
                "NVIDIA image generation exceeded provider deadline. "
                "Please retry, or reduce generation load."
            )
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
