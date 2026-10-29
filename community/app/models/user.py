"""
文件名：app/models/user.py
作用：users 表 ORM 模型，只描述表结构，不包含任何业务逻辑。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, func, text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """用户表。"""

    __tablename__ = "users"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "comment": "用户表",
    }

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, comment="用户名，唯一"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, unique=True, comment="邮箱"
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像地址")
    signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个性签名")
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, default=1, server_default=text("1"), comment="状态：0禁用，1正常，2待激活"
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), comment="用户等级")
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), comment="积分")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="注册时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="软删除时间")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} username={self.username!r}>"