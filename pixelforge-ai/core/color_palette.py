"""PixelForge AI — 游戏配色方案生成器."""

import colorsys
from collections import Counter
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image


@dataclass
class PaletteColor:
    hex: str
    rgb: tuple[int, int, int]
    hsv: tuple[float, float, float]
    ratio: float


# ── 游戏预置配色方案 ──────────────────────────────────────────

GAME_PALETTES = {
    "retro_8bit": {
        "label": "复古 8-bit",
        "colors": ["#2d1b2e", "#566c86", "#94b0c2", "#f3ef7d", "#f2a65a"],
    },
    "forest_mood": {
        "label": "森林氛围",
        "colors": ["#1a3a1a", "#2d6a2d", "#52b152", "#8fd68f", "#c8e6c8"],
    },
    "ocean_depth": {
        "label": "深海蓝",
        "colors": ["#0a1628", "#0f2b4c", "#1a5c8a", "#2e9cca", "#89d4f4"],
    },
    "sunset_warm": {
        "label": "日落暖色",
        "colors": ["#4a1a2d", "#8b2d4a", "#d4605e", "#f4a67a", "#fdd2a4"],
    },
    "neon_cyber": {
        "label": "霓虹赛博",
        "colors": ["#0a0a1a", "#1a1a3a", "#ff006e", "#00f5d4", "#fee440"],
    },
    "autumn_gold": {
        "label": "秋日金",
        "colors": ["#3d1c00", "#7a3b1e", "#c47f3b", "#e8b44b", "#fdd97c"],
    },
}


class ColorPalette:
    """游戏配色方案生成器。

    支持从参考图提取 + 预置游戏配色 + 配色方案辅助生成。
    """

    @staticmethod
    def extract_from_image(
        image: Image.Image,
        num_colors: int = 5,
        min_distance: float = 35.0,
    ) -> list[PaletteColor]:
        """从图片提取主色调（K-means 聚类 + 感知去重）。"""
        img = image.copy().convert("RGB")
        w, h = img.size
        max_dim = 300
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        pixels = np.array(img).reshape(-1, 3).astype(np.float32)
        n_clusters = min(num_colors * 3, 16)
        labels = ColorPalette._kmeans(pixels, n_clusters)

        counter = Counter(labels)
        cluster_colors = {}
        for label in set(labels):
            mask = labels == label
            cluster_pixels = pixels[mask]
            cluster_colors[label] = (np.mean(cluster_pixels, axis=0), int(mask.sum()))

        sorted_clusters = sorted(cluster_colors.items(), key=lambda x: x[1][1], reverse=True)

        result: list[PaletteColor] = []
        for label, (color, count) in sorted_clusters:
            if len(result) >= num_colors:
                break
            # 色差去重
            too_close = False
            for existing in result:
                er = np.array(existing.rgb, dtype=np.float32)
                if np.sqrt(np.sum((color - er) ** 2)) < min_distance:
                    too_close = True
                    break
            if too_close:
                continue

            rgb = tuple(int(round(c)) for c in np.clip(color, 0, 255))
            hex_val = "#{:02x}{:02x}{:02x}".format(*rgb)
            hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
            result.append(PaletteColor(
                hex=hex_val, rgb=rgb,
                hsv=(round(hsv[0], 3), round(hsv[1], 3), round(hsv[2], 3)),
                ratio=round(count / len(labels), 3),
            ))

        return result

    @staticmethod
    def get_preset(name: str) -> Optional[dict]:
        """获取预置配色方案。"""
        return GAME_PALETTES.get(name)

    @staticmethod
    def list_presets() -> list[dict]:
        """列出所有预置方案。"""
        return [
            {"name": k, "label": v["label"], "colors": v["colors"]}
            for k, v in GAME_PALETTES.items()
        ]

    @staticmethod
    def to_html(colors: list[PaletteColor]) -> str:
        """渲染色板为 HTML 色块。"""
        if not colors:
            return "<p>无颜色数据</p>"
        swatches = ""
        for c in colors:
            swatches += (
                f'<div style="display:inline-block;margin:6px;text-align:center">'
                f'<div style="width:48px;height:48px;background:{c.hex};'
                f'border-radius:6px;border:1px solid #555"></div>'
                f'<div style="font-size:11px;font-family:monospace;margin-top:3px">{c.hex}</div>'
                f'<div style="font-size:10px;color:#888">{c.ratio:.0%}</div>'
                f"</div>"
            )
        return f'<div style="padding:6px">{swatches}</div>'

    @staticmethod
    def to_prompt_hint(colors: list[PaletteColor]) -> str:
        """将色板转为提示词颜色引导。"""
        if not colors:
            return ""
        return "color palette: " + ", ".join(c.hex for c in colors[:5])

    @staticmethod
    def _kmeans(pixels: np.ndarray, k: int, max_iter: int = 20) -> np.ndarray:
        n = pixels.shape[0]
        rng = np.random.default_rng(42)
        indices = rng.choice(n, k, replace=False)
        centers = pixels[indices].copy()
        labels = np.zeros(n, dtype=np.int32)
        for _ in range(max_iter):
            distances = np.sum((pixels[:, np.newaxis, :] - centers[np.newaxis, :, :]) ** 2, axis=2)
            new_labels = np.argmin(distances, axis=1)
            new_centers = np.zeros_like(centers)
            for j in range(k):
                mask = new_labels == j
                if mask.any():
                    new_centers[j] = np.mean(pixels[mask], axis=0)
                else:
                    new_centers[j] = centers[j]
            if np.all(new_labels == labels):
                break
            labels = new_labels
            centers = new_centers
        return labels
