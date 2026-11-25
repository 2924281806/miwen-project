"""
文件名：app/models/topic_comment.py
作用：topic_comments 表（帖子评论表）、topic_comment_replies 表（评论回复表）与
      comment_likes 表（评论点赞记录表）的 ORM 模型，只描述表结构，不包含任何业务逻辑。
说明：评论与回复分表存储——
      1. 评论表通过对外暴露的 comment_id（4 位数随机唯一编号）标识一条评论；
      2. 回复表通过 reply_id（4 位数随机唯一编号）标识一条回复，
         回复外链到帖子 topic_id 与评论 comment_id（回复只能挂在评论下，不支持回复的回复）；
      3. 点赞记录 (comment_id, uid) 唯一，记录存在即代表点赞，点赞数量与点赞用户列表由记录统计得出。
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TopicComment(Base):
    """帖子评论表：一条记录代表一条评论。"""

    __tablename__ = "topic_comments"
    __table_args__ = (
        Index("idx_topic_id", "topic_id"),
        Index("uk_comment_id", "comment_id", unique=True),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "帖子评论表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="记录ID"
    )
    comment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="评论唯一编号（四位数随机生成）"
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
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="评论时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TopicComment id={self.id} comment_id={self.comment_id} topic_id={self.topic_id} uid={self.uid!r}>"


class TopicCommentReply(Base):
    """评论回复表：一条记录代表某条评论下的一条回复，外链到帖子与评论。"""

    __tablename__ = "topic_comment_replies"
    __table_args__ = (
        Index("uk_reply_id", "reply_id", unique=True),
        Index("idx_comment_id", "comment_id"),
        Index("idx_reply_to_id", "reply_to_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "评论回复表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="记录ID"
    )
    reply_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), nullable=False, comment="回复唯一编号（四位数随机生成）"
    )
    topic_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topics.topic_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="帖子唯一编号，关联 topics.topic_id",
    )
    comment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topic_comments.comment_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="评论唯一编号，关联 topic_comments.comment_id",
    )
    uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="回复用户uid，关联 users.uid",
    )
    reply_to_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("topic_comment_replies.reply_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="被回复的回复编号（toComment），回复其他回复时记录，直接回复评论为空",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="回复内容")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="回复时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TopicCommentReply id={self.id} reply_id={self.reply_id} comment_id={self.comment_id} uid={self.uid!r}>"


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
        comment="评论记录ID，关联 topic_comments.id",
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
