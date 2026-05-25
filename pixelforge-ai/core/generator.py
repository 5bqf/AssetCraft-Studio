"""PixelForge AI — 2D 游戏素材生成器."""

import base64
import io
import os
import time
from dataclasses import dataclass
from typing import Optional

import requests
from PIL import Image

from config import Config, GAME_STYLES, ASSET_TYPES


@dataclass
class GenerationResult:
    """生成结果。"""
    image: Image.Image
    prompt: str
    style: str
    asset_type: str
    seed: int
    elapsed_ms: int
    backend: str = "siliconflow"


class GameAssetGenerator:
    """2D 游戏素材生成器 — 封装硅基流动 API。"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or Config.SILICONFLOW_API_KEY
        self.api_base = api_base or Config.SILICONFLOW_API_BASE
        self.model = model or Config.SILICONFLOW_IMAGE_MODEL

        if not self.api_key:
            raise RuntimeError(
                "SILICONFLOW_API_KEY 未设置。"
                "请在 pixelforge-ai/.env 中配置 API Key。"
            )

    # ── 公开 API ──────────────────────────────────────────────

    def generate_sprite(
        self,
        prompt: str,
        style: str = "pixel_art",
        asset_type: str = "sprite",
        width: int = 256,
        height: int = 256,
        negative_prompt: str = "",
        steps: int = 20,
        seed: int = 0,
    ) -> GenerationResult:
        """生成单个游戏素材。

        Args:
            prompt: 素材描述（支持中文）
            style: 风格键名，对应 GAME_STYLES
            asset_type: 素材类型，对应 ASSET_TYPES
            width/height: 输出尺寸
            negative_prompt: 负面提示词
            steps: 推理步数 (1-50)
            seed: 随机种子 (0=随机)
        """
        t0 = time.perf_counter()

        # 构建增强提示词
        full_prompt = self._build_prompt(prompt, style, asset_type)
        full_negative = negative_prompt or self._build_negative(style)

        # 调用 API
        image = self._call_api(
            prompt=full_prompt,
            negative_prompt=full_negative,
            width=width,
            height=height,
            steps=steps,
            seed=seed,
        )

        elapsed = int((time.perf_counter() - t0) * 1000)
        return GenerationResult(
            image=image,
            prompt=full_prompt,
            style=style,
            asset_type=asset_type,
            seed=seed,
            elapsed_ms=elapsed,
        )

    def generate_from_reference(
        self,
        prompt: str,
        reference_image: Image.Image,
        style: str = "pixel_art",
        asset_type: str = "sprite",
        width: int = 256,
        height: int = 256,
        steps: int = 20,
        seed: int = 0,
    ) -> GenerationResult:
        """基于参考图生成素材（图生图）。

        Args:
            prompt: 目标描述
            reference_image: PIL Image 参考图
            其余参数同 generate_sprite
        """
        t0 = time.perf_counter()

        full_prompt = self._build_prompt(prompt, style, asset_type)

        # 编码参考图
        buf = io.BytesIO()
        reference_image.save(buf, format="PNG")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")

        image = self._call_api(
            prompt=full_prompt,
            image_b64=img_b64,
            width=width,
            height=height,
            steps=steps,
            seed=seed,
        )

        elapsed = int((time.perf_counter() - t0) * 1000)
        return GenerationResult(
            image=image,
            prompt=full_prompt,
            style=style,
            asset_type=asset_type,
            seed=seed,
            elapsed_ms=elapsed,
        )

    # ── 内部方法 ──────────────────────────────────────────────

    def _build_prompt(self, user_prompt: str, style: str, asset_type: str) -> str:
        """组合用户描述 + 风格前缀/后缀 + 素材类型。"""
        style_cfg = GAME_STYLES.get(style, GAME_STYLES["pixel_art"])
        asset_cfg = ASSET_TYPES.get(asset_type, ASSET_TYPES["sprite"])

        parts = [
            style_cfg["prefix"],
            f"{asset_cfg['label']}, ",
            user_prompt,
            style_cfg["suffix"],
            f", {asset_cfg['description']}",
        ]
        return "".join(parts)

    def _build_negative(self, style: str) -> str:
        """获取风格的默认负面提示词。"""
        style_cfg = GAME_STYLES.get(style, {})
        return style_cfg.get("negative", "")

    def _call_api(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 256,
        height: int = 256,
        steps: int = 20,
        seed: int = 0,
        image_b64: Optional[str] = None,
        timeout: int = 120,
    ) -> Image.Image:
        """调用硅基流动 Images API。"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": f"{width}x{height}",
            "batch_size": 1,
            "num_inference_steps": steps,
            "guidance_scale": 7.5,
        }
        if seed != 0:
            payload["seed"] = seed
        if image_b64:
            payload["image"] = image_b64

        resp = requests.post(
            f"{self.api_base}/images/generations",
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        if resp.status_code != 200:
            detail = self._parse_error(resp)
            raise RuntimeError(f"硅基流动 API 返回 {resp.status_code}: {detail}")

        data = resp.json()
        images_data = data.get("images", [])
        if not images_data:
            raise RuntimeError("API 未返回图像")

        first = images_data[0]
        # 优先 b64_json，其次 url
        if first.get("b64_json"):
            img_bytes = base64.b64decode(first["b64_json"])
            return Image.open(io.BytesIO(img_bytes))
        elif first.get("url"):
            img_resp = requests.get(first["url"], timeout=60)
            img_resp.raise_for_status()
            return Image.open(io.BytesIO(img_resp.content))
        else:
            raise RuntimeError(f"无法解析 API 返回: {first}")

    @staticmethod
    def _parse_error(resp) -> str:
        try:
            return str(resp.json())
        except Exception:
            return resp.text[:300]
