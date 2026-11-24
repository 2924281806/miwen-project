"""
文件名：alembic/versions/0023_create_topic_comments.py
作用：创建 topic_comments 帖子评论表与 comment_likes 评论点赞记录表，实现帖子下的评论功能。
说明：评论支持两级结构——顶级评论 parent_id 为空，回复指向某条顶级评论；
      点赞记录 (comment_id, uid) 唯一，点赞数量与点赞用户列表由记录统计得出。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0023_topic_comments"
down_revision = "ee34766ae5a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建帖子评论表与评论点赞记录表。"""
    op.create_table(
        "topic_comments",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="评论ID"),
        sa.Column("topic_id", mysql.BIGINT(unsigned=True), nullable=False, comment="帖子唯一编号，关联 topics.topic_id"),
        sa.Column("uid", sa.String(length=32), nullable=False, comment="评论用户uid，关联 users.uid"),
        sa.Column("parent_id", mysql.BIGINT(unsigned=True), nullable=True, comment="父评论ID，顶级评论为空，回复时指向某条顶级评论"),
        sa.Column("content", sa.Text(), nullable=False, comment="评论内容"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="评论时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.topic_id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["topic_comments.id"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="帖子评论表",
    )
    op.create_index("idx_topic_id", "topic_comments", ["topic_id"], unique=False)
    op.create_index("idx_parent_id", "topic_comments", ["parent_id"], unique=False)

    op.create_table(
        "comment_likes",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column("comment_id", mysql.BIGINT(unsigned=True), nullable=False, comment="评论ID，关联 topic_comments.id"),
        sa.Column("uid", sa.String(length=32), nullable=False, comment="点赞用户uid，关联 users.uid"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="点赞时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["comment_id"], ["topic_comments.id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="评论点赞记录表",
    )
    op.create_index("uk_comment_uid", "comment_likes", ["comment_id", "uid"], unique=True)


def downgrade() -> None:
    """回滚：删除评论相关表。"""
    op.drop_table("comment_likes")
    op.drop_table("topic_comments")
