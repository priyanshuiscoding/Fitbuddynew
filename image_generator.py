"""
Image generation via NVIDIA API Catalog.
Create an API key at https://build.nvidia.com and set NVIDIA_API_KEY in .env.
"""
import os
import base64
import requests

DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("NVIDIA_REQUEST_TIMEOUT_SECONDS", "180"))
DEFAULT_MAX_RETRIES = int(os.environ.get("NVIDIA_REQUEST_MAX_RETRIES", "3"))
DEFAULT_STEPS_FALLBACKS = os.environ.get("NVIDIA_STEPS_FALLBACKS", "30,24,18")

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

    base_payload = {
        "text_prompts": text_prompts,
        "sampler": "K_DPM_2_ANCESTRAL",
        "cfg_scale": 7,
        "seed": 0,
    }

    timeout_seconds = max(30, DEFAULT_TIMEOUT_SECONDS)
    max_retries = max(1, DEFAULT_MAX_RETRIES)
    steps_fallbacks = _parse_steps_fallbacks(DEFAULT_STEPS_FALLBACKS)

    last_error = None
    r = None
    for step_value in steps_fallbacks:
        payload = dict(base_payload)
        payload["steps"] = step_value
        for attempt in range(1, max_retries + 1):
            try:
                r = requests.post(model_url, headers=headers, json=payload, timeout=timeout_seconds)
            except requests.exceptions.Timeout as exc:
                last_error = exc
                if attempt == max_retries and step_value == steps_fallbacks[-1]:
                    raise RuntimeError(
                        f"NVIDIA image generation timed out after {max_retries} attempts "
                        f"(timeout {timeout_seconds}s per attempt). Try again or lower generation complexity."
                    ) from exc
                continue
            except requests.exceptions.RequestException as exc:
                last_error = exc
                if attempt == max_retries and step_value == steps_fallbacks[-1]:
                    raise RuntimeError(f"NVIDIA image generation request failed: {exc}") from exc
                continue

            if r.status_code == 200:
                break

            msg = _extract_error_message(r)
            if _is_deadline_exceeded(msg):
                last_error = RuntimeError(msg)
                break

            if 500 <= r.status_code < 600:
                last_error = RuntimeError(msg)
                if attempt < max_retries:
                    continue

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
