"""
文件名：alembic/versions/0002_add_uid_to_users.py
作用：为 users 表新增 uid 字段（用户唯一标识，唯一索引 uk_uid）。
说明：先加可空列 -> 回填历史数据 -> 改为 NOT NULL -> 建唯一索引，保证存量数据可平滑升级。
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_add_uid_to_users"
down_revision = "0001_create_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 uid 字段。"""
    op.add_column(
        "users",
        sa.Column("uid", sa.String(32), nullable=True, comment="用户唯一标识，对外暴露的ID"),
    )

    # 存量数据回填：MySQL 的 UUID() 在 UPDATE 中逐行取值，去掉横线后为 32 位十六进制
    op.execute("UPDATE `users` SET `uid` = REPLACE(UUID(), '-', '') WHERE `uid` IS NULL")

    op.alter_column(
        "users",
        "uid",
        existing_type=sa.String(32),
        nullable=False,
        comment="用户唯一标识，对外暴露的ID",
    )
    op.create_index("uk_uid", "users", ["uid"], unique=True)


def downgrade() -> None:
    """回滚：删除 uid 字段与索引。"""
    op.drop_index("uk_uid", table_name="users")
    op.drop_column("users", "uid")