"""
文件名：alembic/versions/0008_add_fk_topics_forum.py
作用：为 topics.forum_id 建立指向 forum.forum_id 的外键约束（fk_topics_forum_id）。
说明：topics.forum_id 存放的是版块对外编号 forum_id，因此外键引用 forum 的唯一索引列 uk_forum_id。
      加外键前先清理引用了不存在版块的脏数据，避免约束创建失败。
"""

from alembic import op

revision = "0008_add_fk_topics_forum"
down_revision = "0007_add_forum_id_to_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 topics -> forum 的外键约束。"""
    # 历史数据可能引用了已不存在的版块编号，这类脏数据无法通过外键校验，先清理
    op.execute(
        "DELETE t FROM `topics` t "
        "LEFT JOIN `forum` f ON t.`forum_id` = f.`forum_id` "
        "WHERE f.`forum_id` IS NULL"
    )

    op.create_foreign_key(
        "fk_topics_forum_id",
        source_table="topics",
        referent_table="forum",
        local_cols=["forum_id"],
        remote_cols=["forum_id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    """回滚：删除外键约束。"""
    op.drop_constraint("fk_topics_forum_id", "topics", type_="foreignkey")