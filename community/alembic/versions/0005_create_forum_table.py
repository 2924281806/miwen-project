"""
文件名：alembic/versions/0005_create_forum_table.py
作用：创建 forum 圈子表（含 uid 普通索引）。
说明：结构与 app/models/forum.py 保持一致（InnoDB + utf8mb4 + utf8mb4_unicode_ci）。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0005_create_forum_table"
down_revision = "0004_add_content_to_topics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 forum 表。"""
    op.create_table(
        "forum",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="圈子ID"),
        sa.Column("uid", mysql.BIGINT(unsigned=True), nullable=False, comment="圈子创建用户ID"),
        sa.Column("name", sa.String(200), nullable=False, comment="圈子名称"),
        sa.Column("description", sa.String(255), nullable=True, comment="圈子描述"),
        sa.Column("icon", sa.String(255), nullable=True, comment="圈子图标地址"),
        sa.Column(
            "status", mysql.TINYINT, nullable=False, server_default=sa.text("0"), comment="是否启用：0关闭，1启用"
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True, comment="删除时间"),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="圈子表",
    )
    op.create_index("idx_uid", "forum", ["uid"])
    op.execute(
        "ALTER TABLE `forum` MODIFY COLUMN `updated_at` DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
    )


def downgrade() -> None:
    """回滚：删除 forum 表。"""
    op.drop_index("idx_uid", table_name="forum")
    op.drop_table("forum")