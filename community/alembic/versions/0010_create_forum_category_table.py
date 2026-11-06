"""
文件名：alembic/versions/0010_create_forum_category_table.py
作用：新增版块分类表 forum_category，并给 forum 表增加 category_id / category_name 字段。
说明：forum.category_id 外键关联 forum_category.id；存量版块先回填到"默认分类"，再收紧为非空，
      避免加非空约束时因历史数据为空而失败。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0010_create_forum_category_table"
down_revision = "0009_rename_user_id_to_uid"
branch_labels = None
depends_on = None

DEFAULT_CATEGORY_NAME = "默认分类"


def upgrade() -> None:
    """创建分类表并给 forum 增加分类字段。"""
    op.create_table(
        "forum_category",
        sa.Column(
            "id",
            mysql.BIGINT(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="分类ID，自动生成唯一编号",
        ),
        sa.Column("name", sa.String(100), nullable=False, comment="分类名称"),
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
        comment="版块分类表",
    )

    bind = op.get_bind()
    bind.execute(sa.text("INSERT INTO `forum_category` (`name`) VALUES (:name)"), {"name": DEFAULT_CATEGORY_NAME})
    default_id = bind.execute(sa.text("SELECT `id` FROM `forum_category` ORDER BY `id` LIMIT 1")).scalar()

    op.execute(
        "ALTER TABLE `forum` ADD COLUMN `category_id` BIGINT(20) UNSIGNED NULL "
        "COMMENT '所属分类ID，关联 forum_category.id' AFTER `forum_id`"
    )
    op.execute(
        "ALTER TABLE `forum` ADD COLUMN `category_name` VARCHAR(100) NULL "
        "COMMENT '所属分类名称，与 forum_category.name 保持一致' AFTER `category_id`"
    )
    bind.execute(
        sa.text(
            "UPDATE `forum` SET `category_id` = :cid, `category_name` = :cname "
            "WHERE `category_id` IS NULL"
        ),
        {"cid": default_id, "cname": DEFAULT_CATEGORY_NAME},
    )

    op.execute(
        "ALTER TABLE `forum` MODIFY COLUMN `category_id` BIGINT(20) UNSIGNED NOT NULL "
        "COMMENT '所属分类ID，关联 forum_category.id'"
    )
    op.execute(
        "ALTER TABLE `forum` MODIFY COLUMN `category_name` VARCHAR(100) NOT NULL "
        "COMMENT '所属分类名称，与 forum_category.name 保持一致'"
    )
    op.execute("ALTER TABLE `forum` ADD KEY `idx_category_id` (`category_id`)")
    op.create_foreign_key(
        "fk_forum_category_id",
        "forum",
        "forum_category",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    """回滚：删除 forum 的分类字段与分类表。"""
    op.drop_constraint("fk_forum_category_id", "forum", type_="foreignkey")
    op.execute("ALTER TABLE `forum` DROP KEY `idx_category_id`")
    op.execute("ALTER TABLE `forum` DROP COLUMN `category_name`")
    op.execute("ALTER TABLE `forum` DROP COLUMN `category_id`")
    op.drop_table("forum_category")