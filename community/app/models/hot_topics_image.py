"""
文件名：app/models/hot_topics_image.py
作用：热门话题图片表 ORM 模型。
说明：独立图片表，不关联其他表。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HotTopicsImage(Base):
    """热门话题图片表，用于返回图片列表。"""

    __tablename__ = "hot_topics_image"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(BigInteger(), "mysql"),
        primary_key=True,
        autoincrement=True,
        comment="图片ID，自动生成唯一编号",
    )
    img_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="图片URL",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),
        nullable=True,
        comment="删除时间",
    )
