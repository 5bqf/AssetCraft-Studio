"""PixelForge AI — 主项目配置."""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """应用配置，所有敏感信息通过环境变量注入。"""

    # ── 硅基流动 API ──
    SILICONFLOW_API_KEY: str = os.getenv(
        "SILICONFLOW_API_KEY", ""
    )
    SILICONFLOW_API_BASE: str = os.getenv(
        "SILICONFLOW_API_BASE", "https://api.siliconflow.cn/v1"
    )
    SILICONFLOW_IMAGE_MODEL: str = os.getenv(
        "SILICONFLOW_IMAGE_MODEL", "Qwen/Qwen-Image"
    )

    # ── Gradio ──
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: int = int(os.getenv("PORT", "7860"))

    # ── 输出目录 ──
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "static", "outputs")

    # ── 生成限制 ──
    MAX_BATCH_SIZE: int = 20
    MAX_STEPS: int = 50
    MIN_STEPS: int = 10


# ── 2D 游戏素材类型 ──

ASSET_TYPES = {
    "sprite": {
        "label": "精灵 (Sprite)",
        "description": "角色、道具、NPC 等独立图像",
        "default_size": (256, 256),
        "export_type": "sprite",
    },
    "tileset": {
        "label": "瓦片集 (Tileset)",
        "description": "地图瓦片，用于拼接游戏场景",
        "default_size": (512, 512),
        "export_type": "tileset",
    },
    "ui_element": {
        "label": "UI 元素 (UI Element)",
        "description": "按钮、面板、图标等界面组件",
        "default_size": (128, 128),
        "export_type": "ui",
    },
    "vfx": {
        "label": "特效 (VFX)",
        "description": "粒子、爆炸、魔法等视觉特效",
        "default_size": (256, 256),
        "export_type": "vfx",
    },
    "icon": {
        "label": "图标 (Icon)",
        "description": "物品栏、技能栏中的小图标",
        "default_size": (64, 64),
        "export_type": "icon",
    },
}


# ── 2D 游戏风格预设 ──

GAME_STYLES = {
    "pixel_art": {
        "label": "像素风 (Pixel Art)",
        "prefix": "pixel art, 16-bit retro game ",
        "suffix": ", clean pixel edges, limited color palette, sharp, on transparent background",
        "negative": "blurry, smooth gradients, photorealistic, 3D, anti-aliasing",
    },
    "cartoon_2d": {
        "label": "卡通 2D (Cartoon 2D)",
        "prefix": "2D cartoon game asset, cel shaded, bright colors, ",
        "suffix": ", bold outlines, flat shading, cheerful style, on transparent background",
        "negative": "realistic, 3D, dark, gritty, noise, complex shading",
    },
    "hand_drawn": {
        "label": "手绘风 (Hand-Drawn)",
        "prefix": "hand-drawn sketch style, watercolor texture, ",
        "suffix": ", gentle ink outlines, warm and organic, storybook art, indie game",
        "negative": "digital vector, sharp lines, pixel perfect, synthetic, 3D",
    },
    "low_poly": {
        "label": "低多边形 (Low Poly)",
        "prefix": "low poly 3D render, flat shaded, geometric shapes, ",
        "suffix": ", clean geometry, minimalist, isometric view, game ready",
        "negative": "high poly, realistic texture, complex details, noise",
    },
    "dark_fantasy": {
        "label": "暗黑奇幻 (Dark Fantasy)",
        "prefix": "dark fantasy game asset, gothic horror, torch-lit, ",
        "suffix": ", high contrast, deep shadows, rusted metal, oppressive atmosphere",
        "negative": "bright, cheerful, colorful, cartoon, cute, pastel, daylight",
    },
    "sci_fi": {
        "label": "科幻 (Sci-Fi)",
        "prefix": "sci-fi game asset, neon glow, cyberpunk, futuristic, ",
        "suffix": ", holographic UI, blue and cyan tones, high-tech, clean",
        "negative": "natural lighting, warm colors, organic, rustic, vintage",
    },
}


# ── 尺寸预设 ──

SIZE_PRESETS = {
    "图标 64x64": (64, 64),
    "小型 128x128": (128, 128),
    "中型 256x256": (256, 256),
    "精灵 512x512": (512, 512),
    "大型 1024x1024": (1024, 1024),
    "瓦片集 512x512": (512, 512),
    "横向 16:9": (896, 512),
    "纵向 9:16": (512, 896),
}
