"""M2: Style prompt templates for consistent asset generation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StyleTemplate:
    name: str
    label: str
    description: str
    style_prefix: str
    style_suffix: str = ""
    negative_prompt: str = ""
    recommended_size: tuple[int, int] = (512, 512)


STYLE_TEMPLATES: dict[str, StyleTemplate] = {
    "pixel-art": StyleTemplate(
        name="pixel-art",
        label="复古像素风 (Pixel Art)",
        description="经典 16-bit 像素游戏风格，清晰的像素边缘、有限的调色板",
        style_prefix="pixel art, 16-bit retro game sprite, ",
        style_suffix=", clean pixel edges, limited color palette, game asset, "
        "on transparent background, sharp, highly detailed pixel art",
        negative_prompt="blurry, smooth gradients, photorealistic, 3D render, "
        "anti-aliasing, high resolution photo",
        recommended_size=(256, 256),
    ),
    "vector-flat": StyleTemplate(
        name="vector-flat",
        label="矢量扁平风 (Flat Vector)",
        description="现代扁平化 UI 图标风格，简洁几何形状、柔和色彩",
        style_prefix="flat vector art, clean minimalist icon design, ",
        style_suffix=", simple geometric shapes, pastel colors, 2D game UI element, "
        "clean lines, modern mobile game style, on transparent background",
        negative_prompt="3D, realistic, gradients, shadows, complex background, noisy",
        recommended_size=(512, 512),
    ),
    "sci-fi": StyleTemplate(
        name="sci-fi",
        label="科技蓝 (Sci-Fi Blue)",
        description="科幻感蓝黑色调，发光边缘、赛博朋克元素",
        style_prefix="sci-fi game asset, neon blue glow, cyberpunk style, dark theme, ",
        style_suffix=", glowing edges, high-tech UI element, holographic effect, "
        "on dark background, blue and cyan color scheme, futuristic",
        negative_prompt="natural lighting, warm colors, organic shapes, "
        "rustic, vintage, pastel, daylight",
        recommended_size=(512, 512),
    ),
    "hand-drawn": StyleTemplate(
        name="hand-drawn",
        label="手绘水彩风 (Hand-Drawn)",
        description="温暖的手绘水彩质感，柔和的轮廓线、自然纹理",
        style_prefix="hand-drawn watercolor style, sketchy illustration, ",
        style_suffix=", gentle ink outlines, watercolor texture, warm and cozy, "
        "storybook art style, soft edges, organic feel, indie game aesthetic",
        negative_prompt="digital art, sharp lines, vector, pixel perfect, "
        "synthetic, 3D, photorealistic",
        recommended_size=(512, 512),
    ),
    "stardew-like": StyleTemplate(
        name="stardew-like",
        label="星露谷温馨风 (Stardew-Like)",
        description="《星露谷物语》式的温馨像素 RPG 风格",
        style_prefix="Stardew Valley style, cozy farming RPG sprite, "
        "top-down view game asset, charming pixel art, ",
        style_suffix=", cute and cozy, warm earthy tones, 2D RPG icon, "
        "harvest moon inspired, isometric pixel art, game item sprite",
        negative_prompt="modern, realistic, 3D, dark, scary, violent, "
        "gritty, complex shading, noise",
        recommended_size=(256, 256),
    ),
    "dark-dungeon": StyleTemplate(
        name="dark-dungeon",
        label="暗黑地牢风 (Dark Dungeon)",
        description="哥特暗黑风格，烛光高对比、锈蚀金属质感、压抑氛围",
        style_prefix="dark dungeon crawler art, gothic horror game asset, "
        "torch-lit medieval fantasy, ",
        style_suffix=", high contrast chiaroscuro, rusted iron texture, "
        "gritty dark fantasy, deep shadows, candlelight glow, "
        "oppressive atmosphere, hand-drawn ink style, on dark background",
        negative_prompt="bright, cheerful, colorful, cartoon, cute, "
        "pastel, modern UI, clean and shiny, daylight, rainbow",
        recommended_size=(512, 512),
    ),
    "game-icon": StyleTemplate(
        name="game-icon",
        label="RPG 物品图标 (RPG Icons)",
        description="经典 RPG 物品栏图标，45度角透视、精致边框",
        style_prefix="RPG inventory icon, isometric game item, fantasy game asset, ",
        style_suffix=", detailed item icon, diablo-style item, golden border, "
        "game loot, magical glow, centered on transparent background, "
        "role playing game prop",
        negative_prompt="flat, modern UI, text, labels, realistic photo, background scene",
        recommended_size=(512, 512),
    ),
}


def list_templates() -> list[dict]:
    """返回所有可用风格模板的基本信息。"""
    return [
        {
            "name": t.name,
            "label": t.label,
            "description": t.description,
        }
        for t in STYLE_TEMPLATES.values()
    ]


def get_template(name: str) -> Optional[StyleTemplate]:
    return STYLE_TEMPLATES.get(name)


def build_styled_prompt(
    subject: str,
    template_name: str,
    palette_hex: Optional[list[str]] = None,
) -> tuple[str, str, tuple[int, int]]:
    """
    根据风格模板构建完整的提示词。

    返回 (完整提示词, 负面提示词, 推荐尺寸)。
    """
    template = get_template(template_name)
    if template is None:
        available = ", ".join(STYLE_TEMPLATES.keys())
        raise ValueError(f"未知风格模板 '{template_name}'。可用: {available}")

    prompt = f"{template.style_prefix}{subject}{template.style_suffix}"

    # 如果有调色板，在 prompt 末尾追加颜色引导
    if palette_hex:
        color_hint = ", color palette: " + ", ".join(palette_hex[:5])
        prompt += color_hint

    return prompt, template.negative_prompt, template.recommended_size


def palette_to_style_hint(colors: list[dict]) -> str:
    """根据调色板生成风格化的颜色描述文本。"""
    if not colors:
        return ""
    hex_list = [c["hex"] for c in colors[:5]]
    return ", ".join(hex_list)
