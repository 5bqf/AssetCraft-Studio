"""Tests for asset exporter module."""

import os
import zipfile

from PIL import Image

from modules.exporter import (
    _make_readme_md,
    _sanitize_filename,
    export_asset_pack,
    OUTPUT_DIR,
)


def test_make_readme_md():
    readme = _make_readme_md("pixel-art", ["sword", "shield", "potion"])
    assert "# Asset Pack" in readme or "Asset Pack" in readme
    assert "pixel-art" in readme
    assert "sword" in readme
    assert "1x" in readme
    assert "2x" in readme
    assert "Unity" in readme or "Godot" in readme


def test_make_readme_md_with_colors():
    readme = _make_readme_md("pixel-art", ["sword"], ["#ff0000", "#00ff00"])
    assert "#ff0000" in readme


def test_sanitize_filename_basic():
    assert _sanitize_filename("hello world") == "hello_world"
    assert _sanitize_filename("icon-01") == "icon-01"
    assert _sanitize_filename("shop icon!@#") == "shop_icon"


def test_sanitize_filename_chinese():
    result = _sanitize_filename("商店图标")
    assert len(result) > 0


def test_export_asset_pack_creates_valid_zip():
    images = [
        Image.new("RGBA", (64, 64), (255, 0, 0, 255)),
        Image.new("RGBA", (64, 64), (0, 255, 0, 255)),
    ]
    subjects = ["sword", "shield"]

    zip_path = export_asset_pack(images, subjects, style_name="pixel-art")
    assert os.path.exists(zip_path)
    assert zip_path.endswith(".zip")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "assets/README_assets.md" in names
        assert any("1x/" in n and "sword" in n for n in names)
        assert any("2x/" in n and "sword" in n for n in names)
        assert any("1x/" in n and "shield" in n for n in names)
        assert any("@2x" in n for n in names)

    os.remove(zip_path)


def test_sanitize_filename_empty():
    result = _sanitize_filename("!!!")
    assert result == "asset"
