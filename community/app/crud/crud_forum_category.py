"""
文件名：app/crud/crud_forum_category.py
作用：forum_category 表纯数据库操作（增删改查），不处理业务规则判断。
说明：分类是否可删除、名称唯一性等业务规则一律放在 api 层。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.forum_category import ForumCategory


def get_category_by_id(
    db: Session, category_id: int, include_deleted: bool = False
) -> Optional[ForumCategory]:
    """按分类ID查询分类，默认过滤软删除数据。"""
    stmt = select(ForumCategory).where(ForumCategory.id == category_id)
    if not include_deleted:
        stmt = stmt.where(ForumCategory.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_category_by_name(
    db: Session,
    name: str,
    include_deleted: bool = False,
    exclude_id: Optional[int] = None,
) -> Optional[ForumCategory]:
    """按分类名称查询分类，默认过滤软删除数据；exclude_id 用于修改时排除自身。"""
    stmt = select(ForumCategory).where(ForumCategory.name == name)
    if not include_deleted:
        stmt = stmt.where(ForumCategory.deleted_at.is_(None))
    if exclude_id is not None:
        stmt = stmt.where(ForumCategory.id != exclude_id)
    return db.execute(stmt).scalar_one_or_none()


def create_category(db: Session, *, name: str) -> ForumCategory:
    """新增分类并返回持久化后的实例。"""
    category = ForumCategory(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: ForumCategory, update_data: dict) -> ForumCategory:
    """按字段字典更新分类（只更新传入的字段）。"""
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def soft_delete_category(db: Session, category: ForumCategory) -> ForumCategory:
    """软删除分类：写入 deleted_at。

    名称列有唯一索引 uk_name，软删除后仍占用原名称会阻止后续创建同名分类，
    因此这里把名称改写为「原名称#deleted-{id}」（截断保证不超过 100 字），释放原名称。
    """
    suffix = f"#deleted-{category.id}"
    max_base_len = 100 - len(suffix)
    category.name = category.name[:max_base_len] + suffix
    category.deleted_at = datetime.now()
    db.commit()
    db.refresh(category)
    return category


def get_default_category(db: Session) -> Optional[ForumCategory]:
    """取最早创建的未删除分类，用于未指定分类时的兜底。"""
    stmt = (
        select(ForumCategory)
        .where(ForumCategory.deleted_at.is_(None))
        .order_by(ForumCategory.id.asc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_categories(db: Session, include_deleted: bool = False) -> List[ForumCategory]:
    """查询分类列表：按创建时间倒序。"""
    stmt = select(ForumCategory)
    if not include_deleted:
        stmt = stmt.where(ForumCategory.deleted_at.is_(None))
    stmt = stmt.order_by(ForumCategory.created_at.desc())
    return list(db.execute(stmt).scalars().all())