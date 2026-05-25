"""Tests for style templates module."""

import pytest

from modules.style_templates import (
    list_templates,
    get_template,
    build_styled_prompt,
    palette_to_style_hint,
    STYLE_TEMPLATES,
    StyleTemplate,
)


def test_list_templates_returns_all():
    result = list_templates()
    assert len(result) == len(STYLE_TEMPLATES)
    names = {t["name"] for t in result}
    assert names == set(STYLE_TEMPLATES.keys())


def test_get_template_valid():
    tmpl = get_template("pixel-art")
    assert tmpl is not None
    assert tmpl.name == "pixel-art"
    assert "pixel art" in tmpl.style_prefix.lower()


def test_get_template_invalid():
    assert get_template("nonexistent") is None


def test_build_styled_prompt_basic():
    prompt, neg, size = build_styled_prompt("sword icon", "pixel-art")
    assert "sword icon" in prompt
    assert "pixel art" in prompt.lower()
    assert len(neg) > 0
    assert isinstance(size, tuple)
    assert len(size) == 2


def test_build_styled_prompt_with_palette():
    palette = ["#ff0000", "#00ff00", "#0000ff"]
    prompt, neg, size = build_styled_prompt("sword icon", "pixel-art", palette)
    assert "#ff0000" in prompt


def test_build_styled_prompt_invalid_template():
    with pytest.raises(ValueError, match="未知风格模板"):
        build_styled_prompt("test", "invalid-template")


def test_palette_to_style_hint():
    colors = [
        {"hex": "#ff0000", "rgb": (255, 0, 0), "ratio": 0.5},
        {"hex": "#00ff00", "rgb": (0, 255, 0), "ratio": 0.3},
    ]
    hint = palette_to_style_hint(colors)
    assert "#ff0000" in hint
    assert "#00ff00" in hint


def test_all_templates_have_required_fields():
    for name, tmpl in STYLE_TEMPLATES.items():
        assert isinstance(tmpl, StyleTemplate)
        assert tmpl.name
        assert tmpl.label
        assert tmpl.style_prefix
        assert isinstance(tmpl.recommended_size, tuple)
