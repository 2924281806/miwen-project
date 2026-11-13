"""
文件名：app/models/user_follow.py
作用：user_follows 表 ORM 模型（用户关注记录表），只描述表结构，不包含任何业务逻辑。
说明：参照 topic_votes 的设计，(follower_uid, following_uid) 唯一，
      记录存在即代表关注，接口返回时按当前登录用户计算 is_follow（0/1）。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserFollow(Base):
    """用户关注记录表：一个用户对另一个用户最多一条记录，是否存在即代表是否关注。"""

    __tablename__ = "user_follows"
    __table_args__ = (
        Index("uk_follower_following", "follower_uid", "following_uid", unique=True),
        Index("idx_following_uid", "following_uid"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "用户关注记录表",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="记录ID"
    )
    follower_uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="关注者uid，关联 users.uid",
    )
    following_uid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.uid", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="被关注者uid，关联 users.uid",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="关注时间"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserFollow id={self.id} follower={self.follower_uid!r} following={self.following_uid!r}>"
