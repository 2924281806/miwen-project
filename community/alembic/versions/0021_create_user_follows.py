"""
文件名：alembic/versions/0021_create_user_follows.py
作用：创建 user_follows 用户关注记录表，实现"用户关注用户"的关系数据。
说明：is_follow 是按当前登录用户区分的状态，不能存在 users 表的一个列里
      （一列只能存一个用户的值），因此：
      1. 新建 user_follows 关联表，(follower_uid, following_uid) 唯一，
         记录存在即代表该用户关注了对方；
      2. 接口返回他人信息时按当前登录用户计算 is_follow（0/1）。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0021_user_follows"
down_revision = "d49ad90b02c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建用户关注记录表。"""
    op.create_table(
        "user_follows",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column("follower_uid", sa.String(length=32), nullable=False, comment="关注者uid，关联 users.uid"),
        sa.Column("following_uid", sa.String(length=32), nullable=False, comment="被关注者uid，关联 users.uid"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="关注时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["follower_uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["following_uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="用户关注记录表",
    )
    op.create_index("uk_follower_following", "user_follows", ["follower_uid", "following_uid"], unique=True)
    op.create_index("idx_following_uid", "user_follows", ["following_uid"], unique=False)


def downgrade() -> None:
    """回滚：删除 user_follows 表。"""
    op.drop_table("user_follows")
