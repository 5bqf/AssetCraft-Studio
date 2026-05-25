"""PixelForge AI — Godot 引擎导出器."""

import os

from .base_exporter import BaseExporter


# Godot .import 文件模板（2D 像素风预设）
GODOT_IMPORT_TEMPLATE = """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://{uid}"
path="{res_path}"

[deps]

source_file="res://.godot/imported/{name}.png"

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=true
process/premult_alpha=true
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""

# Godot Sprite2D 场景模板
SPRITE_SCENE_TEMPLATE = """[gd_scene load_steps=2 format=3 uid="uid://{uid}"]

[ext_resource type="Texture2D" uid="uid://{tex_uid}" path="res://{tex_path}" id="1_{name}"]

[node name="{name}" type="Sprite2D"]
texture = ExtResource("1_{name}")
centered = true
offset = Vector2(0, 0)
"""

# Godot SpriteFrames 资源模板（动画）
SPRITE_FRAMES_TEMPLATE = (
    "[gd_resource type=\"SpriteFrames\" load_steps={load_steps} format=3 "
    "uid=\"uid://{uid}\"]\n\n"
    "{ext_resources}\n\n"
    "[resource]\n"
    "animations = [{animations}]\n"
)


class GodotExporter(BaseExporter):
    """Godot 4.x 引擎导出器。

    为每个素材生成：
    - .import 文件（Godot 自动导入配置）
    - .tscn 场景文件（Sprite2D 节点）
    - 可选 SpriteFrames .tres 动画资源
    """

    ENGINE_NAME = "godot"

    def __init__(self, output_root=None, pixel_art_mode=True):
        super().__init__(output_root)
        self.pixel_art_mode = pixel_art_mode
        self._uid_counter = 1

    def export_sprite(
        self, image, name, asset_type="sprite", style="pixel_art", tags=None,
    ):
        """导出素材 + Godot .import + .tscn 场景。"""
        path_1x = super().export_sprite(image, name, asset_type, style, tags)

        safe_name = self._sanitize_name(name)
        is_pixel = (style == "pixel_art" or self.pixel_art_mode)
        tex_uid = self._next_uid()

        # .import 文件（1x）
        import_1x = self._build_import(safe_name, tex_uid, is_pixel)
        import_path_1x = path_1x + ".import"
        with open(import_path_1x, "w", encoding="utf-8") as f:
            f.write(import_1x)
        self._exported_files.append(import_path_1x)

        # .tscn 场景文件（1x）
        scene_uid = self._next_uid()
        scene_path = os.path.join(os.path.dirname(path_1x), f"{safe_name}.tscn")
        scene = SPRITE_SCENE_TEMPLATE.format(
            uid=scene_uid,
            tex_uid=tex_uid,
            tex_path=f"1x/{safe_name}.png",
            name=safe_name,
        )
        with open(scene_path, "w", encoding="utf-8") as f:
            f.write(scene)
        self._exported_files.append(scene_path)

        # 2x import
        tex_uid_2x = self._next_uid()
        path_2x = path_1x.replace("/1x/", "/2x/").replace(".png", "@2x.png")
        import_2x = self._build_import(f"{safe_name}@2x", tex_uid_2x, is_pixel)
        import_2x_path = path_2x + ".import"
        with open(import_2x_path, "w", encoding="utf-8") as f:
            f.write(import_2x)
        self._exported_files.append(import_2x_path)

        return path_1x

    def export_sprite_frames(
        self,
        images: list,
        name: str,
        fps: int = 8,
        style: str = "pixel_art",
    ) -> str:
        """导出动画帧序列为 SpriteFrames .tres。

        Args:
            images: 动画帧列表（PIL Image）
            name: 动画名称
            fps: 帧率

        Returns:
            .tres 文件路径
        """
        session_dir = self._ensure_session_dir()
        self._create_dirs(session_dir)

        safe_name = self._sanitize_name(name)
        resources = []
        anim_frames = ""

        for i, img in enumerate(images):
            frame_uid = self._next_uid()
            tex_name = f"{safe_name}_frame_{i:03d}"
            tex_path = f"1x/{tex_name}.png"

            # 保存帧图片
            frame_path = os.path.join(session_dir, "1x", f"{tex_name}.png")
            img.save(frame_path, "PNG")
            self._exported_files.append(frame_path)

            resources.append(
                f'[ext_resource type="Texture2D" uid="uid://{frame_uid}" '
                f'path="res://{tex_path}" id="{i + 1}_{tex_name}"]'
            )

            anim_frames += (
                f'\n{{'
                f'"duration": {1.0 / fps}, '
                f'"texture": ExtResource("{i + 1}_{tex_name}")'
                f'}}'
            )
            if i < len(images) - 1:
                anim_frames += ","

        uid = self._next_uid()
        animations_block = (
            '[{\n'
            f'"frames": [{anim_frames}\n],\n'
            '"loop": true,\n'
            f'"name": &"{safe_name}",\n'
            f'"speed": {fps}.0\n'
            '}}]'
        )
        tres_content = SPRITE_FRAMES_TEMPLATE.format(
            load_steps=len(images) + 1,
            uid=uid,
            ext_resources="\n".join(resources),
            animations=animations_block,
        )

        tres_path = os.path.join(session_dir, f"{safe_name}.tres")
        with open(tres_path, "w", encoding="utf-8") as f:
            f.write(tres_content)
        self._exported_files.append(tres_path)

        return tres_path

    # ── 覆写 ──────────────────────────────────────────────────

    def _build_metadata(self) -> dict:
        meta = super()._build_metadata()
        meta["godot_version"] = "4.x"
        meta["import_instructions"] = (
            "将整个导出文件夹复制到 Godot 项目的 res:// 目录下，"
            "素材自动识别。如需像素风清晰边缘，在 Project Settings "
            "中将 Rendering/Textures/Default Filters 设为 Nearest。"
        )
        return meta

    def _write_engine_files(self, session_dir: str) -> list[str]:
        readme = os.path.join(session_dir, "GODOT_README.txt")
        content = self._godot_readme()
        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)
        return [readme]

    # ── 内部 ──────────────────────────────────────────────────

    def _next_uid(self) -> str:
        uid = f"c{self._uid_counter:06d}"
        self._uid_counter += 1
        return uid

    @staticmethod
    def _build_import(name: str, uid: str, pixel_art: bool) -> str:
        return GODOT_IMPORT_TEMPLATE.format(
            uid=uid,
            res_path=f"res://.godot/imported/{name}.png-{uid}.res",
            name=name,
        )

    @staticmethod
    def _godot_readme() -> str:
        return """Godot 4.x 资源包 — PixelForge AI 生成
=======================================

使用方法:
1. 将整个导出文件夹复制到 Godot 项目的 res:// 目录
2. .png.import 文件确保素材以正确设置导入
3. .tscn 文件可直接作为 Sprite2D 场景打开
4. .tres 文件为 SpriteFrames 动画资源

像素风设置:
Project Settings → Rendering → Textures → Default Filters → Nearest
"""
