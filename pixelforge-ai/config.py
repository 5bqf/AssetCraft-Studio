"""
硅基流动API配置
API Key: sk-hjvspgngeebhvaczarwgidrbgdcftifipuybznwcjyqfpbug
"""

SILICONFLOW_CONFIG = {
    "api_key": "sk-hjvspgngeebhvaczarwgidrbgdcftifipuybznwcjyqfpbug",
    "api_base": "https://api.siliconflow.cn/v1",
    "models": {
        "sd3": "stabilityai/stable-diffusion-3.5-large",
        "sdxl": "stabilityai/stable-diffusion-xl-base-1.0"
    }
}

# 2D游戏风格预设
GAME_STYLES = {
    "pixel_art": "像素风格",
    "cartoon_2d": "卡通2D",
    "hand_drawn": "手绘风格",
    "low_poly": "低多边形"
}

# 素材类型
ASSET_TYPES = {
    "character": "角色精灵",
    "tileset": "瓦片集",
    "ui_element": "UI元素",
    "vfx": "特效"
}
