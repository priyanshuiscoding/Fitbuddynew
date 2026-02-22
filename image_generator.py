"""
Image generation via NVIDIA API Catalog.
Create an API key at https://build.nvidia.com and set NVIDIA_API_KEY in .env.
"""
import os
import base64
import re
import requests
import time

DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("NVIDIA_REQUEST_TIMEOUT_SECONDS", "240"))
DEFAULT_MAX_RETRIES = int(os.environ.get("NVIDIA_REQUEST_MAX_RETRIES", "3"))
DEFAULT_STEPS_FALLBACKS = os.environ.get("NVIDIA_STEPS_FALLBACKS", "14,10,6")
DEFAULT_SIZE_FALLBACKS = os.environ.get("NVIDIA_SIZE_FALLBACKS", "1024x1024")
DEFAULT_MODELS_FALLBACKS = os.environ.get("NVIDIA_IMAGE_MODELS_FALLBACKS", "stabilityai/stable-diffusion-xl")
DEFAULT_API_BASE_FALLBACKS = os.environ.get("NVIDIA_API_BASE_FALLBACKS", "")
NVIDIA_TRUST_ENV = os.environ.get("NVIDIA_TRUST_ENV", "0").strip().lower() in ("1", "true", "yes", "on")

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


def _is_endpoint_not_found(text: str) -> bool:
    msg = (text or "").lower()
    return "404 page not found" in msg or msg.strip() == "page not found"


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
    expanded = []
    seen = set()
    for model in models:
        variants = [model]
        # Common NVIDIA FLUX naming mismatch between catalog pages and endpoint paths.
        variants.append(model.replace("flux_1", "flux.1"))
        variants.append(model.replace("flux.1", "flux_1"))
        for candidate in variants:
            c = candidate.strip()
            if c and c not in seen:
                seen.add(c)
                expanded.append(c)
    return expanded


def _parse_api_base_fallbacks(primary_base: str, value: str):
    bases = [primary_base]
    for item in (value or "").split(","):
        candidate = item.strip()
        if candidate and candidate not in bases:
            bases.append(candidate)

    expanded = []
    seen = set()
    for base in bases:
        b = base.rstrip("/")
        if not b:
            continue
        variants = [b]
        if b.endswith("/v1/genai"):
            variants.append(b[: -len("/genai")])
        elif b.endswith("/v1"):
            variants.append(f"{b}/genai")
        for v in variants:
            if v not in seen:
                seen.add(v)
                expanded.append(v)
    return expanded


def _build_model_urls(api_base: str, model_name: str):
    base = api_base.rstrip("/")
    model = model_name.strip("/")
    urls = [f"{base}/{model}"]
    out = []
    seen = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _parse_min_from_message(text: str):
    if not text:
        return None
    match = re.search(r"greater than or equal to\s+(\d+)", text, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def _extract_min_constraints_from_text(text: str):
    msg = text or ""
    matches = {
        "width": re.search(r"width\s+Input should be greater than or equal to\s+(\d+)", msg, re.IGNORECASE),
        "height": re.search(r"height\s+Input should be greater than or equal to\s+(\d+)", msg, re.IGNORECASE),
        "steps": re.search(r"steps\s+Input should be greater than or equal to\s+(\d+)", msg, re.IGNORECASE),
    }
    result = {}
    for key, match in matches.items():
        if match:
            result[key] = int(match.group(1))
    return result


def _extract_min_constraints_from_payload(payload):
    result = {}
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, list):
            for item in detail:
                if not isinstance(item, dict):
                    continue
                loc = item.get("loc") or []
                if not isinstance(loc, (list, tuple)):
                    continue
                for key in ("width", "height", "steps"):
                    if key not in loc:
                        continue
                    min_value = None
                    ctx = item.get("ctx")
                    if isinstance(ctx, dict):
                        ctx_value = ctx.get("ge")
                        if isinstance(ctx_value, (int, float)):
                            min_value = int(ctx_value)
                    if min_value is None:
                        min_value = _parse_min_from_message(item.get("msg"))
                    if min_value is not None:
                        result[key] = max(result.get(key, 0), min_value)
        elif isinstance(detail, str):
            result.update(_extract_min_constraints_from_text(detail))
        if not result:
            for key in ("message", "error"):
                value = payload.get(key)
                if isinstance(value, str):
                    result.update(_extract_min_constraints_from_text(value))
    elif isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            loc = item.get("loc") or []
            if not isinstance(loc, (list, tuple)):
                continue
            for key in ("width", "height", "steps"):
                if key not in loc:
                    continue
                min_value = _parse_min_from_message(item.get("msg"))
                if min_value is not None:
                    result[key] = max(result.get(key, 0), min_value)
    return result


def _extract_min_constraints(response: requests.Response, fallback_text: str):
    payload = None
    try:
        payload = response.json()
    except Exception:
        payload = None
    result = _extract_min_constraints_from_payload(payload)
    if not result:
        result = _extract_min_constraints_from_text(fallback_text)
    if not result:
        result = _extract_min_constraints_from_text(response.text or "")
    return result


