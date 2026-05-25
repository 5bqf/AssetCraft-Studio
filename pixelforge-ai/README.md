# PixelForge AI

### 2D 游戏素材生成器 — 一键生成 · 多引擎导出 · 风格统一

## 功能

| 模块 | 说明 |
|------|------|
| **精灵生成** | 角色、道具、NPC |
| **瓦片生成** | 地形、建筑、场景 (4主题 + autotile) |
| **UI 生成** | 按钮、面板、图标 |
| **特效生成** | 粒子、爆炸、魔法 |
| **动画生成** | 5种预设动画序列 (idle/walk/attack/jump/spin) |
| **批量生成** | 同风格 1-6 个素材 |
| **三引擎导出** | Unity .meta / Godot .tres .tscn / Cocos .plist |

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env  # 编辑填入 SILICONFLOW_API_KEY
python app.py          # 打开 http://127.0.0.1:7860
```

## Docker

```bash
docker-compose up -d
```

## 测试

```bash
pytest tests/ -v            # 全部快速测试 (24项)
pytest tests/ -v -m slow    # 含API慢速测试
```

## 技术架构

```
core/
  generator.py       # GameAssetGenerator — 硅基流动 API
  prompt_engine.py   # PromptEngine — 10 游戏模板
  style_manager.py   # StyleManager — 风格一致性
  animation.py       # AnimationGenerator — 动画序列
  tileset.py         # TilesetGenerator — 瓦片集
  color_palette.py   # ColorPalette — 配色方案
  cache.py           # GenerationCache — 缓存
exporters/
  base_exporter.py   # BaseExporter — 1x/2x/ZIP
  unity_exporter.py  # UnityExporter — .meta
  godot_exporter.py  # GodotExporter — .tres .tscn
  cocos_exporter.py  # CocosExporter — .plist
```

## 支持引擎

- Unity 2022.3+
- Godot 4.x
- Cocos Creator 3.x

## 模型

默认 `Qwen/Qwen-Image` (硅基流动)，支持中文提示词。
通过 `.env` 中 `SILICONFLOW_IMAGE_MODEL` 切换。
