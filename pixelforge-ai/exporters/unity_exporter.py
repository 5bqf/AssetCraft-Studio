"""PixelForge AI — Unity 引擎导出器."""

import os
import uuid
from datetime import datetime, timezone, timedelta

from .base_exporter import BaseExporter, AssetManifest

TZ_BEIJING = timezone(timedelta(hours=8))

# Unity 精灵导入设置模板
SPRITE_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: {filter_mode}
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: {sprite_mode}
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: {pixels_per_unit}
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID:
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  spritePackingTag:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""

# Unity 文件夹 .meta
FOLDER_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""


class UnityExporter(BaseExporter):
    """Unity 2D 游戏引擎导出器。

    为每个素材生成 .meta 文件，包含 GUID 和精灵导入设置，
    Unity 导入时可自动识别为 Sprite (2D and UI)。
    """

    ENGINE_NAME = "unity"

    def export_sprite(
        self, image, name, asset_type="sprite", style="pixel_art", tags=None,
    ):
        """导出素材同时生成 .meta 文件。"""
        path_1x = super().export_sprite(image, name, asset_type, style, tags)

        # 生成 .meta 文件
        pixels_per_unit = self._get_pixels_per_unit(asset_type)
        meta_content = self._build_sprite_meta(
            pixels_per_unit=pixels_per_unit,
            filter_mode=0 if style == "pixel_art" else 1,
            sprite_mode=1,
        )

        meta_path_1x = path_1x + ".meta"
        with open(meta_path_1x, "w", encoding="utf-8") as f:
            f.write(meta_content)
        self._exported_files.append(meta_path_1x)

        # 2x .meta
        w2, h2 = image.size[0] * 2, image.size[1] * 2
        path_2x = path_1x.replace("/1x/", "/2x/").replace(".png", "@2x.png")
        meta_path_2x = path_2x + ".meta"
        with open(meta_path_2x, "w", encoding="utf-8") as f:
            f.write(self._build_sprite_meta(
                pixels_per_unit=pixels_per_unit * 2,
                filter_mode=0 if style == "pixel_art" else 1,
                sprite_mode=1,
            ))
        self._exported_files.append(meta_path_2x)

        # 文件夹 .meta
        for subdir in ("1x", "2x"):
            folder_path = os.path.join(os.path.dirname(path_1x), "..")
            # 只给 session_dir 下的 1x/2x 生成一次
            dir_1x = os.path.dirname(path_1x)
            dir_meta = dir_1x + ".meta"
            if not os.path.exists(dir_meta):
                with open(dir_meta, "w", encoding="utf-8") as f:
                    f.write(FOLDER_META_TEMPLATE.format(guid=self._new_guid()))

        return path_1x

    # ── 覆写 ──────────────────────────────────────────────────

    def _build_metadata(self) -> dict:
        meta = super()._build_metadata()
        meta["unity_version"] = "2022.3+"
        meta["import_instructions"] = (
            "将 assets/ 目录拖入 Unity Project 窗口的 Assets 文件夹，"
            "所有素材自动识别为 Sprite。"
        )
        return meta

    def _write_engine_files(self, session_dir: str) -> list[str]:
        """生成 Unity 资源包说明文件。"""
        readme = os.path.join(session_dir, "UNITY_README.txt")
        content = self._unity_readme()
        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)
        return [readme]

    # ── 内部 ──────────────────────────────────────────────────

    @staticmethod
    def _new_guid() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def _get_pixels_per_unit(asset_type: str) -> int:
        """根据素材类型返回合适的 PPU。"""
        ppu_map = {
            "sprite": 64,
            "tileset": 32,
            "ui_element": 128,
            "icon": 64,
            "vfx": 64,
        }
        return ppu_map.get(asset_type, 64)

    def _build_sprite_meta(
        self,
        pixels_per_unit: int = 64,
        filter_mode: int = 0,
        sprite_mode: int = 1,
    ) -> str:
        return SPRITE_META_TEMPLATE.format(
            guid=self._new_guid(),
            pixels_per_unit=pixels_per_unit,
            filter_mode=filter_mode,
            sprite_mode=sprite_mode,
        )

    @staticmethod
    def _unity_readme() -> str:
        return """Unity 2D 资源包 — PixelForge AI 生成
=======================================

使用方法:
1. 将整个 assets/ 文件夹拖入 Unity Project 窗口
2. 素材自动识别为 Sprite (2D and UI)
3. 像素风素材 (filterMode=Point) 保持清晰边缘
4. 其他风格 (filterMode=Bilinear) 平滑过滤

兼容版本: Unity 2022.3+
"""
