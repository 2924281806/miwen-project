"""
文件名：alembic/versions/0024_comment_ids_and_replies.py
作用：1. 给 topic_comments 增加 comment_id（四位数随机唯一编号）列并回填历史数据；
      2. 新建 topic_comment_replies 评论回复表（reply_id 四位数随机唯一编号，外链 topic_id 与 comment_id）；
      3. 把旧结构（parent_id 自关联）中的回复数据迁移进回复表，然后删除 parent_id 列。
"""

import random

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0024_comment_ids_replies"
down_revision = "0023_topic_comments"
branch_labels = None
depends_on = None


def _rand_4digit(used: set) -> int:
    """生成一个未使用的四位数（1000-9999）随机编号。"""
    while True:
        value = random.randint(1000, 9999)
        if value not in used:
            used.add(value)
            return value


def upgrade() -> None:
    conn = op.get_bind()

    # 1. topic_comments 增加 comment_id 列（先可空，回填后再收紧）
    op.add_column(
        "topic_comments",
        sa.Column("comment_id", mysql.BIGINT(unsigned=True), nullable=True, comment="评论唯一编号（四位数随机生成）"),
    )

    # 2. 回填历史评论的 comment_id
    used_comment_ids: set = set()
    comment_ids = conn.execute(sa.text("SELECT id FROM topic_comments ORDER BY id")).scalars().all()
    for row_id in comment_ids:
        cid = _rand_4digit(used_comment_ids)
        conn.execute(
            sa.text("UPDATE topic_comments SET comment_id = :cid WHERE id = :rid"),
            {"cid": cid, "rid": row_id},
        )

    # 3. comment_id 收紧为非空并加唯一索引（建回复表前完成：外键需要引用列有索引）
    op.alter_column("topic_comments", "comment_id", existing_type=mysql.BIGINT(unsigned=True), nullable=False)
    op.create_index("uk_comment_id", "topic_comments", ["comment_id"], unique=True)

    # 4. 新建评论回复表
    op.create_table(
        "topic_comment_replies",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column("reply_id", mysql.BIGINT(unsigned=True), nullable=False, comment="回复唯一编号（四位数随机生成）"),
        sa.Column("topic_id", mysql.BIGINT(unsigned=True), nullable=False, comment="帖子唯一编号，关联 topics.topic_id"),
        sa.Column("comment_id", mysql.BIGINT(unsigned=True), nullable=False, comment="评论唯一编号，关联 topic_comments.comment_id"),
        sa.Column("uid", sa.String(length=32), nullable=False, comment="回复用户uid，关联 users.uid"),
        sa.Column("content", sa.Text(), nullable=False, comment="回复内容"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="回复时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.topic_id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["topic_comments.comment_id"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="评论回复表",
    )
    op.create_index("uk_reply_id", "topic_comment_replies", ["reply_id"], unique=True)
    op.create_index("idx_comment_id", "topic_comment_replies", ["comment_id"], unique=False)

    # 5. 把旧 parent_id 结构里的回复迁移进回复表
    old_replies = conn.execute(
        sa.text(
            "SELECT id, topic_id, parent_id, uid, content, created_at "
            "FROM topic_comments WHERE parent_id IS NOT NULL ORDER BY id"
        )
    ).all()
    if old_replies:
        used_reply_ids: set = set()
        for _rid, topic_id, parent_id, uid, content, created_at in old_replies:
            parent_comment_id = conn.execute(
                sa.text("SELECT comment_id FROM topic_comments WHERE id = :pid"),
                {"pid": parent_id},
            ).scalar()
            if parent_comment_id is None:
                continue
            reply_id = _rand_4digit(used_reply_ids)
            conn.execute(
                sa.text(
                    "INSERT INTO topic_comment_replies (reply_id, topic_id, comment_id, uid, content, created_at) "
                    "VALUES (:rpid, :tid, :cid, :uid, :content, :created_at)"
                ),
                {"rpid": reply_id, "tid": topic_id, "cid": parent_comment_id, "uid": uid,
                 "content": content, "created_at": created_at},
            )
        conn.execute(sa.text("DELETE FROM topic_comments WHERE parent_id IS NOT NULL"))

    # 6. 删除 parent_id 列（先删索引与外键）
    fk_name = conn.execute(
        sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'topic_comments' "
            "AND COLUMN_NAME = 'parent_id' AND REFERENCED_TABLE_NAME IS NOT NULL"
        )
    ).scalar()
    if fk_name:
        op.drop_constraint(fk_name, "topic_comments", type_="foreignkey")
    op.drop_index("idx_parent_id", table_name="topic_comments")
    op.drop_column("topic_comments", "parent_id")


def downgrade() -> None:
    """回滚：删除回复表，去掉 comment_id 列，恢复 parent_id 列。"""
    op.drop_table("topic_comment_replies")
    op.drop_index("uk_comment_id", table_name="topic_comments")
    op.drop_column("topic_comments", "comment_id")
    op.add_column(
        "topic_comments",
        sa.Column("parent_id", mysql.BIGINT(unsigned=True), nullable=True, comment="父评论ID"),
    )
