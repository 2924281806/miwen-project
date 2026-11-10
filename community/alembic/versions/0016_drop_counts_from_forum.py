"""
文件名：alembic/versions/0016_drop_counts_from_forum.py
作用：删除 forum 表的 favorites / votes / comments 三个计数字段。
说明：与 0014_add_counts_to_forum 相反的回退操作，模型与 Schema 已同步移除。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0016_drop_counts_from_forum"
down_revision = "0016_add_counts_to_topics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """删除 forum 表三个计数字段。"""
    with op.batch_alter_table("forum") as batch_op:
        batch_op.drop_column("favorites")
        batch_op.drop_column("votes")
        batch_op.drop_column("comments")


def downgrade() -> None:
    """回滚：恢复三个计数字段（TINYINT NOT NULL DEFAULT 0）。"""
    with op.batch_alter_table("forum") as batch_op:
        batch_op.add_column(
            sa.Column(
                "favorites",
                mysql.TINYINT(),
                nullable=False,
                server_default=sa.text("0"),
                comment="收藏数",
            )
        )
        batch_op.add_column(
            sa.Column(
                "votes",
                mysql.TINYINT(),
                nullable=False,
                server_default=sa.text("0"),
                comment="点赞数",
            )
        )
        batch_op.add_column(
            sa.Column(
                "comments",
                mysql.TINYINT(),
                nullable=False,
                server_default=sa.text("0"),
                comment="评论数",
            )
        )
