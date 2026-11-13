"""
文件名：app/models/forum_member.py
作用：forum_members 表 ORM 模型（圈子成员记录表），只描述表结构，不包含任何业务逻辑。
说明：参照 topic_votes 的设计，(uid, forum_id) 唯一，
      记录存在即代表已加入圈子，接口返回时按当前登录用户计算 is_join（0/1）。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ForumMember(Base):
    """圈子成员记录表：一个用户对一个圈子最多一条记录，是否存在即代表是否加入。"""

    __tablename__ = "forum_members"
    __table_args__ = (
        Index("uk_uid_forum", "uid", "forum_id", unique=True),
        Index("idx_forum_id", "forum_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "圈子成员记录表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="记录ID"
    )
    uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="成员uid，关联 users.uid",
    )
    forum_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("forum.forum_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="圈子唯一编号，关联 forum.forum_id",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="加入时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ForumMember id={self.id} uid={self.uid!r} forum_id={self.forum_id}>"
