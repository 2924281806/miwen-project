"""
文件名：app/models/forum.py
作用：forum 表 ORM 模型，只描述表结构，不包含任何业务逻辑。
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.forum_category import ForumCategory
    from app.models.topics import Topic
    from app.models.user import User

class Forum(Base):
    """圈子表。"""
    __tablename__ = "forum"
    __table_args__ = (
        Index("uk_forum_id", "forum_id", unique=True),
        Index("idx_uid", "uid"),
        Index("idx_category_id", "category_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "圈子表",
        },
    )
    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="圈子ID"
    )
    forum_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="圈子唯一编号，对外暴露的编号"
    )
    category_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("forum_category.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属分类ID，关联 forum_category.id",
    )
    category_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="所属分类名称，与 forum_category.name 保持一致"
    )
    uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="圈子创建用户uid，关联 users.uid",
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="圈子名称")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="圈子描述")
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="圈子图标地址")
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=0, server_default=text("0"), comment="是否启用：0关闭，1启用"
    )

    join_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="public",
        server_default=text("'public'"),
        comment="加入方式：public公开加入，private需要申请",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="删除时间")

    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="forum")
    category: Mapped["ForumCategory"] = relationship("ForumCategory", back_populates="forums")
    user: Mapped["User"] = relationship("User")

    user_counts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"), comment="圈子用户数量"
    )

    topic_counts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"), comment="圈子话题数量"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Forum id={self.id} forum_id={self.forum_id} name={self.name!r} description={self.description!r}>"