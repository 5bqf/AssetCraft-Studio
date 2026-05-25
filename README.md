# AssetCraft Studio

双项目架构：2D游戏素材生成 + AI设计工作流

## 项目结构

```
├── pixelforge-ai/          # 主项目 - 2D游戏素材生成
│   ├── core/               # 核心引擎 (生成/提示词/风格/动画/瓦片/配色/缓存)
│   ├── exporters/          # 三引擎导出 (Unity/Godot/Cocos)
│   ├── app.py              # Gradio Web 界面 (5 Tab)
│   └── tests/              # 24项测试
├── assetcraft-studio/      # 补充工具 - AI设计工作流
│   ├── modules/            # 生成/调色板/风格模板/导出
│   └── app.py              # Gradio Web 界面
├── shared/                 # 共享组件
├── launch.py               # 统一启动器
└── README.md
```

## 快速启动

```bash
# 主项目
cd pixelforge-ai
pip install -r requirements.txt
cp .env.example .env  # 填入 SILICONFLOW_API_KEY
python app.py         # http://127.0.0.1:7860

# 统一启动器
python launch.py      # 选择 1 (PixelForge) 或 2 (AssetCraft)
```

## 测试

```bash
cd pixelforge-ai
pytest tests/ -v      # 24项测试
```

## 在线演示

> 部署到 Hugging Face Spaces 后在此添加链接

## License

MIT
