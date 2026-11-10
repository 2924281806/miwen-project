"""
文件名：alembic/versions/0018_create_topic_votes_favorites.py
作用：实现"每个用户对帖子的点赞 / 收藏状态"。
说明：is_votes / is_favorites 是按用户区分的状态，不能存在 topics 表的一个列里
      （一列只能存一个用户的值），因此：
      1. 删除 topics.is_votes 列（语义错误，无法表达多用户状态）；
      2. 新建 topic_votes / topic_favorites 两张关联表，
         (uid, topic_id) 唯一，记录存在即代表该用户点赞 / 收藏了该帖子；
      3. 接口返回时按当前登录用户计算 is_votes / is_favorites（0/1），
         topics.votes / topics.favorites 继续作为总计数维护。
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0018_topic_votes_favorites"
down_revision = "0017_add_is_votes_to_topics"
branch_labels = None
depends_on = None


def _create_action_table(table_name: str, comment: str) -> None:
    """创建点赞 / 收藏记录表（结构相同：id + uid + topic_id + created_at）。"""
    op.create_table(
        table_name,
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column(
            "uid",
            sa.String(length=32),
            nullable=False,
            comment=f"{'点赞' if table_name == 'topic_votes' else '收藏'}用户uid，关联 users.uid",
        ),
        sa.Column("topic_id", mysql.BIGINT(unsigned=True), nullable=False, comment="帖子唯一编号，关联 topics.topic_id"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment=f"{comment}时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["uid"], ["users.uid"], ondelete="RESTRICT", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.topic_id"], ondelete="RESTRICT", onupdate="CASCADE"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment=f"{comment}记录表",
    )
    op.create_index("uk_uid_topic", table_name, ["uid", "topic_id"], unique=True)


def upgrade() -> None:
    """删除 topics.is_votes，创建两张用户-帖子关联表。"""
    with op.batch_alter_table("topics") as batch_op:
        batch_op.drop_column("is_votes")
    _create_action_table("topic_votes", "点赞")
    _create_action_table("topic_favorites", "收藏")


def downgrade() -> None:
    """回滚：删除两张关联表，恢复 topics.is_votes。"""
    op.drop_table("topic_favorites")
    op.drop_table("topic_votes")
    with op.batch_alter_table("topics") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_votes",
                mysql.TINYINT(),
                nullable=False,
                server_default=sa.text("0"),
                comment="是否点赞：0否1是",
            )
        )
