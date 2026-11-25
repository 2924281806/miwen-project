"""
文件名：alembic/versions/0025_reply_to_id.py
作用：给 topic_comment_replies 增加 reply_to_id 列（toComment：回复其他回复时记录被回复的回复编号），
      新回复与被回复的回复同级挂在所属评论下。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0025_reply_to_id"
down_revision = "0024_comment_ids_replies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """给回复表加 reply_to_id 列（含自引用外键与索引）。"""
    op.add_column(
        "topic_comment_replies",
        sa.Column(
            "reply_to_id",
            mysql.BIGINT(unsigned=True),
            nullable=True,
            comment="被回复的回复编号（toComment），回复其他回复时记录，直接回复评论为空",
        ),
    )
    op.create_index("idx_reply_to_id", "topic_comment_replies", ["reply_to_id"], unique=False)
    op.create_foreign_key(
        "fk_reply_to_id",
        "topic_comment_replies",
        "topic_comment_replies",
        ["reply_to_id"],
        ["reply_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    """回滚：删除 reply_to_id 列。"""
    op.drop_constraint("fk_reply_to_id", "topic_comment_replies", type_="foreignkey")
    op.drop_index("idx_reply_to_id", table_name="topic_comment_replies")
    op.drop_column("topic_comment_replies", "reply_to_id")
