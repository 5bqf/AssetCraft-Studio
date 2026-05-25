"""PixelForge AI — 智能瓦片集生成器."""

import time
from dataclasses import dataclass
from typing import Optional

from PIL import Image

from .generator import GameAssetGenerator
from .prompt_engine import PromptEngine
from .style_manager import StyleManager


@dataclass
class TilesetResult:
    """瓦片集生成结果。"""
    tiles: list[Image.Image]
    tile_names: list[str]
    grid_cols: int
    grid_rows: int
    style: str
    elapsed_ms: int


# 预置瓦片集主题
TILESET_THEMES = {
    "grassland": {
        "label": "草原主题 (Grassland)",
        "tiles": [
            ("grass_center", "green grass terrain tile, seamless"),
            ("grass_edge_top", "grass edge meeting dirt, top border"),
            ("grass_corner_tl", "grass corner top-left, dirt visible"),
            ("dirt_path", "dirt path terrain tile, brown earth"),
            ("flower_patch", "grass with small flowers, decorative tile"),
        ],
    },
    "dungeon": {
        "label": "地牢主题 (Dungeon)",
        "tiles": [
            ("stone_floor", "dark stone floor tile, dungeon"),
            ("stone_wall", "stone brick wall tile, dark dungeon"),
            ("torch_sconce", "wall torch sconce, flickering flame"),
            ("iron_bars", "iron bars gate tile, prison cell"),
            ("cracked_floor", "cracked stone floor, damaged dungeon"),
        ],
    },
    "forest": {
        "label": "森林主题 (Forest)",
        "tiles": [
            ("forest_floor", "forest floor with leaves, natural ground"),
            ("tree_trunk", "large tree trunk, impassable obstacle"),
            ("bush", "green bush, decorative foliage"),
            ("mushroom", "red mushroom on forest floor"),
            ("stream_water", "shallow stream water, animated surface"),
        ],
    },
    "sci_fi": {
        "label": "科幻主题 (Sci-Fi)",
        "tiles": [
            ("metal_floor", "metal grid floor, sci-fi spaceship"),
            ("metal_wall", "metal panel wall, futuristic"),
            ("computer_terminal", "computer terminal, glowing screen"),
            ("energy_field", "blue energy field barrier, glowing"),
            ("ventilation", "metal ventilation grate, floor detail"),
        ],
    },
}


class TilesetGenerator:
    """2D 游戏瓦片集生成器。

    为地图编辑器生成风格统一的瓦片组。
    支持多种预置主题 + 自定义瓦片列表。
    """

    def __init__(self):
        self.generator = GameAssetGenerator()
        self.prompt_engine = PromptEngine()

    def generate_tileset(
        self,
        theme: str = "grassland",
        style: str = "pixel_art",
        tile_size: int = 256,
        custom_tiles: Optional[list[tuple[str, str]]] = None,
    ) -> TilesetResult:
        """生成一组风格统一的瓦片。

        Args:
            theme: 预置主题名 (grassland/dungeon/forest/sci_fi)
            style: 风格键名
            tile_size: 瓦片尺寸（正方形）
            custom_tiles: 自定义瓦片列表 [(名称, 描述), ...]，覆盖预置主题

        Returns:
            TilesetResult 含瓦片列表 + 网格布局信息
        """
        if custom_tiles:
            tiles_def = custom_tiles
        else:
            theme_cfg = TILESET_THEMES.get(theme)
            if theme_cfg is None:
                available = ", ".join(TILESET_THEMES.keys())
                raise ValueError(f"未知主题 '{theme}'。可用: {available}")
            tiles_def = theme_cfg["tiles"]

        t0 = time.perf_counter()
        tiles: list[Image.Image] = []
        names: list[str] = []

        for i, (name, desc) in enumerate(tiles_def):
            full_prompt = self.prompt_engine.build(
                f"{desc}, tileable seamless texture", "platform_tile", style
            )
            result = self.generator.generate_sprite(
                prompt=full_prompt,
                style=style,
                asset_type="tileset",
                width=tile_size,
                height=tile_size,
                seed=100 + i,
            )
            tiles.append(result.image)
            names.append(name)

        # 计算网格布局
        cols = min(len(tiles), 4)
        rows = (len(tiles) + cols - 1) // cols

        elapsed = int((time.perf_counter() - t0) * 1000)
        return TilesetResult(
            tiles=tiles,
            tile_names=names,
            grid_cols=cols,
            grid_rows=rows,
            style=style,
            elapsed_ms=elapsed,
        )

    def generate_autotile_set(
        self,
        base_desc: str,
        style: str = "pixel_art",
        tile_size: int = 256,
    ) -> TilesetResult:
        """生成自动瓦片组（中心 + 4边 + 4角）。

        适用于支持 auto-tiling 的地图编辑器（如 Tiled、Unity Rule Tile）。

        Args:
            base_desc: 基础瓦片描述（如 "green grass"）
            style: 风格
            tile_size: 瓦片尺寸
        """
        autotile_defs = [
            ("center", f"{base_desc} center tile, full terrain"),
            ("edge_top", f"{base_desc} top edge, half terrain half transparent"),
            ("edge_right", f"{base_desc} right edge, half terrain"),
            ("edge_bottom", f"{base_desc} bottom edge, half terrain"),
            ("edge_left", f"{base_desc} left edge, half terrain"),
            ("corner_tl", f"{base_desc} top-left corner, quarter terrain"),
            ("corner_tr", f"{base_desc} top-right corner, quarter terrain"),
            ("corner_bl", f"{base_desc} bottom-left corner, quarter terrain"),
            ("corner_br", f"{base_desc} bottom-right corner, quarter terrain"),
        ]
        return self.generate_tileset(
            custom_tiles=autotile_defs,
            style=style,
            tile_size=tile_size,
        )

    @staticmethod
    def list_themes() -> list[dict]:
        return [
            {"name": k, "label": v["label"], "count": len(v["tiles"])}
            for k, v in TILESET_THEMES.items()
        ]
