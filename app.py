"""AssetCraft Studio — AI 原生产品设计师的 2D 游戏素材工作流引擎."""

import os
import gradio as gr

from dotenv import load_dotenv

load_dotenv()

from modules.generator import (
    SIZE_PRESETS,
    text_to_image,
    image_to_image,
)
from modules.palette import extract_palette, palette_to_html
from modules.style_templates import (
    list_templates,
    build_styled_prompt,
    palette_to_style_hint,
)
from modules.exporter import batch_generate, export_asset_pack

# 风格模板选项列表
TEMPLATE_LIST = list_templates()
TEMPLATE_CHOICES = [t["label"] for t in TEMPLATE_LIST]
TEMPLATE_NAME_MAP = {t["label"]: t["name"] for t in TEMPLATE_LIST}
SIZE_CHOICES = list(SIZE_PRESETS.keys())

CSS = """
.gradio-container { max-width: 960px !important; margin: 0 auto !important; }
.palette-box { min-height: 90px; }
footer { visibility: hidden; }
"""


def _parse_size(size_choice: str) -> tuple[int, int]:
    return SIZE_PRESETS.get(size_choice, (512, 512))


# ── Tab 1: 文生图 ──────────────────────────────────────────────

def on_text_to_image(
    prompt: str,
    negative_prompt: str,
    size_choice: str,
    steps: int,
    cfg_scale: float,
    seed: int,
    style_template: str,
):
    if not prompt.strip():
        return None, "请输入提示词。"
    try:
        w, h = _parse_size(size_choice)
        final_prompt = prompt
        final_negative = negative_prompt

        if style_template and style_template != "无":
            tmpl_name = TEMPLATE_NAME_MAP[style_template]
            final_prompt, tmpl_neg, (rec_w, rec_h) = build_styled_prompt(prompt, tmpl_name)
            final_negative = negative_prompt or tmpl_neg
            if size_choice == "正方形 512x512":
                w, h = rec_w, rec_h

        result = text_to_image(
            prompt=final_prompt,
            negative_prompt=final_negative,
            width=w,
            height=h,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
        )
        return result.image, f"生成成功 | 种子: {result.seed} | 耗时: {result.elapsed_ms}ms"
    except Exception as e:
        return None, f"错误: {e}"


# ── Tab 2: 图生图 ──────────────────────────────────────────────

def on_image_to_image(
    prompt: str,
    init_image,
    negative_prompt: str,
    image_strength: float,
    size_choice: str,
    steps: int,
    cfg_scale: float,
    seed: int,
):
    if init_image is None:
        return None, "请上传一张参考图。"
    if not prompt.strip():
        return None, "请输入提示词。"
    try:
        w, h = _parse_size(size_choice)
        result = image_to_image(
            prompt=prompt,
            init_image=init_image,
            negative_prompt=negative_prompt,
            image_strength=image_strength,
            width=w,
            height=h,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
        )
        return result.image, f"风格转换成功 | 种子: {result.seed} | 耗时: {result.elapsed_ms}ms"
    except Exception as e:
        return None, f"错误: {e}"


# ── Tab 3: 设计协调器 ──────────────────────────────────────────

def on_extract_palette(ref_image):
    if ref_image is None:
        return "", "请上传一张参考图。"
    try:
        colors = extract_palette(ref_image)
        html = palette_to_html(colors)
        hex_list = [c["hex"] for c in colors]
        hex_text = ", ".join(hex_list)
        return html, f"已提取 {len(colors)} 种颜色: {hex_text}"
    except Exception as e:
        return "", f"错误: {e}"


def on_apply_palette_style(ref_image, style_template, subject):
    """基于提取的调色板 + 风格模板生成图片。"""
    if ref_image is None:
        return None, "请先上传参考图提取色板。"
    if not subject.strip():
        return None, "请输入要生成的素材名称。"
    if not style_template or style_template == "无":
        return None, "请选择一个风格模板。"
    try:
        colors = extract_palette(ref_image)
        hex_list = [c["hex"] for c in colors]
        tmpl_name = TEMPLATE_NAME_MAP.get(style_template, "pixel-art")
        prompt, neg, (w, h) = build_styled_prompt(subject, tmpl_name, hex_list)
        result = text_to_image(prompt=prompt, negative_prompt=neg, width=w, height=h)
        return result.image, f"生成成功 | 色板: {', '.join(hex_list[:5])}"
    except Exception as e:
        return None, f"错误: {e}"


