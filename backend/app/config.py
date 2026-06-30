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

    # MySQL 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "supermarket"

    # 兼容 Railway 等多种云平台的数据库环境变量
    DATABASE_URL: Optional[str] = None
    MYSQL_URL: Optional[str] = None
    MYSQL_DATABASE_URL: Optional[str] = None
    MYSQL_PRIVATE_URL: Optional[str] = None
    MYSQL_PUBLIC_URL: Optional[str] = None
    RAILWAY_MYSQL_URL: Optional[str] = None

    @property
    def db_url(self) -> str:
        # 直接从环境变量读取，绕过 pydantic-settings 缓存
        env_val = os.environ.get("DATABASE_URL")
        debug(f"[DEBUG] DATABASE_URL env = {env_val}")

        for key in ["DATABASE_URL", "MYSQL_URL", "MYSQL_DATABASE_URL", "MYSQL_PRIVATE_URL", "MYSQL_PUBLIC_URL"]:
            val = os.environ.get(key)
            if val:
                debug(f"[DEBUG] Found ENV {key} = {val[:50]}...")

        # 按优先级尝试不同的环境变量
        url = (
            self.DATABASE_URL
            or self.MYSQL_URL
            or self.MYSQL_DATABASE_URL
            or self.MYSQL_PRIVATE_URL
            or self.MYSQL_PUBLIC_URL
            or self.RAILWAY_MYSQL_URL
        )
        if url:
            debug(f"[DEBUG] using url: {url[:60]}...")
            if url.startswith("mysql://"):
                url = "mysql+pymysql://" + url[len("mysql://"):]
            if "charset" not in url:
                url += "?charset=utf8mb4" if "?" not in url else "&charset=utf8mb4"
            debug(f"[Config] 使用 DATABASE_URL: {url}")
            return url

        # 备选：从独立变量拼接
        url = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        debug(f"[Config] 使用本地配置: {url}")
        return url

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

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