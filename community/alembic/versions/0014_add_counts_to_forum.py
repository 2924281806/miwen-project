"""
文件名：alembic/versions/0014_add_counts_to_forum.py
作用：给 forum 表新增 favorites / votes / comments 三个计数字段（收藏数 / 点赞数 / 评论数）。
说明：三个字段均为 TINYINT NOT NULL DEFAULT 0，存量行自动回填 0；
      与 app/models/forum.py 中的列定义保持一致。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0014_add_counts_to_forum"
down_revision = "0013_fix_circle_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """forum 表新增三个计数字段。"""
    with op.batch_alter_table("forum") as batch_op:
        batch_op.add_column(
            sa.Column("favorites", mysql.TINYINT(), nullable=False, server_default=sa.text("0"), comment="收藏数")
        )
        batch_op.add_column(
            sa.Column("votes", mysql.TINYINT(), nullable=False, server_default=sa.text("0"), comment="点赞数")
        )
        batch_op.add_column(
            sa.Column("comments", mysql.TINYINT(), nullable=False, server_default=sa.text("0"), comment="评论数")
        )


def downgrade() -> None:
    """回滚：删除三个计数字段。"""
    with op.batch_alter_table("forum") as batch_op:
        batch_op.drop_column("comments")
        batch_op.drop_column("votes")
        batch_op.drop_column("favorites")