# ── Tab 4: 批量导出 ────────────────────────────────────────────

def on_batch_generate(subjects_text: str, style_template: str, negative_prompt: str, seed: int):
    subjects = [s.strip() for s in subjects_text.split("\n") if s.strip()]
    if not subjects:
        return [], "请输入至少一个素材名称，每行一个。", None
    if len(subjects) > 20:
        return [], "一次最多生成 20 个素材。", None
    tmpl_name = TEMPLATE_NAME_MAP.get(style_template, "pixel-art")
    try:
        result = batch_generate(
            subjects=subjects,
            style_template=tmpl_name,
            negative_prompt=negative_prompt,
            seed=seed,
        )
        info = f"批量生成完毕 | {len(result.images)} 张图片 | 耗时: {result.elapsed_ms}ms"

        zip_path = export_asset_pack(
            images=result.images,
            subjects=subjects,
            style_name=tmpl_name,
        )
        return result.images, info, zip_path
    except Exception as e:
        return [], f"错误: {e}", None


# ── Gradio UI ───────────────────────────────────────────────────

def create_ui():
    with gr.Blocks(title="AssetCraft Studio") as app:
        gr.Markdown(
            """# AssetCraft Studio
### 为 AI 原生产品设计师打造的 2D 游戏素材工作流引擎
上传参考图 → 提取色板 → 选择风格 → 批量生成 → 一键打包，让创意概念无缝转化为可交付的游戏资产。
"""
        )

        with gr.Tabs():
            # ── Tab 1: 文生图 ──
            with gr.TabItem("文生图 (Text-to-Image)"):
                with gr.Row():
                    with gr.Column(scale=1):
                        prompt = gr.Textbox(
                            label="提示词 (Prompt)",
                            placeholder="描述你想要生成的游戏素材，例如: a golden sword icon for RPG game, pixel art style...",
                            lines=3,
                        )
                        negative_prompt = gr.Textbox(
                            label="负面提示词 (Negative Prompt)",
                            placeholder="不希望出现的元素...",
                            lines=2,
                        )
                        with gr.Row():
                            size_choice = gr.Dropdown(
                                label="尺寸",
                                choices=SIZE_CHOICES,
                                value="正方形 512x512",
                            )
                            style_template = gr.Dropdown(
                                label="风格模板 (可选)",
                                choices=["无"] + TEMPLATE_CHOICES,
                                value="无",
                            )
                        with gr.Row():
                            steps = gr.Slider(10, 50, value=30, step=1, label="采样步数 (Steps)")
                            cfg_scale = gr.Slider(1.0, 15.0, value=7.0, step=0.5, label="CFG Scale")
                        seed = gr.Number(label="随机种子 (Seed, 0=随机)", value=0, precision=0)
                        btn_generate = gr.Button("生成", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        output_t2i = gr.Image(label="生成结果", type="pil", height=400)
                        status_t2i = gr.Textbox(label="状态", interactive=False)

                btn_generate.click(
                    fn=on_text_to_image,
                    inputs=[prompt, negative_prompt, size_choice, steps, cfg_scale, seed, style_template],
                    outputs=[output_t2i, status_t2i],
                )

            # ── Tab 2: 图生图 ──
            with gr.TabItem("图生图 (Image-to-Image)"):
                with gr.Row():
                    with gr.Column(scale=1):
                        init_image = gr.Image(label="参考图", type="pil", height=300)
                        prompt_i2i = gr.Textbox(
                            label="提示词",
                            placeholder="描述目标风格...",
                            lines=3,
                        )
                        negative_i2i = gr.Textbox(label="负面提示词", lines=2)
                        strength = gr.Slider(
                            0.1, 0.9, value=0.35, step=0.05,
                            label="风格强度 (Image Strength) — 越小越接近原图",
                        )
                        size_i2i = gr.Dropdown(
                            label="输出尺寸", choices=SIZE_CHOICES, value="正方形 512x512"
                        )
                        with gr.Row():
                            steps_i2i = gr.Slider(10, 50, value=30, step=1, label="Steps")
                            cfg_i2i = gr.Slider(1.0, 15.0, value=7.0, step=0.5, label="CFG Scale")
                        seed_i2i = gr.Number(label="Seed", value=0, precision=0)
                        btn_i2i = gr.Button("风格转换", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        output_i2i = gr.Image(label="生成结果", type="pil", height=400)
                        status_i2i = gr.Textbox(label="状态", interactive=False)

                btn_i2i.click(
                    fn=on_image_to_image,
                    inputs=[prompt_i2i, init_image, negative_i2i, strength, size_i2i, steps_i2i, cfg_i2i, seed_i2i],
                    outputs=[output_i2i, status_i2i],
                )

            # ── Tab 3: 设计协调器 ──
            with gr.TabItem("设计协调器 (Design Coordinator)"):
                gr.Markdown("### 灵感 → 色板 → 风格化素材")
                with gr.Row():
                    with gr.Column(scale=1):
                        ref_image = gr.Image(label="1. 上传参考图", type="pil", height=250)
                        btn_extract = gr.Button("提取调色板", variant="secondary")
                        palette_display = gr.HTML(label="提取的色板", elem_classes=["palette-box"])

                    with gr.Column(scale=1):
                        coord_subject = gr.Textbox(
                            label="2. 素材描述",
                            placeholder="例如: shop icon, backpack icon, quest log icon...",
                            lines=2,
                        )
                        coord_style = gr.Dropdown(
                            label="3. 选择风格模板",
                            choices=TEMPLATE_CHOICES,
                            value=TEMPLATE_CHOICES[0],
                        )
                        btn_coord_generate = gr.Button("生成风格化素材", variant="primary", size="lg")
                        coord_output = gr.Image(label="生成结果", type="pil", height=300)
                        coord_status = gr.Textbox(label="状态", interactive=False)

                btn_extract.click(
                    fn=on_extract_palette,
                    inputs=[ref_image],
                    outputs=[palette_display, coord_status],
                )
                btn_coord_generate.click(
                    fn=on_apply_palette_style,
                    inputs=[ref_image, coord_style, coord_subject],
                    outputs=[coord_output, coord_status],
                )

            # ── Tab 4: 批量导出 ──
            with gr.TabItem("批量导出 (Batch Export)"):
                gr.Markdown("### 批量生成 + 一键打包为 Unity/Godot 就绪的资源包")
                with gr.Row():
                    with gr.Column(scale=1):
                        batch_subjects = gr.Textbox(
                            label="素材列表 (每行一个)",
                            placeholder="shop icon\nbackpack icon\nquest log icon\nsword icon\npotion icon",
                            lines=8,
                        )
                        batch_style = gr.Dropdown(
                            label="风格模板",
                            choices=TEMPLATE_CHOICES,
                            value=TEMPLATE_CHOICES[0],
                        )
                        batch_neg = gr.Textbox(label="全局负面提示词 (可选)", lines=2)
                        batch_seed = gr.Number(label="基础种子", value=42, precision=0)
                        btn_batch = gr.Button("批量生成并打包", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        batch_gallery = gr.Gallery(
                            label="生成的素材", columns=3, height=400,
                        )
                        batch_status = gr.Textbox(label="状态", interactive=False)
                        batch_download = gr.File(label="下载资源包 (ZIP)", file_count="single")

                btn_batch.click(
                    fn=on_batch_generate,
                    inputs=[batch_subjects, batch_style, batch_neg, batch_seed],
                    outputs=[batch_gallery, batch_status, batch_download],
                )

        gr.Markdown(
            """---
### 使用流程
1. **文生图** — 描述素材内容，直接生成
2. **图生图** — 上传参考图进行风格迁移
3. **设计协调器** — 上传截图提取色板 → 基于色板生成风格统一素材（核心亮点）
4. **批量导出** — 输入系列素材列表 → 一键打包为引擎就绪资源包
"""
        )

    return app


# ── Entry point ─────────────────────────────────────────────────

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
