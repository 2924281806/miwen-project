"""
文件名：app/crud/crud_forum.py
作用：forum 表纯数据库操作（增删改查），不处理权限、状态、审核等业务规则判断。
说明：作者校验、字段白名单等业务逻辑一律放在 api 层。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.forum import Forum
from app.models.forum_member import ForumMember
from app.models.topics import Topic


def get_forum_by_id(db: Session, forum_id: int, include_deleted: bool = False) -> Optional[Forum]:
    """按主键查询圈子，默认过滤软删除数据。"""
    stmt = select(Forum).where(Forum.id == forum_id)
    if not include_deleted:
        stmt = stmt.where(Forum.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()

def get_forum_by_forum_id(db: Session, forum_id: int, include_deleted: bool = False) -> Optional[Forum]:
    """按圈子唯一编号 forum_id 查询圈子，默认过滤软删除数据。"""
    stmt = select(Forum).where(Forum.forum_id == forum_id)
    if not include_deleted:
        stmt = stmt.where(Forum.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def create_forum(
    db: Session,
    *,
    forum_id: int,
    uid: str,
    category_id: int,
    category_name: str,
    name: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    status: int = 1,
    join_type: str = "public",
) -> Forum:
    """新增圈子并返回持久化后的实例。"""
    forum = Forum(
        forum_id=forum_id,
        uid=uid,
        category_id=category_id,
        category_name=category_name,
        name=name,
        description=description,
        icon=icon,
        status=status,
        join_type=join_type,
    )
    db.add(forum)
    db.commit()
    db.refresh(forum)
    return forum


def update_forum(db: Session, forum: Forum, update_data: dict) -> Forum:
    """按字段字典更新圈子（只更新传入的字段）。"""
    for field, value in update_data.items():
        setattr(forum, field, value)
    db.commit()
    db.refresh(forum)
    return forum


def soft_delete_forum(db: Session, forum: Forum) -> Forum:
    """软删除圈子：写入 deleted_at。"""
    forum.deleted_at = datetime.now()
    db.commit()
    db.refresh(forum)
    return forum


def _apply_filters(
    stmt,
    *,
    name: Optional[str] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    category_id: Optional[int] = None,
    include_deleted: Optional[bool] = False,
):
    """给查询语句追加列表筛选条件（列表与计数复用，保证口径一致）。"""
    if not include_deleted:
        stmt = stmt.where(Forum.deleted_at.is_(None))
    if name:
        stmt = stmt.where(Forum.name.like(f"%{name}%"))
    if uid is not None:
        stmt = stmt.where(Forum.uid == uid)
    if keyword:
        stmt = stmt.where(Forum.name.like(f"%{keyword}%") | Forum.description.like(f"%{keyword}%"))
    if status is not None:
        stmt = stmt.where(Forum.status == status)
    if category_id is not None:
        stmt = stmt.where(Forum.category_id == category_id)
    return stmt


def list_forums(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    category_id: Optional[int] = None,
    include_deleted: bool = False,
) -> List[Forum]:
    """分页查询圈子列表：按创建时间倒序。"""
    stmt = _apply_filters(
        select(Forum),
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        category_id=category_id,
        include_deleted=include_deleted,
    )
    stmt = stmt.order_by(Forum.created_at.desc()).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())

def all_list(db: Session) -> List[Forum]:
    """查询全部圈子：按创建时间倒序，默认过滤软删除数据。"""
    stmt = _apply_filters(select(Forum))
    stmt = stmt.order_by(Forum.created_at.desc())
    return list(db.execute(stmt).scalars().all())

def count_forums(
    db: Session,
    *,
    name: Optional[str] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    category_id: Optional[int] = None,
    include_deleted: bool = False,
) -> int:
    """统计满足筛选条件的圈子总数（分页用）。"""
    stmt = _apply_filters(
        select(Forum),
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        category_id=category_id,
        include_deleted=include_deleted,
    )
    return db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()


def count_forums_by_category(db: Session, category_id: int) -> int:
    """统计某分类下的未删除圈子数量（用于删除分类前的前置校验）。"""
    stmt = select(func.count()).select_from(Forum).where(
        Forum.category_id == category_id, Forum.deleted_at.is_(None)
    )
    return db.execute(stmt).scalar_one()


def update_category_name_by_category_id(db: Session, category_id: int, category_name: str) -> int:
    """分类改名后同步圈子表冗余的 category_name 字段，返回受影响行数。"""
    stmt = (
        Forum.__table__.update()
        .where(Forum.category_id == category_id)
        .values(category_name=category_name)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0


# ==================== 加入圈子相关 ====================
def get_join_record(db: Session, uid: str, forum_id: int) -> Optional[ForumMember]:
    """查询一条加入记录（uid 是否加入了 forum_id 圈子）。"""
    stmt = select(ForumMember).where(
        ForumMember.uid == uid,
        ForumMember.forum_id == forum_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def is_joined(db: Session, uid: str, forum_id: int) -> bool:
    """判断 uid 是否已加入 forum_id 圈子（记录存在即代表已加入）。"""
    return get_join_record(db, uid, forum_id) is not None


def join_forum(db: Session, *, uid: str, forum_id: int) -> ForumMember:
    """新增加入记录（唯一索引兜底，业务层已保证不重复加入）。"""
    record = ForumMember(uid=uid, forum_id=forum_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def leave_forum(db: Session, *, uid: str, forum_id: int) -> bool:
    """删除加入记录，返回是否删除了记录（未加入时返回 False）。"""
    record = get_join_record(db, uid, forum_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def get_user_forum_flags(db: Session, uid: str, forum_ids: List[int]) -> dict:
    """
    批量查询用户对一组圈子的加入状态。

    :param uid: 用户 uid
    :param forum_ids: 对外暴露的圈子编号列表
    :return: {forum_id: {"is_join": 0/1}}，未加入默认 0
    """
    flags = {fid: {"is_join": 0} for fid in forum_ids}
    if not forum_ids:
        return flags

    joined_ids = set(
        db.execute(
            select(ForumMember.forum_id).where(
                ForumMember.uid == uid, ForumMember.forum_id.in_(forum_ids)
            )
        ).scalars().all()
    )
    for fid in joined_ids:
        flags[fid]["is_join"] = 1
    return flags

def get_forum_user_counts(db: Session, forum_id: int) -> int:
    """查询 forum_id 圈子的用户数量。"""
    stmt = select(func.count()).select_from(ForumMember).where(
        ForumMember.forum_id == forum_id)
    return db.execute(stmt).scalar_one()

def get_forum_topic_counts(db: Session, forum_id: int) -> int:
    """查询 forum_id 圈子的话题数量。"""
    stmt = select(func.count()).select_from(Topic).where(
        Topic.forum_id == forum_id
    )
    return db.execute(stmt).scalar_one()