"""PixelForge AI — 2D 游戏专用提示词引擎."""

from dataclasses import dataclass, field
from typing import Optional

from config import GAME_STYLES, ASSET_TYPES


@dataclass
class PromptTemplate:
    """单个提示词模板。"""
    name: str
    label: str
    genre: str  # rpg, platformer, puzzle, shooter, strategy
    template_cn: str  # 中文模板
    template_en: str  # 英文模板
    negative: str = ""
    tags: list[str] = field(default_factory=list)


# ── 预置模板库 ─────────────────────────────────────────────────

BUILTIN_TEMPLATES: dict[str, PromptTemplate] = {
    # ── RPG ──
    "rpg_sword": PromptTemplate(
        name="rpg_sword",
        label="RPG 武器",
        genre="rpg",
        template_cn="{style}风格的{subject}，奇幻RPG游戏武器，精致金属质感",
        template_en="{style} style {subject}, fantasy RPG weapon, "
        "detailed metal texture, glowing enchantment",
        negative="modern gun, sci-fi, realistic photo, broken, damaged",
        tags=["weapon", "equipment", "fantasy"],
    ),
    "rpg_potion": PromptTemplate(
        name="rpg_potion",
        label="RPG 药水",
        genre="rpg",
        template_cn="{style}风格的{subject}药水，玻璃瓶装，发光液体，游戏物品图标",
        template_en="{style} style {subject} potion, glass bottle, "
        "glowing liquid, game item icon, magical",
        negative="plastic bottle, modern container, broken glass",
        tags=["consumable", "item", "fantasy"],
    ),
    "rpg_character": PromptTemplate(
        name="rpg_character",
        label="RPG 角色",
        genre="rpg",
        template_cn="{style}风格的游戏角色{subject}，全身站立姿态，正面视图，角色设计",
        template_en="{style} style game character {subject}, "
        "full body standing pose, front view, character design sheet",
        negative="realistic human, photograph, distorted anatomy, blurry",
        tags=["character", "npc", "hero"],
    ),
    # ── 平台跳跃 ──
    "platform_tile": PromptTemplate(
        name="platform_tile",
        label="平台瓦片",
        genre="platformer",
        template_cn="{style}风格的平台游戏{subject}瓦片，可平铺，侧面视角",
        template_en="{style} style platformer {subject} tile, "
        "seamless tileable, side view, game level design",
        negative="3D, perspective, top-down, realistic texture",
        tags=["tile", "platform", "environment"],
    ),
    "platform_coin": PromptTemplate(
        name="platform_coin",
        label="收集金币",
        genre="platformer",
        template_cn="{style}风格的金币道具，旋转动画帧，平台游戏收集品",
        template_en="{style} style gold coin pickup, "
        "spinning animation frame, platformer collectible",
        negative="realistic currency, modern money, dark",
        tags=["pickup", "collectible", "item"],
    ),
    # ── UI 通用 ──
    "ui_button": PromptTemplate(
        name="ui_button",
        label="UI 按钮",
        genre="ui",
        template_cn="{style}风格的{subject}按钮，游戏UI元素，简洁清晰",
        template_en="{style} style {subject} button, "
        "game UI element, clean and clear, interactive state",
        negative="web design, mobile app, photorealistic, 3D button",
        tags=["ui", "button", "interface"],
    ),
    "ui_icon": PromptTemplate(
        name="ui_icon",
        label="UI 图标",
        genre="ui",
        template_cn="{style}风格的{subject}图标，游戏界面小图标，可识别性强",
        template_en="{style} style {subject} icon, "
        "game UI small icon, highly recognizable, minimalist",
        negative="complex scene, text labels, photorealistic",
        tags=["ui", "icon", "interface"],
    ),
    # ── 特效 ──
    "vfx_explosion": PromptTemplate(
        name="vfx_explosion",
        label="爆炸特效",
        genre="vfx",
        template_cn="{style}风格的爆炸特效序列帧，2D游戏视觉特效",
        template_en="{style} style explosion effect sprite sheet, "
        "2D game VFX, animated frames, particle burst",
        negative="realistic explosion, 3D particles, slow motion photo",
        tags=["vfx", "explosion", "animation"],
    ),
    "vfx_magic": PromptTemplate(
        name="vfx_magic",
        label="魔法特效",
        genre="vfx",
        template_cn="{style}风格的魔法{subject}特效，光效粒子，2D游戏法术",
        template_en="{style} style magic {subject} effect, "
        "glowing particles, 2D game spell, ethereal light",
        negative="realistic fire, smoke, 3D particles",
        tags=["vfx", "magic", "spell"],
    ),
    # ── 环境 ──
    "env_tree": PromptTemplate(
        name="env_tree",
        label="环境树木",
        genre="environment",
        template_cn="{style}风格的游戏场景{subject}树木，2D游戏环境素材",
        template_en="{style} style game environment {subject} tree, "
        "2D game background asset, scenic",
        negative="3D tree, realistic photo, winter dead tree",
        tags=["environment", "nature", "background"],
    ),
}


