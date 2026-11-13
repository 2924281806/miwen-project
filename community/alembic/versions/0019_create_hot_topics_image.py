"""
文件名：alembic/versions/0019_create_hot_topics_image.py
作用：新增热门话题图片表 hot_topics_image。
说明：独立图片表，不关联其他表；img_url 唯一。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0019_hot_topics_image"
down_revision = "0018_topic_votes_favorites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建热门话题图片表。"""
    op.create_table(
        "hot_topics_image",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="图片ID，自动生成唯一编号",
        ),
        sa.Column(
            "img_url",
            sa.String(255),
            nullable=False,
            comment="图片URL",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            comment="创建时间",
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="删除时间"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="热门话题图片表",
    )
    op.create_index("uk_img_url", "hot_topics_image", ["img_url"], unique=True)


def downgrade() -> None:
    """回滚：删除热门话题图片表。"""
    op.drop_index("uk_img_url", table_name="hot_topics_image")
    op.drop_table("hot_topics_image")
