"""
文件名：app/models/topics.py
作用：topics 表 ORM 模型，只描述表结构，不包含任何业务逻辑。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.forum import Forum


class Topic(Base):
    """帖子表。"""

    __tablename__ = "topics"
    __table_args__ = (
        Index("uk_topic_id", "topic_id", unique=True),
        Index("idx_forum_id", "forum_id"),
        Index("idx_uid", "uid"),
        Index("idx_last_post_at", "last_post_at"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "帖子表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主题ID"
    )
    topic_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="帖子唯一编号，对外暴露的编号"
    )
    forum_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("forum.forum_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属圈子ID，关联 forum.forum_id",
    )
    uid: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="发帖用户ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="帖子标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="帖子内容")
    cover: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="封面图")
    is_top: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=0, server_default=text("0"), comment="是否置顶：0否1是"
    )
    is_essence: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=0, server_default=text("0"), comment="是否精华：0否1是"
    )
    is_closed: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=0, server_default=text("0"), comment="是否关闭回复：0否1是"
    )
    views: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"), comment="浏览量"
    )
    reply_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"), comment="回复数量"
    )
    last_post_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="最后回复时间"
    )
    last_post_uid: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True), nullable=True, comment="最后回复人ID"
    )
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=1, server_default=text("1"), comment="0待审核，1正常，2隐藏"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="发帖时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="软删除")

    forum: Mapped["Forum"] = relationship("Forum", back_populates="topics")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Topic id={self.id} topic_id={self.topic_id} title={self.title!r} forum_id={self.forum_id}>"