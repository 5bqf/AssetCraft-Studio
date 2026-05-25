# AssetCraft Studio

### 为 AI 原生产品设计师打造的 2D 游戏素材工作流引擎

> 上传参考图 → 提取色板 → 选择风格 → 批量生成 → 一键打包，将模糊的创意描述快速转化为风格统一、引擎就绪的游戏资产包。

---

## 产品定位

**目标用户**: 正积极使用 Claude、Cursor 等 AI 编码助手的独立开发者、产品设计师和游戏美术。他们擅长用自然语言定义需求，但苦于"创意概念"与"可交付素材"之间存在断层。

**核心价值**: AssetCraft Studio 不是又一个"文生图"工具。它聚焦于**工作流整合**与**设计一致性**——确保从第一张参考图到最终下载的资源包，所有素材保持统一的视觉风格、规范的尺寸和引擎兼容的文件结构。

**创新性**:
- **设计协调器**: 上传任意参考图 → 自动提取核心色板 → 一键应用风格模板 → 生成同风格素材，解决了"系列素材风格不一致"的核心痛点
- **资产导出器**: 批量生成后自动打包为 `assets/1x/` + `assets/2x/` 目录结构，附带 README，直接可导入 Unity、Godot、Cocos Creator 等主流引擎

---

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone <your-repo-url>
cd AssetCraft-Studio

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```
SILICONFLOW_API_KEY=your-siliconflow-api-key
SILICONFLOW_IMAGE_MODEL=Qwen/Qwen-Image
```

> 在 [cloud.siliconflow.cn](https://cloud.siliconflow.cn) 注册获取 API Key（新用户有免费额度）。
> 可选模型：`Qwen/Qwen-Image`（中文友好）、`black-forest-labs/FLUX.1-dev`、
> `FLUX.2 [pro]` 等，通过 `SILICONFLOW_IMAGE_MODEL` 指定。

### 3. 启动应用

```bash
python app.py
```

访问 `http://localhost:7860` 即可使用。

---

## 功能详解

### M1: 基础生成器

| 功能 | 说明 |
|------|------|
| **文生图 (Text-to-Image)** | 输入提示词描述，直接生成游戏素材 |
| **图生图 (Image-to-Image)** | 上传参考图，结合提示词进行风格迁移 |
| **负面提示词** | 排除不需要的元素（如模糊、3D 渲染等） |
| **尺寸预设** | 7 种常用尺寸：正方形、16:9、图标、精灵表等 |
| **高级参数** | Steps、CFG Scale、Seed 精细控制 |

### M2: 设计协调器 (核心亮点)

这是本工具区别于普通 AI 图像工具的核心功能：

1. **调色板提取**: 上传参考图（如《星露谷物语》截图）→ 使用 K-means 颜色聚类算法自动提取 5 种核心色板，显示 HEX 值和像素占比
2. **风格模板**: 6 种预设风格（复古像素、矢量扁平、科技蓝、手绘水彩、星露谷温馨、RPG 物品图标），每种包含精心调校的正/负面提示词工程
3. **一键生成**: 基于提取的色板 + 选择的风格模板，自动构建优化提示词并生成风格统一素材

**完整工作流**: 上传《星露谷物语》截图 → 提取温馨像素风配色 → 选择"星露谷温馨风"模板 → 输入"商店图标" → 生成与参考图风格一致的游戏素材

### M3: 资产导出器

| 功能 | 说明 |
|------|------|
| **批量生成** | 输入素材列表（每行一个），一次生成整体系列 |
| **风格一致性** | 同一模板 + 递增随机种子，确保系列素材风格统一 |
| **一键打包** | 自动打包为 `assets.zip` |
| **引擎就绪** | 内含 `1x/`(原始) + `2x/`(@2x 放大) 目录及 README |

ZIP 目录结构:
```
assets/
├── 1x/
│   ├── asset_01_shop_icon.png
│   ├── asset_02_backpack_icon.png
│   └── ...
├── 2x/
│   ├── asset_01_shop_icon@2x.png
│   ├── asset_02_backpack_icon@2x.png
│   └── ...
└── README_assets.md
```

---

## 技术架构

```
AssetCraft-Studio/
├── app.py                      # Gradio Web UI 入口
├── config.py                   # 配置管理
├── requirements.txt            # 依赖列表
├── modules/
│   ├── generator.py            # M1: 硅基流动 SiliconFlow API 封装
│   ├── palette.py              # M2: K-means 颜色聚类
│   ├── style_templates.py      # M2: 6 种风格提示词模板
│   └── exporter.py             # M3: 批量生成 + ZIP 打包
├── static/
│   └── outputs/                # 生成的 ZIP 文件
└── tests/                      # 单元测试
```

**技术选型**:
- **Gradio 5.x**: 现代化 Web UI，支持 Hugging Face Spaces 一键部署
- **硅基流动 SiliconFlow API**: 国内直连，调用 Qwen-Image / FLUX 等主流生图模型，中文提示词友好
- **PIL/NumPy**: 自实现 K-means 颜色聚类，零额外 ML 依赖
- **zipfile**: Python 标准库，生成引擎兼容的资源包

---

## 使用案例

### 案例: 从《星露谷物语》截图到一套完整图标

1. 找到一张《星露谷物语》游戏截图
2. 在"设计协调器"Tab 上传截图 → 点击"提取调色板" → 获得 5 种核心色
3. 选择"星露谷温馨风"风格模板
4. 输入素材描述（如 "shop icon, backpack icon, quest icon"）
5. 点击"生成风格化素材" → 获得风格统一的游戏素材
6. 切换到"批量导出"Tab，输入完整素材列表 → 批量生成 + 一键下载

**效果**: 仅凭一张截图，10 分钟内产出整套风格统一的游戏图标资源包，可直接导入 Unity 使用。

---

## 致谢

本项目在规划和编码过程中得到了 Claude Code (Anthropic) 的深度协助，涵盖架构设计、代码生成、提示词工程优化等方面。这正是本工具致力于服务的场景——AI 与人类设计师的高效协作，将创意概念快速转化为可交付产品。

同时也感谢硅基流动 (SiliconFlow) 提供的国内图像生成 API，以及 Gradio 团队打造的优秀 ML 应用框架。

---

## 在线演示

> 部署到 Hugging Face Spaces 后可在此处添加演示链接:
> `https://huggingface.co/spaces/<your-username>/assetcraft-studio`

---

## License

MIT
