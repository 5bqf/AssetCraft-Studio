"""M2: Color palette extraction from reference images."""

import colorsys
from collections import Counter
from typing import Sequence

import numpy as np
from PIL import Image


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _color_distance(c1: np.ndarray, c2: np.ndarray) -> float:
    """CIEDE2000 简化为欧氏距离 + 色相惩罚，用于颜色聚类去重。"""
    diff = c1.astype(float) - c2.astype(float)
    return float(np.sqrt(np.sum(diff * diff)))


def extract_palette(
    image: Image.Image,
    num_colors: int = 5,
    min_distance: float = 35.0,
) -> list[dict]:
    """
    从图片提取主色调。

    使用 K-means 颜色聚类 + 感知去重，返回按视觉占比排序的颜色列表。
    """
    img = image.copy().convert("RGB")
    # 缩放到合理尺寸以加速
    w, h = img.size
    max_dim = 300
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    pixels = np.array(img).reshape(-1, 3).astype(np.float32)

    # K-means 聚类
    n_clusters = min(num_colors * 3, 16)
    best_labels = _kmeans(pixels, n_clusters)

    # 统计每个聚类的大小
    counter = Counter(best_labels)
    # 计算每个聚类的平均颜色
    cluster_colors = {}
    for label in set(best_labels):
        mask = best_labels == label
        cluster_pixels = pixels[mask]
        avg_color = np.mean(cluster_pixels, axis=0)
        cluster_colors[label] = (avg_color, int(mask.sum()))

    # 按像素占比排序
    sorted_clusters = sorted(
        cluster_colors.items(), key=lambda x: x[1][1], reverse=True
    )

    # 去重：过滤掉过于相似的颜色
    result: list[dict] = []
    for label, (color, count) in sorted_clusters:
        if len(result) >= num_colors:
            break
        # 检查是否与已有颜色太接近
        too_close = False
        for existing in result:
            existing_rgb = np.array(hex_to_rgb(existing["hex"]), dtype=np.float32)
            if _color_distance(color, existing_rgb) < min_distance:
                too_close = True
                break
        if too_close:
            continue

        rgb = tuple(int(round(c)) for c in np.clip(color, 0, 255))
        hex_val = rgb_to_hex(rgb)
        hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        result.append({
            "hex": hex_val,
            "rgb": rgb,
            "hsv": tuple(round(v, 3) for v in hsv),
            "ratio": round(count / len(best_labels), 3),
        })

    return result


def _kmeans(pixels: np.ndarray, k: int, max_iter: int = 20) -> np.ndarray:
    """简易 K-means 实现，避免引入 sklearn 依赖。"""
    n = pixels.shape[0]
    # 随机初始化中心
    rng = np.random.default_rng(42)
    indices = rng.choice(n, k, replace=False)
    centers = pixels[indices].copy()

    labels = np.zeros(n, dtype=np.int32)
    for _ in range(max_iter):
        # 分配标签
        distances = np.sum((pixels[:, np.newaxis, :] - centers[np.newaxis, :, :]) ** 2, axis=2)
        new_labels = np.argmin(distances, axis=1)

        # 更新中心
        new_centers = np.zeros_like(centers)
        for j in range(k):
            mask = new_labels == j
            if mask.any():
                new_centers[j] = np.mean(pixels[mask], axis=0)
            else:
                new_centers[j] = centers[j]

        if np.all(new_labels == labels):
            break

        labels = new_labels
        centers = new_centers

    return labels


def palette_to_html(colors: list[dict]) -> str:
    """将调色板渲染为 HTML 色块，供 Gradio 展示。"""
    if not colors:
        return "<p>未能提取到有效颜色</p>"

    swatches = ""
    for c in colors:
        swatches += (
            f'<div style="display:inline-block;margin:6px;text-align:center">'
            f'<div style="width:56px;height:56px;background:{c["hex"]};'
            f'border-radius:8px;border:2px solid #333"></div>'
            f'<div style="font-size:11px;font-family:monospace;margin-top:4px">{c["hex"]}</div>'
            f'<div style="font-size:10px;color:#888">{c["ratio"]:.0%}</div>'
            f"</div>"
        )
    return f'<div style="padding:8px">{swatches}</div>'
