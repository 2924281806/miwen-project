"""
文件名：alembic/versions/0022_create_forum_members.py
作用：创建 forum_members 圈子成员记录表，实现"用户加入圈子"的关系数据。
说明：is_join 是按当前登录用户区分的状态，不能存在 forum 表的一个列里
      （一列只能存一个用户的值），因此：
      1. 新建 forum_members 关联表，(uid, forum_id) 唯一，
         记录存在即代表该用户已加入该圈子；
      2. 接口返回圈子信息时按当前登录用户计算 is_join（0/1）。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0022_forum_members"
down_revision = "0021_user_follows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建圈子成员记录表。"""
    op.create_table(
        "forum_members",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column("uid", sa.String(length=32), nullable=False, comment="成员uid，关联 users.uid"),
        sa.Column("forum_id", mysql.BIGINT(unsigned=True), nullable=False, comment="圈子唯一编号，关联 forum.forum_id"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="加入时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["forum_id"], ["forum.forum_id"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="圈子成员记录表",
    )
    op.create_index("uk_uid_forum", "forum_members", ["uid", "forum_id"], unique=True)
    op.create_index("idx_forum_id", "forum_members", ["forum_id"], unique=False)


def downgrade() -> None:
    """回滚：删除 forum_members 表。"""
    op.drop_table("forum_members")
