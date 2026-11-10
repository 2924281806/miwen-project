"""
文件名：alembic/versions/0017_add_is_votes_to_topics.py
作用：给 topics 表新增 is_votes 字段（是否点赞：0否1是）。
说明：TINYINT NOT NULL DEFAULT 0，存量行自动回填 0；
      与 app/models/topics.py 中的列定义保持一致。
      （由 alembic autogenerate 生成后清理，去除了误检测的
      server_default / comment 噪音变更。）
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0017_add_is_votes_to_topics"
down_revision = "0016_drop_counts_from_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """topics 表新增 is_votes 字段。"""
    with op.batch_alter_table("topics") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_votes",
                mysql.TINYINT(),
                nullable=False,
                server_default=sa.text("0"),
                comment="是否点赞：0否1是",
            )
        )


def downgrade() -> None:
    """回滚：删除 is_votes 字段。"""
    with op.batch_alter_table("topics") as batch_op:
        batch_op.drop_column("is_votes")
