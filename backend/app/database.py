# -*- coding: utf-8 -*-
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from .config import settings

# SQLite 不需要连接池配置
engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False},  # SQLite 多线程访问必需
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表，失败时自动重试（用于 Railway 等场景等待卷就绪）"""
    max_retries = 5
    retry_delay = 3

    for attempt in range(1, max_retries + 1):
        try:
            # Test connection first
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            # Enable WAL mode for better concurrent performance
            with engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.execute(text("PRAGMA foreign_keys=ON"))
            # Create all tables
            Base.metadata.create_all(bind=engine)
            print(f"[DB] 数据库表创建成功 (attempt {attempt})")
            return
        except OperationalError as e:
            if attempt < max_retries:
                print(f"[DB] 数据库连接失败，{retry_delay}s 后重试 (attempt {attempt}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                print(f"[DB] 数据库连接失败，已重试 {max_retries} 次: {e}")
                raise