def _build_size_profiles(size_fallbacks, min_width: int, min_height: int):
    out = []
    seen = set()
    for width, height in size_fallbacks:
        adjusted = (max(width, min_width), max(height, min_height))
        if adjusted not in seen:
            seen.add(adjusted)
            out.append(adjusted)
    if not out:
        out.append((min_width, min_height))
    return out


def _extract_error_message(response: requests.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            if "detail" in data and isinstance(data["detail"], str):
                return data["detail"]
            if "detail" in data and isinstance(data["detail"], list):
                parts = []
                for item in data["detail"]:
                    if not isinstance(item, dict):
                        continue
                    loc = item.get("loc")
                    msg = item.get("msg") if isinstance(item.get("msg"), str) else None
                    if isinstance(loc, (list, tuple)):
                        loc_text = " -> ".join(str(chunk) for chunk in loc)
                        if msg:
                            parts.append(f"{loc_text} {msg}")
                        elif loc_text:
                            parts.append(loc_text)
                    elif msg:
                        parts.append(msg)
                if parts:
                    return " | ".join(parts)
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
    api_base_fallbacks = _parse_api_base_fallbacks(NVIDIA_API_BASE, DEFAULT_API_BASE_FALLBACKS)
    model_fallbacks = _parse_model_fallbacks(NVIDIA_IMAGE_MODEL, DEFAULT_MODELS_FALLBACKS)
    min_width = 1
    min_height = 1
    min_steps = 1

    with requests.Session() as session:
        session.trust_env = NVIDIA_TRUST_ENV
        last_error = None
        r = None
        attempted_urls = []
        for _ in range(3):
            size_profiles = _build_size_profiles(size_fallbacks, min_width=min_width, min_height=min_height)
            steps_profiles = [s for s in steps_fallbacks if s >= min_steps] or [min_steps]
            endpoint_profiles = []
            for api_base in api_base_fallbacks:
                for model_name in model_fallbacks:
                    for model_url in _build_model_urls(api_base, model_name):
                        endpoint_profiles.append((api_base, model_name, model_url))
            if not endpoint_profiles:
                raise RuntimeError("No NVIDIA endpoint profiles could be built. Check NVIDIA_API_BASE.")

            total_profiles = len(endpoint_profiles) * len(size_profiles) * len(steps_profiles)
            profile_index = 0
            should_retry_with_constraints = False

            for _, _, model_url in endpoint_profiles:
                endpoint_unavailable = False
                if model_url not in attempted_urls:
                    attempted_urls.append(model_url)
                for width, height in size_profiles:
                    for step_value in steps_profiles:
                        profile_index += 1
                        payload = dict(base_payload)
                        payload["steps"] = step_value
                        payload["width"] = width
                        payload["height"] = height
                        payload["samples"] = 1
                        for attempt in range(1, max_retries + 1):
                            try:
                                r = session.post(model_url, headers=headers, json=payload, timeout=timeout_seconds)
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
                            constraints = _extract_min_constraints(r, msg)
                            if constraints:
                                min_width = max(min_width, constraints.get("width", min_width))
                                min_height = max(min_height, constraints.get("height", min_height))
                                min_steps = max(min_steps, constraints.get("steps", min_steps))
                                last_error = RuntimeError(msg)
                                should_retry_with_constraints = True
                                break
                            if _is_deadline_exceeded(msg):
                                last_error = RuntimeError(msg)
                                break
                            if _is_model_not_found_for_account(msg):
                                last_error = RuntimeError(msg)
                                endpoint_unavailable = True
                                break
                            if r.status_code == 404 and _is_endpoint_not_found(msg):
                                last_error = RuntimeError(msg)
                                endpoint_unavailable = True
                                break
                            if r.status_code == 422:
                                # Generic inference 422 means this endpoint/model combo is not usable.
                                last_error = RuntimeError(msg)
                                endpoint_unavailable = True
                                break

                            if 500 <= r.status_code < 600:
                                last_error = RuntimeError(msg)
                                if attempt < max_retries:
                                    time.sleep(min(2 * attempt, 6))
                                    continue

                            break

                        if r is not None and r.status_code == 200:
                            break
                        if endpoint_unavailable or should_retry_with_constraints:
                            break
                    if r is not None and r.status_code == 200:
                        break
                    if endpoint_unavailable or should_retry_with_constraints:
                        break
                if r is not None and r.status_code == 200:
                    break
                if should_retry_with_constraints:
                    break

            if r is not None and r.status_code == 200:
                break
            if not should_retry_with_constraints:
                break

        if r is None:
            attempted_text = ", ".join(attempted_urls) if attempted_urls else "(none)"
            raise RuntimeError(
                f"NVIDIA image generation failed before receiving a response: {last_error}. "
                f"Attempted endpoints: {attempted_text}"
            )

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
            if r.status_code == 404 and _is_endpoint_not_found(msg):
                attempted_text = ", ".join(attempted_urls) if attempted_urls else "(none)"
                raise RuntimeError(
                    f"NVIDIA model endpoint not found: {msg}. "
                    "Verify NVIDIA_IMAGE_MODEL. For FLUX, use 'black-forest-labs/flux.1-schnell'. "
                    f"Attempted endpoints: {attempted_text}"
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
