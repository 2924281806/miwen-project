"""
文件名：alembic/versions/0006_add_topic_id_to_topics.py
作用：为 topics 表新增 topic_id 字段（帖子唯一编号，唯一索引 uk_topic_id）。
说明：先加可空列 -> 回填历史数据 -> 改为 NOT NULL -> 建唯一索引，保证存量数据可平滑升级。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0006_add_topic_id_to_topics"
down_revision = "0005_create_forum_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 topic_id 字段。"""
    op.add_column(
        "topics",
        sa.Column("topic_id", mysql.BIGINT(unsigned=True), nullable=True, comment="帖子唯一编号，对外暴露的编号"),
    )

    # 存量数据回填：先用自增主键作为唯一编号，新帖子的编号由应用层生成（8 位数字）
    op.execute("UPDATE `topics` SET `topic_id` = `id` WHERE `topic_id` IS NULL")

    op.alter_column(
        "topics",
        "topic_id",
        existing_type=mysql.BIGINT(unsigned=True),
        nullable=False,
        comment="帖子唯一编号，对外暴露的编号",
    )
    op.create_index("uk_topic_id", "topics", ["topic_id"], unique=True)


def downgrade() -> None:
    """回滚：删除 topic_id 字段与索引。"""
    op.drop_index("uk_topic_id", table_name="topics")
    op.drop_column("topics", "topic_id")