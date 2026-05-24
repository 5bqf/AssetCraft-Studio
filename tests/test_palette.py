"""Tests for palette extraction module."""

import numpy as np
from PIL import Image

from modules.palette import extract_palette, rgb_to_hex, hex_to_rgb, _kmeans, palette_to_html


def test_rgb_to_hex():
    assert rgb_to_hex((255, 0, 0)) == "#ff0000"
    assert rgb_to_hex((0, 0, 0)) == "#000000"
    assert rgb_to_hex((255, 255, 255)) == "#ffffff"
    assert rgb_to_hex((18, 52, 86)) == "#123456"


def test_hex_to_rgb():
    assert hex_to_rgb("#ff0000") == (255, 0, 0)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("ff0000") == (255, 0, 0)


def test_kmeans_basic():
    pixels = np.array([
        [255, 0, 0],
        [255, 5, 0],
        [0, 255, 0],
        [0, 250, 5],
        [0, 0, 255],
        [5, 0, 255],
    ], dtype=np.float32)
    labels = _kmeans(pixels, k=3)
    assert len(set(labels)) == 3
    # same-color pixels should be in same cluster
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[4] == labels[5]


def test_extract_palette_uniform_image():
    img = Image.new("RGB", (200, 100), (100, 150, 200))
    colors = extract_palette(img, num_colors=5)
    assert len(colors) >= 1
    c = colors[0]
    assert c["ratio"] > 0.9
    assert c["hex"] == "#6496c8"


def test_extract_palette_distinct_colors():
    img = Image.new("RGB", (300, 100))
    for x in range(100):
        for y in range(100):
            img.putpixel((x, y), (255, 0, 0))
    for x in range(100, 200):
        for y in range(100):
            img.putpixel((x, y), (0, 255, 0))
    for x in range(200, 300):
        for y in range(100):
            img.putpixel((x, y), (0, 0, 255))
    colors = extract_palette(img, num_colors=3)
    hexes = {c["hex"] for c in colors}
    assert "#ff0000" in hexes
    assert "#00ff00" in hexes
    assert "#0000ff" in hexes


def test_palette_to_html():
    colors = [{"hex": "#ff0000", "ratio": 0.5}, {"hex": "#00ff00", "ratio": 0.5}]
    html = palette_to_html(colors)
    assert "#ff0000" in html
    assert "#00ff00" in html
    assert "56px" in html
