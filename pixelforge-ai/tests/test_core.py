"""Phase 1 集成测试 — 核心引擎三模块联调."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.generator import GameAssetGenerator, GenerationResult
from core.prompt_engine import PromptEngine
from core.style_manager import StyleManager


class TestPromptEngine:
    """Task 1.3 — PromptEngine 测试."""

    def test_template_count(self):
        engine = PromptEngine()
        assert len(engine.list_templates()) >= 10

    def test_build_en(self):
        engine = PromptEngine()
        result = engine.build("sword", "rpg_sword", "pixel_art", "en")
        assert "sword" in result
        assert "pixel" in result.lower()

    def test_build_cn(self):
        engine = PromptEngine()
        result = engine.build("大剑", "rpg_sword", "pixel_art", "cn")
        assert "大剑" in result

    def test_build_batch(self):
        engine = PromptEngine()
        batch = engine.build_batch(["a", "b", "c"], "rpg_potion", "pixel_art")
        assert len(batch) == 3

    def test_invalid_template_raises(self):
        engine = PromptEngine()
        with pytest.raises(ValueError):
            engine.build("test", "not_exist")

    def test_genres(self):
        engine = PromptEngine()
        genres = engine.get_genres()
        assert "rpg" in genres
        assert "ui" in genres


class TestStyleManager:
    """Task 1.4 — StyleManager 测试."""

    def test_create_profile(self):
        mgr = StyleManager()
        p = mgr.create_profile("test", "pixel_art", seed_base=42)
        assert p.seed_base == 42

    def test_seeds_deterministic(self):
        mgr = StyleManager()
        mgr.create_profile("test", "pixel_art", seed_base=100)
        a = mgr.generate_seeds("test", 5)
        b = mgr.generate_seeds("test", 5)
        assert a == b

    def test_derive_profile(self):
        mgr = StyleManager()
        mgr.create_profile("base", "pixel_art", seed_base=42, width=256)
        d = mgr.derive_profile("base", "large", width=512)
        assert d.seed_base == 42
        assert d.width == 512

    def test_string_seed(self):
        a = StyleManager.make_seed_from_string("hello")
        b = StyleManager.make_seed_from_string("hello")
        assert a == b


class TestIntegration:
    """端到端集成测试."""

    def test_full_pipeline_prompt_build(self):
        """测试完整提示词构建链路。"""
        engine = PromptEngine()
        mgr = StyleManager()
        mgr.create_profile("rpg_set", "pixel_art", seed_base=42)

        prompt = engine.build("golden sword", "rpg_sword", "pixel_art")
        negative = engine.build_negative("rpg_sword", "pixel_art")
        seeds = mgr.generate_seeds("rpg_set", 3)

        assert len(prompt) > 20
        assert len(negative) > 10
        assert len(seeds) == 3
        assert seeds[0] == 42

    @pytest.mark.slow
    def test_real_generation(self):
        """真实 API 生成测试 — 需要 API Key 和网络。"""
        gen = GameAssetGenerator()
        engine = PromptEngine()

        prompt = engine.build("health potion", "rpg_potion", "pixel_art")
        result = gen.generate_sprite(
            prompt=prompt,
            style="pixel_art",
            asset_type="icon",
            width=256,
            height=256,
            seed=42,
        )
        assert result.image is not None
        assert result.image.size == (256, 256)
        assert result.elapsed_ms > 0
