"""PixelForge AI — Cocos Creator 引擎导出器."""

import os
import plistlib
from typing import Optional

from PIL import Image

from .base_exporter import BaseExporter, AssetManifest


class CocosExporter(BaseExporter):
    """Cocos Creator 引擎导出器。

    生成：
    - 单张精灵的独立 PNG（1x + 2x）
    - .plist 精灵表描述文件（可选，用于批量合并）
    - 动画帧序列的 .plist 配置
    """

    ENGINE_NAME = "cocos"

    def export_sprite_sheet(
        self,
        images: list[Image.Image],
        names: list[str],
        sheet_name: str = "spritesheet",
        style: str = "pixel_art",
    ) -> str:
        """将多个精灵打包为一张精灵表 + .plist 元数据。

        Args:
            images: 精灵图片列表（需尺寸一致）
            names: 对应的帧名称
            sheet_name: 精灵表名称
            style: 风格

        Returns:
            .plist 文件路径
        """
        if not images:
            raise ValueError("至少需要一张图片")

        session_dir = self._ensure_session_dir()
        self._create_dirs(session_dir)

        # 计算网格布局
        cols = min(len(images), 4)
        rows = (len(images) + cols - 1) // cols
        cell_w = images[0].size[0]
        cell_h = images[0].size[1]

        sheet_w = cols * cell_w
        sheet_h = rows * cell_h
        sheet_img = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

        frames = {}
        for i, (img, name) in enumerate(zip(images, names)):
            col = i % cols
            row = i // cols
            x, y = col * cell_w, row * cell_h
            sheet_img.paste(img, (x, y))

            safe_name = self._sanitize_name(name)
            frames[safe_name] = {
                "x": x, "y": y,
                "width": cell_w, "height": cell_h,
            }

        # 保存精灵表图片
        png_path = os.path.join(session_dir, "1x", f"{sheet_name}.png")
        sheet_img.save(png_path, "PNG")
        self._exported_files.append(png_path)

        # 2x 精灵表
        sheet_2x = sheet_img.resize((sheet_w * 2, sheet_h * 2), Image.LANCZOS)
        png_2x_path = os.path.join(session_dir, "2x", f"{sheet_name}@2x.png")
        sheet_2x.save(png_2x_path, "PNG")
        self._exported_files.append(png_2x_path)

        # 生成 Cocos .plist
        plist_data = self._build_cocos_plist(
            frames=frames,
            sheet_size=(sheet_w, sheet_h),
            cell_size=(cell_w, cell_h),
            texture_name=f"{sheet_name}.png",
        )
        plist_path = os.path.join(session_dir, f"{sheet_name}.plist")
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)
        self._exported_files.append(plist_path)

        # 记录 manifest
        for name in names:
            safe_name = self._sanitize_name(name)
            self._manifest.append(AssetManifest(
                name=safe_name,
                asset_type="sprite",
                width=cell_w,
                height=cell_h,
                style=style,
            ))

        return plist_path

    def export_animation_frames(
        self,
        images: list[Image.Image],
        anim_name: str,
        fps: int = 8,
    ) -> str:
        """导出动画帧序列（独立 PNG + .plist 帧配置）。

        Returns:
            .plist 文件路径
        """
        names = [f"{anim_name}_frame_{i:03d}" for i in range(len(images))]
        return self.export_sprite_sheet(
            images=images,
            names=names,
            sheet_name=anim_name,
        )

    # ── 覆写 ──────────────────────────────────────────────────

    def _build_metadata(self) -> dict:
        meta = super()._build_metadata()
        meta["cocos_version"] = "3.x"
        meta["import_instructions"] = (
            "将 PNG 文件拖入 Cocos Creator 的 assets 目录，"
            "设置 Texture Type 为 sprite-frame。"
            "对于精灵表，将 .plist 文件一同导入，"
            "Cocos Creator 自动识别帧数据。"
        )
        return meta

    def _write_engine_files(self, session_dir: str) -> list[str]:
        readme = os.path.join(session_dir, "COCOS_README.txt")
        with open(readme, "w", encoding="utf-8") as f:
            f.write(self._cocos_readme())
        return [readme]

    # ── 内部 ──────────────────────────────────────────────────

    @staticmethod
    def _build_cocos_plist(
        frames: dict,
        sheet_size: tuple[int, int],
        cell_size: tuple[int, int],
        texture_name: str,
    ) -> dict:
        """构建 Cocos Creator 兼容的 .plist 数据结构。"""
        frames_data = {}
        for name, rect in frames.items():
            x, y, w, h = rect["x"], rect["y"], rect["width"], rect["height"]
            frames_data[name] = {
                "frame": "{%d,%d,%d,%d}" % (x, y, w, h),
                "offset": "{0,0}",
                "rotated": False,
                "sourceColorRect": "{0,0,%d,%d}" % (w, h),
                "sourceSize": "{%d,%d}" % (w, h),
            }

        sw, sh = sheet_size
        return {
            "frames": frames_data,
            "metadata": {
                "format": 3,
                "size": "{%d,%d}" % (sw, sh),
                "textureFileName": texture_name,
                "realTextureFileName": texture_name,
                "smartupdate": "",
            },
        }

    @staticmethod
    def _cocos_readme() -> str:
        return """Cocos Creator 资源包 — PixelForge AI 生成
===========================================

使用方法:
1. 将 PNG 文件拖入 Cocos Creator 的 assets 目录
2. 选中图片 → 属性面板设置 Texture Type = sprite-frame
3. 对于精灵表 (.plist)：
   - PNG 和 .plist 放在同一目录
   - Cocos Creator 自动导入为 SpriteAtlas
4. 像素风素材：Texture Filter Mode = Point

兼容版本: Cocos Creator 3.x
"""