class PromptEngine:
    """2D 游戏专用提示词引擎。

    提供预置模板 + 参数化构建 + 批量生成提示词列表。
    """

    def __init__(self):
        self.templates = dict(BUILTIN_TEMPLATES)

    # ── 公开 API ──────────────────────────────────────────────

    def build(
        self,
        subject: str,
        template_name: str = "rpg_sword",
        style: str = "pixel_art",
        language: str = "en",
    ) -> str:
        """使用指定模板构建提示词。

        Args:
            subject: 素材主题（如 "golden sword", "红色药水"）
            template_name: 模板名称
            style: 风格键名
            language: "en" 英文 / "cn" 中文
        """
        tmpl = self.templates.get(template_name)
        if tmpl is None:
            available = ", ".join(self.templates.keys())
            raise ValueError(f"未知模板 '{template_name}'。可用: {available}")

        style_cfg = GAME_STYLES.get(style, {})
        style_label = style_cfg.get("label", style)

        if language == "cn":
            text = tmpl.template_cn.format(style=style_label, subject=subject)
        else:
            text = tmpl.template_en.format(style=style_label, subject=subject)

        # 追加风格前缀/后缀
        prefix = style_cfg.get("prefix", "")
        suffix = style_cfg.get("suffix", "")
        return f"{prefix}{text}{suffix}"

    def build_negative(self, template_name: str, style: str = "pixel_art") -> str:
        """构建负面提示词（模板 + 风格合并）。"""
        tmpl = self.templates.get(template_name)
        style_cfg = GAME_STYLES.get(style, {})

        parts = []
        if style_cfg.get("negative"):
            parts.append(style_cfg["negative"])
        if tmpl and tmpl.negative:
            parts.append(tmpl.negative)
        return ", ".join(parts)

    def build_batch(
        self,
        subjects: list[str],
        template_name: str = "rpg_sword",
        style: str = "pixel_art",
        language: str = "en",
    ) -> list[str]:
        """为多个主题批量构建提示词，保证风格一致。"""
        return [self.build(s, template_name, style, language) for s in subjects]

    def list_templates(self, genre: Optional[str] = None) -> list[dict]:
        """列出可用模板，可按类型筛选。"""
        result = []
        for name, tmpl in self.templates.items():
            if genre and tmpl.genre != genre:
                continue
            result.append({
                "name": name,
                "label": tmpl.label,
                "genre": tmpl.genre,
                "tags": tmpl.tags,
            })
        return result

    def get_genres(self) -> list[str]:
        """返回所有可用类型。"""
        return sorted(set(t.genre for t in self.templates.values()))

    def register_template(self, tmpl: PromptTemplate) -> None:
        """注册自定义模板。"""
        self.templates[tmpl.name] = tmpl
