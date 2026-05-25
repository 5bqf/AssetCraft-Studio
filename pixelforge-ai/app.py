"""PixelForge AI — 2D 游戏素材生成器 Web 界面."""

import os
import gradio as gr

from config import Config, GAME_STYLES, ASSET_TYPES, SIZE_PRESETS
from core.generator import GameAssetGenerator
from core.prompt_engine import PromptEngine
from core.style_manager import StyleManager
from exporters.unity_exporter import UnityExporter
from exporters.godot_exporter import GodotExporter
from exporters.cocos_exporter import CocosExporter

# ── 全局实例 ───────────────────────────────────────────────────
generator = GameAssetGenerator()
prompt_engine = PromptEngine()
style_manager = StyleManager()

STYLE_CHOICES = [v["label"] for v in GAME_STYLES.values()]
STYLE_KEY_MAP = {v["label"]: k for k, v in GAME_STYLES.items()}
ASSET_CHOICES = [v["label"] for v in ASSET_TYPES.values()]
ASSET_KEY_MAP = {v["label"]: k for k, v in ASSET_TYPES.items()}
SIZE_CHOICES = list(SIZE_PRESETS.keys())
TEMPLATE_LIST = prompt_engine.list_templates()
TEMPLATE_CHOICES = [t["label"] for t in TEMPLATE_LIST]
TEMPLATE_KEY_MAP = {t["label"]: t["name"] for t in TEMPLATE_LIST}

CSS = """
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }
footer { visibility: hidden; }
"""


def create_ui():
    theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")

    with gr.Blocks(title="PixelForge AI") as app:
        gr.Markdown(
            """# PixelForge AI
### 2D 游戏素材生成器 — 一键生成 · 多引擎导出 · 风格统一
""")

        with gr.Tabs():
            with gr.TabItem("精灵生成 (Sprite)"):
                gr.Markdown("### 生成游戏精灵 — 角色、道具、NPC")

            with gr.TabItem("瓦片生成 (Tileset)"):
                gr.Markdown("### 生成地图瓦片 — 地形、建筑、场景")

            with gr.TabItem("UI 生成 (UI Element)"):
                gr.Markdown("### 生成 UI 元素 — 按钮、面板、图标")

            with gr.TabItem("特效生成 (VFX)"):
                gr.Markdown("### 生成视觉特效 — 粒子、爆炸、魔法")

    return app


if __name__ == "__main__":
    app = create_ui()
    port = int(os.getenv("PORT", "7860"))
    theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")
    app.queue(max_size=20).launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        theme=theme,
        css=CSS,
    )
