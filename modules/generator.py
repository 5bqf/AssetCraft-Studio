"""M1: Image generator via 硅基流动 (SiliconFlow) API."""

import base64
import io
import os
import time
from dataclasses import dataclass
from typing import Optional

import requests
from PIL import Image

SILICONFLOW_API_HOST = "https://api.siliconflow.cn"

# 可用模型
DEFAULT_MODEL = "Qwen/Qwen-Image"  # 支持中文提示词
ALT_MODELS = {
    "qwen": "Qwen/Qwen-Image",
    "flux-dev": "black-forest-labs/FLUX.1-dev",
    "flux-schnell": "black-forest-labs/FLUX.1-schnell",
    "flux2-pro": "FLUX.2 [pro]",
    "flux2-flex": "FLUX.2 [flex]",
}


@dataclass
class GenerationResult:
    image: Image.Image
    seed: int
    elapsed_ms: int


def _api_key() -> str:
    key = os.getenv("SILICONFLOW_API_KEY", "")
    if not key:
        raise RuntimeError(
            "SILICONFLOW_API_KEY 环境变量未设置。"
            "请在 https://cloud.siliconflow.cn 获取 API Key，"
            "然后在项目根目录 .env 中添加: SILICONFLOW_API_KEY=your-key"
        )
    return key


def _image_model() -> str:
    return os.getenv("SILICONFLOW_IMAGE_MODEL", DEFAULT_MODEL)


def _call_siliconflow(payload: dict, timeout: int = 120) -> list[Image.Image]:
    """调用硅基流动 Images API 生成图像。"""
    headers = {
        "Authorization": f"Bearer {_api_key()}",
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
            img_bytes = base64.b64decode(b64)
            images.append(Image.open(io.BytesIO(img_bytes)))
        elif url:
            img_resp = requests.get(url, timeout=60)
            img_resp.raise_for_status()
            images.append(Image.open(io.BytesIO(img_resp.content)))

    if not images:
        raise RuntimeError("API 未返回任何图像，请检查提示词或网络连接。")

    return images


# 尺寸预设 — 硅基流动使用 "WxH" 字符串格式
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
    """文生图：通过硅基流动 API 调用 Qwen-Image / FLUX 等模型。"""
    t0 = time.perf_counter()
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

    result_seed = seed
    return GenerationResult(image=images[0], seed=result_seed, elapsed_ms=elapsed)


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
    """图生图：上传参考图进行风格迁移，通过硅基流动图像编辑模型实现。"""
    t0 = time.perf_counter()
    model = _image_model()

    # 将参考图编码为 base64
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

    return GenerationResult(image=images[0], seed=seed, elapsed_ms=elapsed)
