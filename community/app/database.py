"""
文件名：app/database.py
作用：数据库引擎、会话工厂、ORM 基类与 Session 依赖。
说明：只负责数据库连接相关基础设施，不包含任何业务逻辑。
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings

# 连接池配置：pool_pre_ping 自动剔除失效连接，pool_recycle 避免 MySQL 8 小时断连
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """所有 ORM 模型的公共基类（SQLAlchemy 2.0 声明式写法）。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每个请求独立 Session，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()