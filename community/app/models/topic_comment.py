"""
文件名：app/models/topic_comment.py
作用：topic_comments 表（帖子评论表）与 comment_likes 表（评论点赞记录表）的 ORM 模型，
      只描述表结构，不包含任何业务逻辑。
说明：评论支持两级结构——顶级评论 parent_id 为空，回复指向某条顶级评论（parent_id 不允许再指向回复）；
      点赞记录 (comment_id, uid) 唯一，记录存在即代表点赞，点赞数量与点赞用户列表由记录统计得出。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TopicComment(Base):
    """帖子评论表：一条记录代表一条评论或一条回复。"""

    __tablename__ = "topic_comments"
    __table_args__ = (
        Index("idx_topic_id", "topic_id"),
        Index("idx_parent_id", "parent_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "帖子评论表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="评论ID"
    )
    topic_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topics.topic_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="帖子唯一编号，关联 topics.topic_id",
    )
    uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="评论用户uid，关联 users.uid",
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topic_comments.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="父评论ID，顶级评论为空，回复时指向某条顶级评论",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="评论时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TopicComment id={self.id} topic_id={self.topic_id} uid={self.uid!r}>"


class CommentLike(Base):
    """评论点赞记录表：一个用户对一条评论最多一条记录，是否存在即代表是否点赞。"""

    __tablename__ = "comment_likes"
    __table_args__ = (
        Index("uk_comment_uid", "comment_id", "uid", unique=True),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "评论点赞记录表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="记录ID"
    )
    comment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topic_comments.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="评论ID，关联 topic_comments.id",
    )
    uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="点赞用户uid，关联 users.uid",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="点赞时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CommentLike id={self.id} comment_id={self.comment_id} uid={self.uid!r}>"
