"""
文件名：alembic/versions/0013_fix_circle_comments.py
作用：把存量表结构里残留的"版块"注释统一修正为"圈子"，与代码/文档术语保持一致。
说明：早期迁移 0003 / 0005 / 0010 建表时写的是"版块"，这些迁移已在库中执行过，
      修改历史迁移文件的注释不会回写到数据库，因此单独用一个迁移修正注释。
      只改注释，不改列类型、默认值与索引，MODIFY COLUMN 保持原有列定义与顺序。
"""

from alembic import op

revision = "0013_fix_circle_comments"
down_revision = "0012_add_join_type_to_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """修正 forum / forum_category / topics 的表注释与列注释。"""
    op.execute(
        "ALTER TABLE `forum` "
        "MODIFY COLUMN `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '圈子ID', "
        "MODIFY COLUMN `forum_id` BIGINT UNSIGNED NOT NULL COMMENT '圈子唯一编号，对外暴露的编号', "
        "MODIFY COLUMN `uid` BIGINT UNSIGNED NOT NULL COMMENT '圈子创建用户ID', "
        "MODIFY COLUMN `name` VARCHAR(200) NOT NULL COMMENT '圈子名称', "
        "MODIFY COLUMN `description` VARCHAR(255) NULL COMMENT '圈子描述', "
        "MODIFY COLUMN `icon` VARCHAR(255) NULL COMMENT '圈子图标地址'"
    )
    op.execute("ALTER TABLE `forum` COMMENT = '圈子表'")
    op.execute("ALTER TABLE `forum_category` COMMENT = '圈子分类表'")
    op.execute(
        "ALTER TABLE `topics` "
        "MODIFY COLUMN `forum_id` BIGINT UNSIGNED NOT NULL COMMENT '所属圈子ID'"
    )


def downgrade() -> None:
    """回滚为"版块"注释。"""
    op.execute(
        "ALTER TABLE `forum` "
        "MODIFY COLUMN `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '版块ID', "
        "MODIFY COLUMN `forum_id` BIGINT UNSIGNED NOT NULL COMMENT '版块唯一编号，对外暴露的编号', "
        "MODIFY COLUMN `uid` BIGINT UNSIGNED NOT NULL COMMENT '版块创建用户ID', "
        "MODIFY COLUMN `name` VARCHAR(200) NOT NULL COMMENT '版块名称', "
        "MODIFY COLUMN `description` VARCHAR(255) NULL COMMENT '版块描述', "
        "MODIFY COLUMN `icon` VARCHAR(255) NULL COMMENT '版块图标地址'"
    )
    op.execute("ALTER TABLE `forum` COMMENT = '版块表'")
    op.execute("ALTER TABLE `forum_category` COMMENT = '版块分类表'")
    op.execute(
        "ALTER TABLE `topics` "
        "MODIFY COLUMN `forum_id` BIGINT UNSIGNED NOT NULL COMMENT '所属版块ID'"
    )