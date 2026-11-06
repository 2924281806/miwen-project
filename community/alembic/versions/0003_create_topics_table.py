"""
文件名：alembic/versions/0003_create_topics_table.py
作用：创建 topics 帖子表（含 forum_id / uid / last_post_at 三个索引）。
说明：结构与需求文档中的 DDL 保持一致（InnoDB + utf8mb4）。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0003_create_topics_table"
down_revision = "0002_add_uid_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 topics 表。"""
    op.create_table(
        "topics",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="主题ID"),
        sa.Column("forum_id", mysql.BIGINT(unsigned=True), nullable=False, comment="所属圈子ID"),
        sa.Column("uid", mysql.BIGINT(unsigned=True), nullable=False, comment="发帖用户ID"),
        sa.Column("title", sa.String(200), nullable=False, comment="帖子标题"),
        sa.Column("cover", sa.String(255), nullable=True, comment="封面图"),
        sa.Column("is_top", mysql.TINYINT, nullable=False, server_default=sa.text("0"), comment="是否置顶：0否1是"),
        sa.Column(
            "is_essence", mysql.TINYINT, nullable=False, server_default=sa.text("0"), comment="是否精华：0否1是"
        ),
        sa.Column(
            "is_closed", mysql.TINYINT, nullable=False, server_default=sa.text("0"), comment="是否关闭回复：0否1是"
        ),
        sa.Column("views", sa.Integer, nullable=False, server_default=sa.text("0"), comment="浏览量"),
        sa.Column("reply_count", sa.Integer, nullable=False, server_default=sa.text("0"), comment="回复数量"),
        sa.Column(
            "last_post_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="最后回复时间",
        ),
        sa.Column("last_post_uid", mysql.BIGINT(unsigned=True), nullable=True, comment="最后回复人ID"),
        sa.Column(
            "status",
            mysql.TINYINT,
            nullable=False,
            server_default=sa.text("1"),
            comment="0待审核，1正常，2隐藏",
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="发帖时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True, comment="软删除"),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="帖子表",
    )

    op.create_index("idx_forum_id", "topics", ["forum_id"])
    op.create_index("idx_uid", "topics", ["uid"])
    op.create_index("idx_last_post_at", "topics", ["last_post_at"])

    # MySQL 的 ON UPDATE CURRENT_TIMESTAMP 无法通过 create_table 表达，这里单独补上
    op.execute(
        "ALTER TABLE `topics` MODIFY COLUMN `updated_at` DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
    )


def downgrade() -> None:
    """回滚：删除 topics 表。"""
    op.drop_index("idx_last_post_at", table_name="topics")
    op.drop_index("idx_uid", table_name="topics")
    op.drop_index("idx_forum_id", table_name="topics")
    op.drop_table("topics")