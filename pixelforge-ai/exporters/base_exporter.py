"""PixelForge AI — 导出器基类."""

import io
import json
import os
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from PIL import Image

TZ_BEIJING = timezone(timedelta(hours=8))


@dataclass
class AssetManifest:
    """单个素材的描述信息。"""
    name: str
    asset_type: str  # sprite, tileset, ui, vfx, icon
    width: int
    height: int
    style: str
    tags: list[str] = field(default_factory=list)


@dataclass
class ExportResult:
    """导出结果。"""
    output_dir: str
    zip_path: str
    files: list[str]
    manifest: list[AssetManifest]


class BaseExporter:
    """导出器基类。

    封装所有引擎导出器共用的逻辑：
    - 目录创建（@1x / @2x）
    - 图像保存（PNG 格式）
    - ZIP 打包
    - 元数据生成
    """

    ENGINE_NAME: str = "base"

    def __init__(self, output_root: Optional[str] = None):
        if output_root is None:
            output_root = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "static", "exports"
            )
        self.output_root = output_root
        self._manifest: list[AssetManifest] = []
        self._exported_files: list[str] = []

    # ── 公开 API ──────────────────────────────────────────────

    def export_sprite(
        self,
        image: Image.Image,
        name: str,
        asset_type: str = "sprite",
        style: str = "pixel_art",
        tags: Optional[list[str]] = None,
    ) -> str:
        """导出单个素材到 1x 和 2x 目录。

        Returns:
            素材在 1x 目录中的文件路径
        """
        session_dir = self._ensure_session_dir()
        self._create_dirs(session_dir)

        # 清理文件名
        safe_name = self._sanitize_name(name)

        # 1x — 原始尺寸
        path_1x = os.path.join(session_dir, "1x", f"{safe_name}.png")
        image.save(path_1x, "PNG")
        self._exported_files.append(path_1x)

        # 2x — 双倍放大
        w2, h2 = image.size[0] * 2, image.size[1] * 2
        img_2x = image.resize((w2, h2), Image.LANCZOS)
        path_2x = os.path.join(session_dir, "2x", f"{safe_name}@2x.png")
        img_2x.save(path_2x, "PNG")
        self._exported_files.append(path_2x)

        # 记录 manifest
        self._manifest.append(AssetManifest(
            name=safe_name,
            asset_type=asset_type,
            width=image.size[0],
            height=image.size[1],
            style=style,
            tags=tags or [],
        ))

        return path_1x

    def export_batch(
        self,
        images: list[Image.Image],
        names: list[str],
        asset_type: str = "sprite",
        style: str = "pixel_art",
    ) -> list[str]:
        """批量导出素材。"""
        results = []
        for img, name in zip(images, names):
            path = self.export_sprite(img, name, asset_type, style)
            results.append(path)
        return results

    def finalize(self) -> ExportResult:
        """完成导出：生成元数据 + 打包 ZIP。

        Returns:
            ExportResult 包含输出目录、ZIP 路径、文件清单
        """
        session_dir = self._ensure_session_dir()

        # 生成引擎元数据
        metadata = self._build_metadata()
        meta_path = os.path.join(session_dir, "manifest.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        self._exported_files.append(meta_path)

        # 生成引擎特定文件（子类实现）
        engine_files = self._write_engine_files(session_dir)
        self._exported_files.extend(engine_files)

        # 打包 ZIP
        zip_path = self._make_zip(session_dir)

        return ExportResult(
            output_dir=session_dir,
            zip_path=zip_path,
            files=list(self._exported_files),
            manifest=list(self._manifest),
        )

    # ── 子类可覆写 ────────────────────────────────────────────

    def _build_metadata(self) -> dict:
        """构建通用元数据（子类可追加引擎特定字段）。"""
        return {
            "engine": self.ENGINE_NAME,
            "generated_at": datetime.now(TZ_BEIJING).isoformat(),
            "assets": [
                {
                    "name": m.name,
                    "type": m.asset_type,
                    "size": f"{m.width}x{m.height}",
                    "style": m.style,
                    "tags": m.tags,
                }
                for m in self._manifest
            ],
        }

    def _write_engine_files(self, session_dir: str) -> list[str]:
        """写入引擎特定文件（子类实现）。"""
        return []

    # ── 内部方法 ──────────────────────────────────────────────

    def _ensure_session_dir(self) -> str:
        """获取或创建本次导出的会话目录。"""
        ts = datetime.now(TZ_BEIJING).strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(self.output_root, f"export_{ts}")
        return session_dir

    @staticmethod
    def _create_dirs(session_dir: str) -> None:
        os.makedirs(os.path.join(session_dir, "1x"), exist_ok=True)
        os.makedirs(os.path.join(session_dir, "2x"), exist_ok=True)

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """安全化文件名。"""
        import re
        safe = re.sub(r"[^\w\-一-鿿]", "_", name.strip())
        return safe.strip("_") or "asset"

    def _make_zip(self, session_dir: str) -> str:
        """将会话目录打包为 ZIP。"""
        zip_path = session_dir + ".zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(session_dir):
                for f in files:
                    full = os.path.join(root, f)
                    arcname = os.path.relpath(full, session_dir)
                    zf.write(full, arcname)
        return zip_path
