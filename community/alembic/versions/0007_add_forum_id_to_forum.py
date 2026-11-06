"""
文件名：alembic/versions/0007_add_forum_id_to_forum.py
作用：为 forum 表新增 forum_id 字段（圈子唯一编号，唯一索引 uk_forum_id）。
说明：先加可空列 -> 回填历史数据 -> 改为 NOT NULL -> 建唯一索引，保证存量数据可平滑升级。
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0007_add_forum_id_to_forum"
down_revision = "0006_add_topic_id_to_topics"
branch_labels = None
depends_on = None

def upgrade() -> None:
    """新增 forum_id 字段。"""
    op.add_column(
        "forum",
        sa.Column("forum_id", mysql.BIGINT(unsigned=True), nullable=True, comment="圈子唯一编号，对外暴露的编号"),
    )
    op.execute("UPDATE `forum` SET `forum_id` = `id` WHERE `forum_id` IS NULL")
   
    op.alter_column(
        "forum",
        "forum_id",
        existing_type=mysql.BIGINT(unsigned=True),
        nullable=False,
        comment="圈子唯一编号，对外暴露的编号",
    )
    op.create_index("uk_forum_id", "forum", ["forum_id"], unique=True)


def downgrade() -> None:
    """回滚：删除 forum_id 字段与索引。"""
    op.drop_index("uk_forum_id", table_name="forum")
    op.drop_column("forum", "forum_id")
