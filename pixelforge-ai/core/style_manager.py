"""PixelForge AI — 风格一致性管理器."""

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Optional

from config import GAME_STYLES


@dataclass
class StyleProfile:
    """风格配置档案。"""
    name: str
    label: str
    seed_base: int  # 基础种子，确保系列素材风格一致
    cfg_scale: float = 7.5
    steps: int = 20
    width: int = 256
    height: int = 256
    extra_tags: list[str] = field(default_factory=list)

    def seed_for(self, index: int) -> int:
        """为系列中的第 N 个素材生成确定性种子。"""
        return self.seed_base + index


class StyleManager:
    """风格一致性管理器。

    确保批量生成的素材保持统一的视觉风格：
    - 相同的基础种子 → 风格一致
    - 递增的派生种子 → 内容差异
    - 风格档案复用 → 跨批次一致性
    """

    def __init__(self):
        self._profiles: dict[str, StyleProfile] = {}

    # ── 公开 API ──────────────────────────────────────────────

    def create_profile(
        self,
        name: str,
        style: str = "pixel_art",
        seed_base: Optional[int] = None,
        cfg_scale: float = 7.5,
        steps: int = 20,
        width: int = 256,
        height: int = 256,
    ) -> StyleProfile:
        """创建一个风格档案，用于系列素材生成。

        Args:
            name: 档案名称（如 "rpg_icons_set"）
            style: 风格键名
            seed_base: 基础种子（None=随机）
            cfg_scale: 提示词遵循度 (1-20)
            steps: 推理步数
            width/height: 统一输出尺寸
        """
        if seed_base is None:
            seed_base = random.randint(0, 999999999)

        style_cfg = GAME_STYLES.get(style, {})
        profile = StyleProfile(
            name=name,
            label=style_cfg.get("label", style),
            seed_base=seed_base,
            cfg_scale=cfg_scale,
            steps=steps,
            width=width,
            height=height,
        )
        self._profiles[name] = profile
        return profile

    def get_profile(self, name: str) -> Optional[StyleProfile]:
        """获取已创建的风格档案。"""
        return self._profiles.get(name)

    def list_profiles(self) -> list[str]:
        """列出所有档案名称。"""
        return list(self._profiles.keys())

    def generate_seeds(self, profile_name: str, count: int) -> list[int]:
        """为批量生成生成确定性的种子序列。

        相同档案 + 相同 count → 相同种子序列（可复现）。
        """
        profile = self._profiles.get(profile_name)
        if profile is None:
            raise ValueError(f"档案不存在: {profile_name}")
        return [profile.seed_for(i) for i in range(count)]

    def derive_profile(
        self,
        base_name: str,
        new_name: str,
        **overrides,
    ) -> StyleProfile:
        """基于已有档案创建变体（保持风格一致，调整部分参数）。"""
        base = self._profiles.get(base_name)
        if base is None:
            raise ValueError(f"基础档案不存在: {base_name}")

        # 使用相同 seed_base 保证风格连贯
        kwargs = {
            "name": new_name,
            "label": base.label,
            "seed_base": base.seed_base,
            "cfg_scale": base.cfg_scale,
            "steps": base.steps,
            "width": base.width,
            "height": base.height,
            "extra_tags": list(base.extra_tags),
        }
        kwargs.update(overrides)
        kwargs["name"] = new_name  # name 不可覆盖

        profile = StyleProfile(**kwargs)
        self._profiles[new_name] = profile
        return profile

    @staticmethod
    def make_seed_from_string(text: str) -> int:
        """从字符串生成确定性种子（相同输入 → 相同种子）。"""
        h = hashlib.md5(text.encode()).hexdigest()
        return int(h[:8], 16)

    @staticmethod
    def timestamp_seed() -> int:
        """基于时间戳生成种子。"""
        return int(time.time() * 1000) % 999999999

    # ── 多图风格一致性增强 ──────────────────────────────────

    def lock_style(
        self,
        profile_name: str,
        style: str = "pixel_art",
        width: int = 256,
        height: int = 256,
        **kwargs,
    ) -> StyleProfile:
        """锁定一个风格档案，后续所有生成使用相同的种子基。

        确保跨批次生成的多组素材保持视觉风格统一。
        """
        seed_base = kwargs.pop("seed_base", None) or self.make_seed_from_string(profile_name)
        return self.create_profile(
            profile_name, style=style,
            seed_base=seed_base, width=width, height=height, **kwargs,
        )

    def consistent_seed_sequence(self, profile_name: str, group_count: int, items_per_group: int) -> list[list[int]]:
        """为多组素材生成一致的种子序列。

        每组有独立的基础种子（组间差异），
        但组内种子递增一致（组内连贯）。
        """
        seeds = []
        for g in range(group_count):
            group_base = self.make_seed_from_string(f"{profile_name}_group_{g}")
            group_seeds = [group_base + i for i in range(items_per_group)]
            seeds.append(group_seeds)
        return seeds

    def get_or_create_profile(self, name: str, **kwargs) -> StyleProfile:
        """获取已有档案，不存在则创建。"""
        existing = self.get_profile(name)
        if existing:
            return existing
        return self.create_profile(name, **kwargs)
