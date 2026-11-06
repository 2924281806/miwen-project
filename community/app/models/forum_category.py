"""
文件名：app/models/forum_category.py
作用：forum_category 表 ORM 模型，只描述表结构，不包含任何业务逻辑。
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.forum import Forum


class ForumCategory(Base):
    """圈子分类表。"""

    __tablename__ = "forum_category"
    __table_args__ = (
        Index("uk_name", "name", unique=True),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "圈子分类表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="分类ID，自动生成唯一编号"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="删除时间")

    forums: Mapped[List["Forum"]] = relationship("Forum", back_populates="category")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ForumCategory id={self.id} name={self.name!r}>"