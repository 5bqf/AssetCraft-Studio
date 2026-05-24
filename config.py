"""AssetCraft Studio 配置."""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """应用配置，支持环境变量覆盖。"""

    # Stability AI
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")

    # Gradio
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: int = int(os.getenv("PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    # 输出目录
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "static", "outputs")

    # 生成限制
    MAX_BATCH_SIZE: int = 20
    MAX_STEPS: int = 50
    MIN_STEPS: int = 10
