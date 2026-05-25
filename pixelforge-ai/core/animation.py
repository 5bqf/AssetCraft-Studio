"""PixelForge AI — 动画序列生成器."""

import time
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image

from .generator import GameAssetGenerator, GenerationResult
from .prompt_engine import PromptEngine
from .style_manager import StyleManager, StyleProfile


@dataclass
class AnimationResult:
    """动画生成结果。"""
    frames: list[Image.Image]
    frame_prompts: list[str]
    fps: int
    style: str
    total_elapsed_ms: int
    profile_name: str = ""


# 预设动画类型及其帧描述
ANIMATION_PRESETS = {
    "idle": {
        "label": "待机动画 (Idle)",
        "frames": 3,
        "fps": 6,
        "prompts": [
            "standing neutral pose, slight breathing",
            "standing neutral pose, subtle shift",
            "standing neutral pose, slight movement",
        ],
    },
    "walk": {
        "label": "行走动画 (Walk)",
        "frames": 4,
        "fps": 8,
        "prompts": [
            "walking step, left foot forward, arms swing",
            "walking step, mid stride, legs apart",
            "walking step, right foot forward, arms swing",
            "walking step, mid stride, legs together",
        ],
    },
    "attack": {
        "label": "攻击动画 (Attack)",
        "frames": 4,
        "fps": 10,
        "prompts": [
            "attack windup, weapon raised back, anticipation",
            "attack swing forward, weapon in motion, action",
            "attack impact, weapon striking, follow through",
            "attack recovery, returning to stance",
        ],
    },
    "jump": {
        "label": "跳跃动画 (Jump)",
        "frames": 4,
        "fps": 8,
        "prompts": [
            "jump start, crouching preparation",
            "jump rising, upward motion, stretching",
            "jump peak, highest point, airborne",
            "jump landing, descending, touching ground",
        ],
    },
    "spin": {
        "label": "旋转动画 (Spin)",
        "frames": 4,
        "fps": 10,
        "prompts": [
            "spinning start, slight rotation, 0 degrees",
            "spinning mid, 90 degrees rotated, side view",
            "spinning further, 180 degrees, back view",
            "spinning complete, 270 degrees, returning to front",
        ],
    },
}


class AnimationGenerator:
    """2D 游戏动画序列生成器。

    为角色/道具/特效生成连续动画帧。
    使用共享种子基 + 逐帧偏移确保帧间连贯性。
    """

    def __init__(self):
        self.generator = GameAssetGenerator()
        self.prompt_engine = PromptEngine()
        self.style_manager = StyleManager()

    def generate_animation(
        self,
        subject: str,
        anim_type: str = "idle",
        style: str = "pixel_art",
        width: int = 256,
        height: int = 256,
        profile_name: Optional[str] = None,
    ) -> AnimationResult:
        """生成一组动画序列帧。

        Args:
            subject: 动画主体描述（如 "knight character"）
            anim_type: 动画类型 (idle/walk/attack/jump/spin)
            style: 风格键名
            width/height: 帧尺寸
            profile_name: StyleManager 档案名（None=自动创建）

        Returns:
            AnimationResult 含帧列表 + 元数据
        """
        preset = ANIMATION_PRESETS.get(anim_type)
        if preset is None:
            available = ", ".join(ANIMATION_PRESETS.keys())
            raise ValueError(f"未知动画类型 '{anim_type}'。可用: {available}")

        # 创建风格档案
        if profile_name is None:
            profile_name = f"anim_{anim_type}_{int(time.time())}"
        profile = self.style_manager.create_profile(
            profile_name, style=style, width=width, height=height
        )
        seeds = self.style_manager.generate_seeds(profile_name, preset["frames"])

        t0 = time.perf_counter()
        frames: list[Image.Image] = []
        frame_prompts: list[str] = []

        for i, (frame_desc, seed) in enumerate(zip(preset["prompts"], seeds)):
            # 使用 RPG 角色模板
            full_prompt = self.prompt_engine.build(
                f"{subject}, {frame_desc}", "rpg_character", style
            )
            result = self.generator.generate_sprite(
                prompt=full_prompt,
                style=style,
                asset_type="sprite",
                width=width,
                height=height,
                seed=seed,
            )
            frames.append(result.image)
            frame_prompts.append(full_prompt)

        elapsed = int((time.perf_counter() - t0) * 1000)

        return AnimationResult(
            frames=frames,
            frame_prompts=frame_prompts,
            fps=preset["fps"],
            style=style,
            total_elapsed_ms=elapsed,
            profile_name=profile_name,
        )

    def generate_custom_animation(
        self,
        subject: str,
        frame_descriptions: list[str],
        fps: int = 8,
        style: str = "pixel_art",
        width: int = 256,
        height: int = 256,
    ) -> AnimationResult:
        """使用自定义帧描述生成动画。

        Args:
            subject: 动画主体
            frame_descriptions: 每帧的动作描述，如 ["手举起", "手挥下", "手收回"]
            fps: 帧率
            style: 风格
            width/height: 尺寸
        """
        profile_name = f"custom_anim_{int(time.time())}"
        profile = self.style_manager.create_profile(
            profile_name, style=style, width=width, height=height
        )
        seeds = self.style_manager.generate_seeds(profile_name, len(frame_descriptions))

        t0 = time.perf_counter()
        frames: list[Image.Image] = []
        frame_prompts: list[str] = []

        for i, (desc, seed) in enumerate(zip(frame_descriptions, seeds)):
            full_prompt = self.prompt_engine.build(
                f"{subject}, {desc}", "rpg_character", style
            )
            result = self.generator.generate_sprite(
                prompt=full_prompt, style=style, asset_type="sprite",
                width=width, height=height, seed=seed,
            )
            frames.append(result.image)
            frame_prompts.append(full_prompt)

        elapsed = int((time.perf_counter() - t0) * 1000)
        return AnimationResult(
            frames=frames, frame_prompts=frame_prompts, fps=fps,
            style=style, total_elapsed_ms=elapsed, profile_name=profile_name,
        )

    @staticmethod
    def list_presets() -> list[dict]:
        """列出所有预设动画类型。"""
        return [
            {"name": k, "label": v["label"], "frames": v["frames"], "fps": v["fps"]}
            for k, v in ANIMATION_PRESETS.items()
        ]
