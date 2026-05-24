"""M3: Batch generation and asset packaging for game development workflows."""

import io
import os
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from PIL import Image

from modules.generator import text_to_image
from modules.style_templates import build_styled_prompt

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "outputs")

# 北京时间
TZ_BEIJING = timezone(timedelta(hours=8))


@dataclass
class BatchResult:
    images: list[Image.Image]
    prompts: list[str]
    elapsed_ms: int
    style_name: str = ""


def batch_generate(
    subjects: list[str],
    style_template: str = "pixel-art",
    negative_prompt: str = "",
    width: int = 256,
    height: int = 256,
    steps: int = 30,
    seed: int = 0,
) -> BatchResult:
    """
    批量生成：为一组主题生成风格统一的系列图像。
    """
    t0 = time.perf_counter()
    images: list[Image.Image] = []
    prompts: list[str] = []

    for i, subject in enumerate(subjects):
        try:
            prompt, neg, (rec_w, rec_h) = build_styled_prompt(subject, style_template)
            w = width or rec_w
            h = height or rec_h
            final_neg = negative_prompt or neg

            result = text_to_image(
                prompt=prompt,
                negative_prompt=final_neg,
                width=w,
                height=h,
                steps=steps,
                seed=seed + i,
            )
            images.append(result.image)
            prompts.append(prompt)
        except Exception as e:
            raise RuntimeError(
                f"批量生成失败（第 {i + 1}/{len(subjects)} 项 '{subject}'）: {e}"
            ) from e

    elapsed = int((time.perf_counter() - t0) * 1000)
    return BatchResult(
        images=images,
        prompts=prompts,
        elapsed_ms=elapsed,
        style_name=style_template,
    )


def _make_readme_md(style_name: str, subjects: list[str], colors: list[str] | None = None) -> str:
    """生成资源包的 README_assets.md 内容。"""
    now = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Asset Pack",
        "",
        f"**生成时间**: {now} (北京时间)",
        f"**风格模板**: {style_name}",
        f"**素材数量**: {len(subjects)}",
        f"**素材列表**: {', '.join(subjects)}",
        "",
    ]
    if colors:
        lines.append(f"**参考色板**: {', '.join(colors)}")
        lines.append("")

    lines += [
        "## 目录结构",
        "",
        "```",
        "assets/",
        "├── 1x/          # 原始尺寸 (游戏内实际使用)",
        "│   ├── asset_01.png",
        "│   ├── asset_02.png",
        "│   └── ...",
        "├── 2x/          # @2x 视网膜分辨率",
        "│   ├── asset_01@2x.png",
        "│   ├── asset_02@2x.png",
        "│   └── ...",
        "└── README_assets.md",
        "```",
        "",
        "## 使用说明",
        "",
        "1. 将 `1x/` 目录中的 PNG 文件导入游戏引擎的资源目录",
        "2. 如引擎支持 @2x 资源缩放（如 Unity / Godot），可将 `2x/` 一并导入",
        "3. 所有素材均为透明背景 PNG，可直接用于 Sprite Renderer",
        "",
        "## 兼容引擎",
        "",
        "- Unity 2D (Sprite Renderer)",
        "- Godot (Sprite2D)",
        "- Cocos Creator",
        "- RPG Maker",
        "- GameMaker Studio",
        "",
    ]
    return "\n".join(lines)


def export_asset_pack(
    images: list[Image.Image],
    subjects: list[str],
    style_name: str = "pixel-art",
    colors: list[str] | None = None,
) -> str:
    """
    将生成的图像打包为 ZIP 文件。

    目录结构:
        assets/
          ├── 1x/          # 原始尺寸
          ├── 2x/          # 2x 放大（使用 LANCZOS）
          └── README_assets.md

    返回 ZIP 文件路径。
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now(TZ_BEIJING).strftime("%Y%m%d_%H%M%S")
    zip_name = f"assets_{style_name}_{timestamp}.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # README
        readme = _make_readme_md(style_name, subjects, colors)
        zf.writestr("assets/README_assets.md", readme)

        for i, img in enumerate(subjects):
            image = images[i]
            safe_name = _sanitize_filename(subjects[i])
            file_name = f"asset_{i + 1:02d}_{safe_name}"

            # 1x
            buf_1x = io.BytesIO()
            image.save(buf_1x, format="PNG")
            zf.writestr(f"assets/1x/{file_name}.png", buf_1x.getvalue())

            # 2x
            w2, h2 = image.size[0] * 2, image.size[1] * 2
            img_2x = image.resize((w2, h2), Image.LANCZOS)
            buf_2x = io.BytesIO()
            img_2x.save(buf_2x, format="PNG")
            zf.writestr(f"assets/2x/{file_name}@2x.png", buf_2x.getvalue())

    return zip_path


def _sanitize_filename(name: str) -> str:
    """将任意字符串转为安全的文件名。"""
    import re
    safe = re.sub(r"[^\w一-鿿\-]", "_", name.strip())
    safe = safe.strip("_") or "asset"
    return safe[:30]
