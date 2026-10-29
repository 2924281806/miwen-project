"""
文件名：alembic/versions/0001_create_users_table.py
作用：初始迁移 - 创建 users 用户表。
说明：结构与需求文档中的 DDL 保持一致（InnoDB + utf8mb4 + 唯一索引）。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0001_create_users_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 users 表。"""
    op.create_table(
        "users",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="用户ID"),
        sa.Column("username", sa.String(50), nullable=False, comment="用户名，唯一"),
        sa.Column("email", sa.String(100), nullable=True, comment="邮箱"),
        sa.Column("password_hash", sa.String(255), nullable=False, comment="密码哈希"),
        sa.Column("nickname", sa.String(50), nullable=True, comment="昵称"),
        sa.Column("avatar", sa.String(255), nullable=True, comment="头像地址"),
        sa.Column("signature", sa.String(500), nullable=True, comment="个性签名"),
        sa.Column(
            "status",
            mysql.TINYINT,
            nullable=False,
            server_default=sa.text("1"),
            comment="状态：0禁用，1正常，2待激活",
        ),
        sa.Column("level", sa.Integer, nullable=False, server_default=sa.text("0"), comment="用户等级"),
        sa.Column("points", sa.Integer, nullable=False, server_default=sa.text("0"), comment="积分"),
        sa.Column("last_login_at", sa.DateTime, nullable=True, comment="最后登录时间"),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="注册时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True, comment="软删除时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uk_username"),
        sa.UniqueConstraint("email", name="uk_email"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="用户表",
    )

    # MySQL 的 ON UPDATE CURRENT_TIMESTAMP 无法通过 create_table 表达，这里单独补上
    op.execute(
        "ALTER TABLE `users` MODIFY COLUMN `updated_at` DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
    )


def downgrade() -> None:
    """回滚：删除 users 表。"""
    op.drop_table("users")