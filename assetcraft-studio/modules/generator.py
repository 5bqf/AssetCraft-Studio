"""M1: Image generator — 硅基流动主推 + Pollinations.ai 免费回退."""

import base64
import io
import os
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import requests
from PIL import Image

SILICONFLOW_API_HOST = "https://api.siliconflow.cn"
POLLINATIONS_HOST = "https://image.pollinations.ai"

DEFAULT_MODEL = "Qwen/Qwen-Image"


@dataclass
class GenerationResult:
    image: Image.Image
    seed: int
    elapsed_ms: int
    backend: str = ""


def _has_siliconflow_key() -> bool:
    return bool(os.getenv("SILICONFLOW_API_KEY", ""))


def _image_model() -> str:
    return os.getenv("SILICONFLOW_IMAGE_MODEL", DEFAULT_MODEL)


# ── 硅基流动 backend ────────────────────────────────────────────

def _call_siliconflow(payload: dict, timeout: int = 120) -> list[Image.Image]:
    key = os.getenv("SILICONFLOW_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        f"{SILICONFLOW_API_HOST}/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=timeout,
    )
    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"硅基流动 API 返回 {resp.status_code}: {detail}")

    data = resp.json()
    images: list[Image.Image] = []
    for item in data.get("images", []):
        url = item.get("url", "")
        b64 = item.get("b64_json", "")
        if b64:
            images.append(Image.open(io.BytesIO(base64.b64decode(b64))))
        elif url:
            img_resp = requests.get(url, timeout=60)
            img_resp.raise_for_status()
            images.append(Image.open(io.BytesIO(img_resp.content)))
    if not images:
        raise RuntimeError("API 未返回任何图像")
    return images


# ── Pollinations.ai 免费 backend ─────────────────────────────────

def _call_pollinations(
    prompt: str,
    width: int = 512,
    height: int = 512,
    seed: int = 0,
    timeout: int = 120,
) -> Image.Image:
    """Pollinations.ai — 完全免费，无需 API Key。"""
    encoded = quote(prompt, safe="")
    url = (
        f"{POLLINATIONS_HOST}/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true"
    )
    resp = requests.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Pollinations API 返回 {resp.status_code}: {resp.text[:300]}")
    return Image.open(io.BytesIO(resp.content))


# ── Public API ───────────────────────────────────────────────────

SIZE_PRESETS = {
    "正方形 512x512": (512, 512),
    "正方形 1024x1024": (1024, 1024),
    "横向 16:9 (896x512)": (896, 512),
    "纵向 9:16 (512x896)": (512, 896),
    "横向 3:2 (768x512)": (768, 512),
    "图标 256x256": (256, 256),
    "精灵表 1024x512": (1024, 512),
}


def _to_size_str(w: int, h: int) -> str:
    return f"{w}x{h}"


def text_to_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.5,
    seed: int = 0,
    samples: int = 1,
    style_preset: Optional[str] = None,
) -> GenerationResult:
    """文生图：硅基流动优先，余额不足自动回退 Pollinations.ai 免费接口。"""
    t0 = time.perf_counter()

    # 尝试硅基流动
    if _has_siliconflow_key():
        try:
            model = _image_model()
            payload: dict = {
                "model": model,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "image_size": _to_size_str(width, height),
                "batch_size": min(samples, 4),
                "num_inference_steps": steps,
                "guidance_scale": cfg_scale,
            }
            if seed != 0:
                payload["seed"] = seed
            images = _call_siliconflow(payload)
            elapsed = int((time.perf_counter() - t0) * 1000)
            return GenerationResult(image=images[0], seed=seed, elapsed_ms=elapsed, backend="siliconflow")
        except RuntimeError as e:
            msg = str(e)
            # 余额不足或鉴权失败 → 回退
            if "30001" not in msg and "401" not in msg and "403" not in msg:
                raise

    # 回退: Pollinations.ai 免费
    image = _call_pollinations(prompt, width, height, seed)
    elapsed = int((time.perf_counter() - t0) * 1000)
    return GenerationResult(image=image, seed=seed, elapsed_ms=elapsed, backend="pollinations")


def image_to_image(
    prompt: str,
    init_image: Image.Image,
    negative_prompt: str = "",
    image_strength: float = 0.35,
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.5,
    seed: int = 0,
    samples: int = 1,
    style_preset: Optional[str] = None,
) -> GenerationResult:
    """图生图：硅基流动优先，余额不足回退 Pollinations（通过增强提示词模拟）。"""
    t0 = time.perf_counter()

    if _has_siliconflow_key():
        try:
            model = _image_model()
            buf = io.BytesIO()
            init_image.save(buf, format="PNG")
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode("utf-8")

            payload: dict = {
                "model": model,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "image": img_b64,
                "image_size": _to_size_str(width, height),
                "batch_size": min(samples, 4),
                "num_inference_steps": steps,
                "guidance_scale": cfg_scale,
            }
            if seed != 0:
                payload["seed"] = seed
            images = _call_siliconflow(payload)
            elapsed = int((time.perf_counter() - t0) * 1000)
            return GenerationResult(image=images[0], seed=seed, elapsed_ms=elapsed, backend="siliconflow")
        except RuntimeError as e:
            msg = str(e)
            if "30001" not in msg and "401" not in msg and "403" not in msg:
                raise

    # 回退: Pollinations（增强提示词模拟风格迁移）
    fallback_prompt = (
        f"{prompt}, in the style of the reference image, same color palette, "
        f"similar composition, artistic style transfer"
    )
    image = _call_pollinations(fallback_prompt, width, height, seed)
    elapsed = int((time.perf_counter() - t0) * 1000)
    return GenerationResult(image=image, seed=seed, elapsed_ms=elapsed, backend="pollinations")
