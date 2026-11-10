"""
文件名：alembic/versions/0015_add_fk_forum_topics_uid.py
作用：把 forum.uid / topics.uid 关联到 users.uid（外键约束）。
说明：users.uid 是 VARCHAR(32)（如 '0001'），而 forum / topics 的 uid 原为 BIGINT
      且存量数据存的是 users.id，因此本迁移分三步：
      1. 把 forum.uid / topics.uid 列类型改为 VARCHAR(32)（显式 utf8mb4_unicode_ci，
         与 users 表一致，避免 MySQL 8 默认 utf8mb4_0900_ai_ci 导致的排序规则冲突）；
      2. 存量数据按 users.id -> users.uid 映射回填（JOIN 比较显式 COLLATE）；
      3. 添加外键 fk_forum_uid / fk_topics_uid -> users.uid（RESTRICT / CASCADE）。
      各步骤幂等，可安全重跑。
"""

from alembic import op

revision = "0015_add_fk_forum_topics_uid"
down_revision = "0014_add_counts_to_forum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """forum / topics 的 uid 改为 VARCHAR 并关联 users.uid。"""
    # 1. 列类型 BIGINT -> VARCHAR(32)，排序规则与 users.uid 保持一致
    op.execute(
        "ALTER TABLE `forum` "
        "MODIFY COLUMN `uid` VARCHAR(32) "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL "
        "COMMENT '圈子创建用户uid，关联 users.uid'"
    )
    op.execute(
        "ALTER TABLE `topics` "
        "MODIFY COLUMN `uid` VARCHAR(32) "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL "
        "COMMENT '发帖用户uid，关联 users.uid'"
    )

    # 2. 存量数据回填：uid 存的是 users.id，映射为 users.uid（比较时显式指定排序规则）
    op.execute(
        "UPDATE `forum` f JOIN `users` u "
        "ON f.uid = CAST(u.id AS CHAR) COLLATE utf8mb4_unicode_ci "
        "SET f.uid = u.uid"
    )
    op.execute(
        "UPDATE `topics` t JOIN `users` u "
        "ON t.uid = CAST(u.id AS CHAR) COLLATE utf8mb4_unicode_ci "
        "SET t.uid = u.uid"
    )

    # 3. 添加外键（已存在则先删除，保证幂等）
    op.execute(
        "ALTER TABLE `forum` DROP FOREIGN KEY `fk_forum_uid`"
    ) if _fk_exists("forum", "fk_forum_uid") else None
    op.execute(
        "ALTER TABLE `topics` DROP FOREIGN KEY `fk_topics_uid`"
    ) if _fk_exists("topics", "fk_topics_uid") else None
    op.execute(
        "ALTER TABLE `forum` "
        "ADD CONSTRAINT `fk_forum_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) "
        "ON DELETE RESTRICT ON UPDATE CASCADE"
    )
    op.execute(
        "ALTER TABLE `topics` "
        "ADD CONSTRAINT `fk_topics_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) "
        "ON DELETE RESTRICT ON UPDATE CASCADE"
    )


def _fk_exists(table: str, fk_name: str) -> bool:
    """判断外键是否已存在（用于幂等处理）。"""
    from sqlalchemy import text

    conn = op.get_bind()
    result = conn.execute(
        text(
            f"SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS "
            f"WHERE CONSTRAINT_SCHEMA = DATABASE() "
            f"AND TABLE_NAME = '{table}' AND CONSTRAINT_NAME = '{fk_name}'"
        )
    )
    return result.scalar_one() > 0


def downgrade() -> None:
    """回滚：删除外键，uid 映射回 users.id，类型改回 BIGINT。"""
    op.execute("ALTER TABLE `forum` DROP FOREIGN KEY `fk_forum_uid`")
    op.execute("ALTER TABLE `topics` DROP FOREIGN KEY `fk_topics_uid`")

    # 数据回滚：users.uid 映射回 users.id
    op.execute(
        "UPDATE `forum` f JOIN `users` u "
        "ON f.uid = u.uid COLLATE utf8mb4_unicode_ci "
        "SET f.uid = CAST(u.id AS CHAR)"
    )
    op.execute(
        "UPDATE `topics` t JOIN `users` u "
        "ON t.uid = u.uid COLLATE utf8mb4_unicode_ci "
        "SET t.uid = CAST(u.id AS CHAR)"
    )

    op.execute(
        "ALTER TABLE `forum` "
        "MODIFY COLUMN `uid` BIGINT UNSIGNED NOT NULL COMMENT '圈子创建用户ID'"
    )
    op.execute(
        "ALTER TABLE `topics` "
        "MODIFY COLUMN `uid` BIGINT UNSIGNED NOT NULL COMMENT '发帖用户ID'"
    )
