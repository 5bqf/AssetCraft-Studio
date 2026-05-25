# AssetCraft Studio

> 双项目架构 2D 游戏素材生成平台 —— 让创意概念无缝转化为引擎就绪的游戏资产

---

## 项目定位与解题思路

### 赛题核心洞察

题目二要求开发一个 **"用户通过输入文本或简单参数，高效、低成本地生成 2D 游戏素材"** 的工具。我们深入分析了常规 2D 游戏创作对素材的实际需求后，提炼出三个关键痛点：

1. **生成断层**：现有 AI 生图工具只产出单张图片，无法直接融入 Unity/Godot/Cocos 等主流引擎的开发流程
2. **风格漂移**：批量生成时缺乏设计一致性控制，系列素材风格混乱
3. **工作流脱节**：从"创意概念"到"可交付资产包"之间缺少工程化桥梁

### 我们的解法：双项目协同架构

```
PixelForge AI (主项目)          AssetCraft Studio (补充工具)
┌──────────────────────┐       ┌─────────────────────┐
│ 文本/参数 → 生图     │  ←→  │ 参考图 → 色板提取   │
│ 风格一致性控制       │       │ 设计协调器          │
│ 动画/瓦片/配色      │       │ 风格化提示词模板    │
│ 三引擎导出           │       │ AI 工作流引擎       │
└──────────────────────┘       └─────────────────────┘
          ↕                            ↕
    游戏开发者                    产品设计师 / AI 用户
```

- **PixelForge AI** 直面赛题：文本生图 + 引擎导出 + 风格一致性，覆盖完整资产管线
- **AssetCraft Studio** 面向"AI 原生产品设计师"细分群体，提供参考图 → 色板 → 风格模板的设计协调能力

两个项目共享同一套 API 配置，通过 `launch.py` 统一启动，形成互补闭环。

---

## 核心功能亮点

### PixelForge AI — 主项目 2D 素材生成引擎

| 模块 | 功能 | 亮点 |
|------|------|------|
| 精灵生成 | 角色 / 道具 / NPC | 6种风格 × 10种模板 × 8种尺寸 |
| 瓦片生成 | 地形 / 建筑 / 场景 | 4大主题 + 自动瓦片(中心+4边+4角) |
| UI 生成 | 按钮 / 面板 / 图标 | 游戏 UI 专用提示词模板 |
| 特效生成 | 粒子 / 爆炸 / 魔法 | 序列帧风格统一 |
| 动画生成 | idle/walk/attack/jump/spin | 种子递增确保帧间连贯 |
| 批量生成 | 1-6 个同风格素材 | 高级面板一键批量 |
| 三引擎导出 | Unity / Godot / Cocos | `.meta` / `.tres`+`.tscn` / `.plist` |
| 配色方案 | 6种预置 + 图片提取 | K-means 聚类 → 提示词颜色引导 |
| 风格一致性 | StyleManager 种子锁定 | 跨批次生成风格统一 |
| 缓存加速 | MD5 键值 24h 有效期 | 相同提示词命中缓存 ≈0ms |

### AssetCraft Studio — 补充工具 AI 设计工作流

| 功能 | 说明 |
|------|------|
| 文生图 + 图生图 | 基础图像生成（已升级为 PixelForge AI） |
| 设计协调器 | 上传参考图 → 提取色板 → 选择风格模板 → 生成风格统一素材 |
| 批量导出 | 素材列表批量生成 + 一键打包 ZIP（@1x/@2x） |

---

## 如何满足比赛题目二要求

| 赛题要求 | 我们的实现 | 对应功能 |
|----------|-----------|----------|
| **文本/参数生成素材** | 输入自然语言描述 + 选择风格/模板/尺寸即可生成 | 5 个生成 Tab + 10 种提示词模板 |
| **高效生成** | 缓存命中 ≈0ms；API 调用 ~15-40s；批量模式并行 | GenerationCache + 批量生成面板 |
| **低成本** | 硅基流动新用户免费额度；Docker 一键部署零运维 | `.env` 配置 + docker-compose |
| **了解 2D 游戏素材需求** | 覆盖精灵/瓦片/UI/特效/动画 5 大品类 + 7 种尺寸预设 | ASSET_TYPES + SIZE_PRESETS |
| **无缝融入引擎** | Unity `.meta` GUID / Godot `.tres` SpriteFrames / Cocos `.plist` 精灵表 | 三引擎导出器 |
| **风格一致性** | 种子管理 + 风格档案 + 提示词工程 + 色板引导 | StyleManager + PromptEngine + ColorPalette |
| **生成效率** | 批量 1-6 个 + 进度条反馈 + 缓存加速 | 高级面板 + gr.Progress |
| **素材质量** | Qwen-Image / FLUX 模型 + 正负面提示词 + 风格模板调优 | GAME_STYLES × 6 + 负面提示词 |

