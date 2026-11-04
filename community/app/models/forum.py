"""
文件名：app/models/forum.py
作用：forum 表 ORM 模型，只描述表结构，不包含任何业务逻辑。
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.topics import Topic

class Forum(Base):
    """版块表。"""
    __tablename__ = "forum"
    __table_args__ = (
        Index("uk_forum_id", "forum_id", unique=True),
        Index("idx_uid", "uid"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "版块表",
        },
    )
    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="版块ID"
    )
    forum_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="版块唯一编号，对外暴露的编号"
    )
    uid: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="版块创建用户ID"
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="版块名称")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="版块描述")
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="版块图标地址")
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=0, server_default=text("0"), comment="是否启用：0关闭，1启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="删除时间")

    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="forum")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Forum id={self.id} forum_id={self.forum_id} name={self.name!r} description={self.description!r}>"