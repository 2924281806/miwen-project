"""
文件名：alembic/versions/0011_add_unique_name_category.py
作用：给 forum_category.name 增加唯一索引 uk_name，保证分类名称不重名。
说明：revision 标识必须不超过 32 字符（alembic_version.version_num 为 VARCHAR(32)）。
      建唯一索引前先清理历史重名数据（保留 id 最小的一条，其余追加 #dup-{id} 后缀），
      避免存量重复名称导致索引创建失败。
"""

from alembic import op

revision = "0011_add_unique_name_category"
down_revision = "0010_create_forum_category_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """清理重名数据后创建唯一索引。"""
    op.execute(
        "UPDATE `forum_category` c "
        "JOIN ("
        "  SELECT `name`, MIN(`id`) AS keep_id FROM `forum_category` "
        "  GROUP BY `name` HAVING COUNT(*) > 1"
        ") d ON c.`name` = d.`name` AND c.`id` <> d.keep_id "
        "SET c.`name` = CONCAT(LEFT(c.`name`, 88), '#dup-', c.`id`)"
    )
    op.create_index("uk_name", "forum_category", ["name"], unique=True)


def downgrade() -> None:
    """删除唯一索引。"""
    op.drop_index("uk_name", table_name="forum_category")