---

## 开发过程与工程实践

### Git 提交图谱

> [查看完整提交历史](https://github.com/5bqf/AssetCraft-Studio/commits/main)

### 阶段化开发总结

| 阶段 | 内容 | 交付物 | 测试 |
|------|------|--------|------|
| Phase 1 | 核心生成引擎 | Generator / PromptEngine / StyleManager | 12 项 |
| Phase 2 | 游戏引擎导出器 | Unity / Godot / Cocos 导出 | 13 项 |
| Phase 3 | Gradio Web 界面 | 4 标签页 + 进度条 + 批量面板 | — |
| Phase 4 | 高级 2D 功能 | 动画生成 / 瓦片集 / 配色方案 / 缓存 | — |
| Phase 5 | 性能与部署 | Docker / 文档 / 缓存 | — |
| Phase 6-7 | 验证与整理 | 补充工具验证 + 总 README | 24 项全过 |

### 工程规范

- **分支策略**：feature 分支 → `--no-ff` merge → main，保持清晰历史
- **提交粒度**：每个功能模块独立提交，commit message 遵循 `feat(test): description` 格式
- **测试覆盖**：24 项 pytest，覆盖核心引擎 + 三大导出器
- **依赖管理**：`requirements.txt` 锁定版本范围，README 列明所有第三方库

### 原创性声明

- `core/generator.py` — 硅基流动 API 封装，自主设计
- `core/prompt_engine.py` — 10 个游戏专用模板，基于 2D 游戏开发经验原创
- `core/style_manager.py` — 种子管理 + 风格档案系统
- `core/animation.py` — 5 种动画预设，帧描述原创
- `core/tileset.py` — 4 大主题 + autotile 算法
- `core/color_palette.py` — K-means 自实现（零 ML 依赖）
- `exporters/` — Unity/Godot/Cocos 三引擎文件格式逆向分析后自主实现
- 第三方库：Gradio / Pillow / NumPy / OpenCV / Requests / Pytest（均在 README 列明）

---

## 快速开始

### 方案一：统一启动器（推荐）

```bash
git clone https://github.com/5bqf/AssetCraft-Studio.git
cd AssetCraft-Studio

# 安装依赖
pip install -r pixelforge-ai/requirements.txt

# 配置 API Key
cp pixelforge-ai/.env.example pixelforge-ai/.env
# 编辑 .env，填入 SILICONFLOW_API_KEY（在 https://cloud.siliconflow.cn 获取）

# 统一启动
python launch.py
# 选择 1 → PixelForge AI（主项目）
# 选择 2 → AssetCraft Studio（补充工具）
```

### 方案二：直接运行

```bash
cd pixelforge-ai
pip install -r requirements.txt
cp .env.example .env  # 填入 API Key
python app.py          # 打开 http://127.0.0.1:7860
```

### 方案三：Docker 部署

```bash
cd pixelforge-ai
docker-compose up -d    # 访问 http://localhost:7860
```

### 在线演示

> 演示视频：*[B站链接待补充]*
>
> 在线体验：*[Hugging Face Spaces 链接待补充]*

---

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| **AI 模型** | Qwen-Image / FLUX (硅基流动) | 支持中文提示词，国内直连 |
| **Web 框架** | Gradio 6.x | 5 标签页交互式 UI |
| **图像处理** | Pillow + NumPy + OpenCV | LANCZOS 放大 / K-means 聚类 |
| **API 通信** | Requests | REST API 调用硅基流动 |
| **测试** | Pytest | 24 项单元+集成测试 |
| **部署** | Docker + docker-compose | 一键容器化 |
| **版本控制** | Git + GitHub | feature-branch 工作流 |

---

## 未来展望

- **Hugging Face Spaces 上线**：一键在线体验，零安装门槛
- **更多引擎支持**：Unreal Engine Paper2D / RPG Maker / GameMaker Studio
- **AI 驱动自动补全**：输入"一套RPG药水"自动生成 5 瓶不同颜色的药水
- **风格迁移增强**：上传任意截图 → AI 分析并复刻其视觉风格
- **协作工作区**：团队共享风格档案库，确保全项目美术统一
- **本地模型支持**：集成 diffusers 库，离线生成无需 API Key

---

## License

MIT
