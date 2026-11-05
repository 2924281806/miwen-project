"""
文件名：alembic/versions/0009_rename_user_id_to_uid.py
作用：把 forum、topics 表中的 user_id 列统一重命名为 uid，索引 idx_user_id 重命名为 idx_uid。
说明：topics.last_post_user_id 语义上同样是"用户ID"，一并重命名为 last_post_uid，
      与 ORM 模型（app/models/topics.py）保持一致，避免查询时出现列不存在。
"""

from alembic import op

revision = "0009_rename_user_id_to_uid"
down_revision = "0008_add_fk_topics_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """重命名列与索引。"""
    op.execute(
        "ALTER TABLE `forum` CHANGE COLUMN `user_id` `uid` "
        "BIGINT(20) UNSIGNED NOT NULL COMMENT '版块创建用户ID'"
    )
    op.execute("ALTER TABLE `forum` RENAME INDEX `idx_user_id` TO `idx_uid`")

    op.execute(
        "ALTER TABLE `topics` CHANGE COLUMN `user_id` `uid` "
        "BIGINT(20) UNSIGNED NOT NULL COMMENT '发帖用户ID'"
    )
    op.execute(
        "ALTER TABLE `topics` CHANGE COLUMN `last_post_user_id` `last_post_uid` "
        "BIGINT(20) UNSIGNED DEFAULT NULL COMMENT '最后回复人ID'"
    )
    op.execute("ALTER TABLE `topics` RENAME INDEX `idx_user_id` TO `idx_uid`")


def downgrade() -> None:
    """回滚：恢复原有列名与索引名。"""
    op.execute("ALTER TABLE `topics` RENAME INDEX `idx_uid` TO `idx_user_id`")
    op.execute(
        "ALTER TABLE `topics` CHANGE COLUMN `last_post_uid` `last_post_user_id` "
        "BIGINT(20) UNSIGNED DEFAULT NULL COMMENT '最后回复人ID'"
    )
    op.execute(
        "ALTER TABLE `topics` CHANGE COLUMN `uid` `user_id` "
        "BIGINT(20) UNSIGNED NOT NULL COMMENT '发帖用户ID'"
    )

    op.execute("ALTER TABLE `forum` RENAME INDEX `idx_uid` TO `idx_user_id`")
    op.execute(
        "ALTER TABLE `forum` CHANGE COLUMN `uid` `user_id` "
        "BIGINT(20) UNSIGNED NOT NULL COMMENT '版块创建用户ID'"
    )