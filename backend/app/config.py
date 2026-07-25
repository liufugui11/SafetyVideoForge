"""
全局配置管理
"""
import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # 目录
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    TEMP_DIR: Path = BASE_DIR / "temp"
    SKILLS_DIR: Path = PROJECT_ROOT / "skills_library"
    CONFIGS_DIR: Path = PROJECT_ROOT / "configs"
    
    # 数据库
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'safety_video_forge.db'}"
    
    # LLM 配置
    LLM_TIMEOUT: int = 120
    LLM_MAX_RETRIES: int = 3
    
    # 视频生成
    DEFAULT_VIDEO_WIDTH: int = 1080
    DEFAULT_VIDEO_HEIGHT: int = 1920  # 竖屏 9:16
    DEFAULT_VIDEO_FPS: int = 30
    DEFAULT_VIDEO_DURATION: int = 60  # 秒
    
    # 并发限制
    MAX_CONCURRENT_GENERATION: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()

# 确保目录存在
for d in [settings.DATA_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)
