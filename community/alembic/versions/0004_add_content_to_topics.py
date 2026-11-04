"""
文件名：alembic/versions/0004_add_content_to_topics.py
作用：为 topics 表新增 content 帖子内容字段。
说明：content 为必填长文本（MySQL TEXT），新增后通过 ALTER 调整到 title 之后，便于阅读表结构。
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_add_content_to_topics"
down_revision = "0003_create_topics_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 content 字段。"""
    op.add_column(
        "topics",
        sa.Column("content", sa.Text, nullable=False, comment="帖子内容"),
    )
    op.execute(
        "ALTER TABLE `topics` MODIFY COLUMN `content` TEXT NOT NULL COMMENT '帖子内容' AFTER `title`"
    )


def downgrade() -> None:
    """回滚：删除 content 字段。"""
    op.drop_column("topics", "content")