"""PixelForge AI — 2D 游戏素材生成器 Web 界面."""

import os
import gradio as gr

from config import GAME_STYLES, ASSET_TYPES, SIZE_PRESETS
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
TEMPLATE_CHOICES = [t["label"] for t in prompt_engine.list_templates()]
TEMPLATE_KEY_MAP = {t["label"]: t["name"] for t in prompt_engine.list_templates()}
SIZE_CHOICES = list(SIZE_PRESETS.keys())
EXPORT_ENGINES = ["Unity", "Godot", "Cocos Creator"]

CSS = """
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }
footer { visibility: hidden; }
"""


# ── 通用生成逻辑 ──────────────────────────────────────────────

def _parse_size(choice: str):
    return SIZE_PRESETS.get(choice, (256, 256))


def _parse_style(label: str) -> str:
    return STYLE_KEY_MAP.get(label, "pixel_art")


def _parse_template(label: str) -> str:
    return TEMPLATE_KEY_MAP.get(label, "rpg_sword")


def _get_exporter(engine: str, output_root: str = "static/exports"):
    if engine == "Unity":
        return UnityExporter(output_root=output_root)
    elif engine == "Godot":
        return GodotExporter(output_root=output_root)
    else:
        return CocosExporter(output_root=output_root)


def on_generate(prompt_text, style_label, template_label, negative, size_choice, seed,
                progress=gr.Progress()):
    """通用生成函数 — 所有 Tab 共用。"""
    if not prompt_text.strip():
        return None, "请输入素材描述", None

    style = _parse_style(style_label)
    tmpl = _parse_template(template_label)
    w, h = _parse_size(size_choice)

    progress(0.1, desc="构建提示词...")
    full_prompt = prompt_engine.build(prompt_text, tmpl, style)
    full_neg = negative or prompt_engine.build_negative(tmpl, style)

    progress(0.3, desc="调用 AI 生成中...")
    try:
        result = generator.generate_sprite(
            prompt=full_prompt,
            style=style,
            asset_type="sprite",
            width=w, height=h,
            negative_prompt=full_neg,
            seed=int(seed or 0),
        )
    except Exception as e:
        return None, f"生成失败: {str(e)[:200]}", None

    progress(0.9, desc="处理结果...")
    info = f"生成成功 | {result.elapsed_ms / 1000:.1f}s | {w}×{h} | seed={result.seed} | backend={result.backend}"
    progress(1.0, desc="完成")
    return result.image, info, None


def on_export(image, engine_choice, name, progress=gr.Progress()):
    """导出当前图片到指定引擎。"""
    if image is None:
        return None, "请先生成素材"
    if not name.strip():
        name = "asset"

    progress(0.2, desc="创建引擎资源...")
    exporter = _get_exporter(engine_choice)
    exporter.export_sprite(image, name.strip(), "sprite", "pixel_art")

    progress(0.7, desc="打包 ZIP...")
    result = exporter.finalize()

    progress(1.0, desc="导出完成")
    return result.zip_path, f"已导出: {os.path.basename(result.zip_path)}"


# ── 构建单个 Tab 的控件 ────────────────────────────────────────

def _build_generation_tab(asset_label: str):
    """构建一个完整的素材生成 Tab，返回所有组件。"""
    with gr.Row():
        with gr.Column(scale=1):
            style_dd = gr.Dropdown(
                label="风格", choices=STYLE_CHOICES, value=STYLE_CHOICES[0])
            template_dd = gr.Dropdown(
                label="提示词模板", choices=TEMPLATE_CHOICES, value=TEMPLATE_CHOICES[0])
            prompt_tb = gr.Textbox(
                label="素材描述", placeholder=f"描述你要生成的{asset_label}...", lines=3)
            negative_tb = gr.Textbox(
                label="负面提示词 (可选)", placeholder="不希望出现的元素...", lines=2)
            with gr.Row():
                size_dd = gr.Dropdown(
                    label="尺寸", choices=SIZE_CHOICES, value=SIZE_CHOICES[3])
                seed_num = gr.Number(label="Seed (0=随机)", value=0, precision=0)
            btn_gen = gr.Button("生成", variant="primary", size="lg")

        with gr.Column(scale=1):
            output_img = gr.Image(label="生成结果", type="pil", height=350)
            status_txt = gr.Textbox(label="状态", interactive=False)
            with gr.Row():
                engine_dd = gr.Dropdown(
                    label="导出引擎", choices=EXPORT_ENGINES, value="Unity")
                name_tb = gr.Textbox(label="素材名称", value="my_asset")
            btn_export = gr.Button("导出资源包", variant="secondary")
            download_file = gr.File(label="下载", file_count="single")

    btn_gen.click(
        fn=on_generate,
        inputs=[prompt_tb, style_dd, template_dd, negative_tb, size_dd, seed_num],
        outputs=[output_img, status_txt, download_file],
    )
    btn_export.click(
        fn=on_export,
        inputs=[output_img, engine_dd, name_tb],
        outputs=[download_file, status_txt],
    )


# ── 主 UI ──────────────────────────────────────────────────────

def create_ui():
    with gr.Blocks(title="PixelForge AI") as app:
        gr.Markdown("""# PixelForge AI
### 2D 游戏素材生成器 — 一键生成 · 多引擎导出 · 风格统一
""")

        with gr.Tabs():
            with gr.TabItem("精灵生成 (Sprite)"):
                gr.Markdown("### 角色 · 道具 · NPC")
                _build_generation_tab("游戏精灵")

            with gr.TabItem("瓦片生成 (Tileset)"):
                gr.Markdown("### 地形 · 建筑 · 场景")
                _build_generation_tab("地图瓦片")

            with gr.TabItem("UI 生成 (UI Element)"):
                gr.Markdown("### 按钮 · 面板 · 图标")
                _build_generation_tab("UI 元素")

            with gr.TabItem("特效生成 (VFX)"):
                gr.Markdown("### 粒子 · 爆炸 · 魔法")
                _build_generation_tab("视觉特效")

    return app


if __name__ == "__main__":
    import os as _os
    _os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,0.0.0.0")
    _os.environ.setdefault("no_proxy", "localhost,127.0.0.1,0.0.0.0")

    app = create_ui()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False)
