"""Phase 2 集成测试 — 三大引擎导出器."""

import os
import sys
import json
import plistlib
import zipfile
import shutil
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image

from exporters.unity_exporter import UnityExporter
from exporters.godot_exporter import GodotExporter
from exporters.cocos_exporter import CocosExporter


TEST_IMG = Image.new("RGBA", (64, 64), (255, 128, 0, 255))
OUTPUT_ROOT = "static/test_exporter_tests"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)


class TestUnityExporter:
    """Task 2.2 — Unity 导出器测试."""

    def test_export_sprite_creates_meta(self):
        e = UnityExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero", "sprite", "pixel_art")
        assert os.path.exists(path)
        assert os.path.exists(path + ".meta")

    def test_meta_contains_guid(self):
        e = UnityExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero", "sprite", "pixel_art")
        with open(path + ".meta") as f:
            content = f.read()
        assert "guid:" in content

    def test_pixel_art_filter_mode_point(self):
        e = UnityExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero", "sprite", "pixel_art")
        with open(path + ".meta") as f:
            assert "filterMode: 0" in f.read()

    def test_finalize_creates_zip(self):
        e = UnityExporter(output_root=OUTPUT_ROOT)
        e.export_sprite(TEST_IMG, "hero")
        r = e.finalize()
        assert os.path.exists(r.zip_path)
        assert r.zip_path.endswith(".zip")


class TestGodotExporter:
    """Task 2.3 — Godot 导出器测试."""

    def test_export_sprite_creates_import(self):
        e = GodotExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero", "sprite", "pixel_art")
        assert os.path.exists(path + ".import")
        assert os.path.exists(path.replace(".png", ".tscn"))

    def test_import_contains_importer(self):
        e = GodotExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero")
        with open(path + ".import") as f:
            assert 'importer="texture"' in f.read()

    def test_tscn_contains_sprite2d(self):
        e = GodotExporter(output_root=OUTPUT_ROOT)
        path = e.export_sprite(TEST_IMG, "hero")
        with open(path.replace(".png", ".tscn")) as f:
            assert "Sprite2D" in f.read()

    def test_sprite_frames_export(self):
        e = GodotExporter(output_root=OUTPUT_ROOT)
        frames = [TEST_IMG for _ in range(3)]
        tres = e.export_sprite_frames(frames, "idle", fps=8)
        assert os.path.exists(tres)
        with open(tres) as f:
            assert "SpriteFrames" in f.read()


class TestCocosExporter:
    """Task 2.4 — Cocos 导出器测试."""

    def test_sprite_sheet_creates_plist(self):
        e = CocosExporter(output_root=OUTPUT_ROOT)
        imgs = [TEST_IMG for _ in range(4)]
        plist = e.export_sprite_sheet(imgs, ["a", "b", "c", "d"], "sheet")
        assert os.path.exists(plist)
        assert plist.endswith(".plist")

    def test_plist_has_frames(self):
        e = CocosExporter(output_root=OUTPUT_ROOT)
        imgs = [TEST_IMG for _ in range(4)]
        plist = e.export_sprite_sheet(imgs, ["a", "b", "c", "d"], "sheet")
        with open(plist, "rb") as f:
            data = plistlib.load(f)
        assert len(data["frames"]) == 4

    def test_animation_frames(self):
        e = CocosExporter(output_root=OUTPUT_ROOT)
        frames = [TEST_IMG for _ in range(3)]
        plist = e.export_animation_frames(frames, "run")
        assert os.path.exists(plist)


class TestAllExportersIntegration:
    """三大引擎导出器集成测试."""

    def test_all_exporters_finalize(self):
        exporters = [
            UnityExporter(output_root=OUTPUT_ROOT + "/unity"),
            GodotExporter(output_root=OUTPUT_ROOT + "/godot"),
            CocosExporter(output_root=OUTPUT_ROOT + "/cocos"),
        ]
        for e in exporters:
            e.export_sprite(TEST_IMG, "test", "sprite", "pixel_art")
            r = e.finalize()
            assert os.path.exists(r.zip_path)

    def test_all_manifests_valid(self):
        exporters = [
            UnityExporter(output_root=OUTPUT_ROOT + "/unity"),
            GodotExporter(output_root=OUTPUT_ROOT + "/godot"),
            CocosExporter(output_root=OUTPUT_ROOT + "/cocos"),
        ]
        engines = ["unity", "godot", "cocos"]
        for e, eng in zip(exporters, engines):
            e.export_sprite(TEST_IMG, "test")
            r = e.finalize()
            with open(os.path.join(r.output_dir, "manifest.json"),
                      "r", encoding="utf-8") as f:
                meta = json.load(f)
            assert meta["engine"] == eng
