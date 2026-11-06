"""
文件名：alembic/versions/0012_add_join_type_to_forum.py
作用：给 forum 表增加 join_type 字段，表示加入圈子方式（public 公开加入 / private 需要申请）。
说明：revision 标识必须不超过 32 字符（alembic_version.version_num 为 VARCHAR(32)）。
      字段带 DEFAULT 'public'，存量圈子自动回填为公开加入，无需单独写回填语句。
"""

from alembic import op

revision = "0012_add_join_type_to_forum"
down_revision = "0011_add_unique_name_category"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 join_type 字段（非空，默认 public）。"""
    op.execute(
        "ALTER TABLE `forum` ADD COLUMN `join_type` VARCHAR(20) NOT NULL DEFAULT 'public' "
        "COMMENT '加入方式：public公开加入，private需要申请' AFTER `status`"
    )


def downgrade() -> None:
    """删除 join_type 字段。"""
    op.execute("ALTER TABLE `forum` DROP COLUMN `join_type`")