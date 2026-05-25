"""PixelForge AI — 生成结果缓存层."""

import hashlib
import json
import os
import time
from typing import Optional

from PIL import Image


class GenerationCache:
    """基于文件系统的生成结果缓存。

    相同提示词 + 种子 → 直接返回缓存图片，跳过 API 调用。
    """

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "static", "cache"
            )
        self.cache_dir = cache_dir
        self._hits = 0
        self._misses = 0
        os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, prompt: str, seed: int, width: int, height: int) -> Optional[Image.Image]:
        """从缓存获取图片，无命中返回 None。"""
        key = self._make_key(prompt, seed, width, height)
        path = os.path.join(self.cache_dir, f"{key}.png")

        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            if time.time() - mtime < 86400:  # 24h 有效期
                self._hits += 1
                return Image.open(path)
            os.remove(path)  # 过期删除

        self._misses += 1
        return None

    def set(self, image: Image.Image, prompt: str, seed: int, width: int, height: int) -> str:
        """存入缓存。"""
        key = self._make_key(prompt, seed, width, height)
        path = os.path.join(self.cache_dir, f"{key}.png")
        image.save(path, "PNG")
        return path

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": round(self._hits / max(total, 1), 2),
        }

    def clear_expired(self) -> int:
        """清理过期缓存文件。"""
        removed = 0
        now = time.time()
        for f in os.listdir(self.cache_dir):
            if not f.endswith(".png"):
                continue
            path = os.path.join(self.cache_dir, f)
            if now - os.path.getmtime(path) > 86400:
                os.remove(path)
                removed += 1
        return removed

    @staticmethod
    def _make_key(prompt: str, seed: int, width: int, height: int) -> str:
        raw = json.dumps([prompt, seed, width, height], sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()[:16]
