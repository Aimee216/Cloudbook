# -*- coding: utf-8 -*-
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys


def debug(msg: str):
    """输出到 stderr 确保 Railway 日志能显示"""
    print(msg, file=sys.stderr, flush=True)


class Settings(BaseSettings):
    APP_NAME: str = "超市管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # SQLite 数据库配置
    # 默认使用本地文件；可通过 DATABASE_URL 环境变量覆盖
    DATABASE_URL: Optional[str] = None
    SQLITE_PATH: str = "supermarket.db"

    @property
    def db_url(self) -> str:
        # 优先从环境变量读取
        env_val = os.environ.get("DATABASE_URL")
        if env_val:
            debug(f"[Config] 使用 DATABASE_URL: {env_val}")
            return env_val

        # 默认 SQLite
        # 使用当前工作目录（Docker 中为 /app/backend）
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            self.SQLITE_PATH
        )
        debug(f"[Config] 使用 SQLite: {local_path}")
        return f"sqlite:///{local_path}"

    # JWT 配置
    SECRET_KEY: str = "supermarket-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        case_sensitive = True
        extra = "ignore"


settings = Settings()
