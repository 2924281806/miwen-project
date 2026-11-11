"""
文件名：app/crud/crud_topic.py
作用：topics 表纯数据库操作（增删改查），不处理权限、状态、审核等业务规则判断。
说明：作者校验、字段白名单等业务逻辑一律放在 api 层。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.topics import Topic, TopicFavorite, TopicVote


def get_topic_by_id(db: Session, topic_id: int, include_deleted: bool = False) -> Optional[Topic]:
    """按主键查询帖子，默认过滤软删除数据。"""
    stmt = select(Topic).where(Topic.id == topic_id)
    if not include_deleted:
        stmt = stmt.where(Topic.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_topic_by_topic_id(db: Session, topic_id: int, include_deleted: bool = False) -> Optional[Topic]:
    """按帖子唯一编号 topic_id 查询帖子，默认过滤软删除数据。"""
    stmt = select(Topic).where(Topic.topic_id == topic_id)
    if not include_deleted:
        stmt = stmt.where(Topic.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def count_topics_by_uid(db: Session, uid: str) -> int:
    """统计某用户的发帖数（仅正常状态）。"""
    stmt = (
        select(func.count())
        .select_from(Topic)
        .where(Topic.uid == uid, Topic.status == 1, Topic.deleted_at.is_(None))
    )
    return int(db.execute(stmt).scalar() or 0)


def create_topic(
    db: Session,
    *,
    topic_id: int,
    forum_id: int,
    uid: str,
    title: str,
    content: str,
    cover: Optional[str] = None,
) -> Topic:
    """新增帖子并返回持久化后的实例（is_top / status 等字段走数据库默认值）。"""
    topic = Topic(
        topic_id=topic_id,
        forum_id=forum_id,
        uid=uid,
        title=title,
        content=content,
        cover=cover,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def update_topic(db: Session, topic: Topic, update_data: dict) -> Topic:
    """按字段字典更新帖子（只更新传入的字段）。"""
    for field, value in update_data.items():
        setattr(topic, field, value)
    db.commit()
    db.refresh(topic)
    return topic


def soft_delete_topic(db: Session, topic: Topic) -> Topic:
    """软删除帖子（写入 deleted_at，不做物理删除）。"""
    topic.deleted_at = datetime.now()
    db.commit()
    db.refresh(topic)
    return topic


def _apply_filters(
    stmt,
    *,
    forum_id: Optional[int] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    include_deleted: bool = False,
):
    """给查询语句追加列表筛选条件（列表与计数复用，保证口径一致）。"""
    if not include_deleted:
        stmt = stmt.where(Topic.deleted_at.is_(None))
    if forum_id is not None:
        stmt = stmt.where(Topic.forum_id == forum_id)
    if uid is not None:
        stmt = stmt.where(Topic.uid == uid)
    if keyword:
        stmt = stmt.where(Topic.title.like(f"%{keyword}%"))
    if status is not None:
        stmt = stmt.where(Topic.status == status)
    return stmt


def list_topics(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 10,
    forum_id: Optional[int] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    include_deleted: bool = False,
) -> List[Topic]:
    """分页查询帖子列表：置顶优先，其次按最后回复时间倒序。"""
    stmt = _apply_filters(
        select(Topic),
        forum_id=forum_id,
        uid=uid,
        keyword=keyword,
        status=status,
        include_deleted=include_deleted,
    )
    stmt = (
        stmt.order_by(Topic.is_top.desc(), Topic.last_post_at.desc(), Topic.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def count_topics(
    db: Session,
    *,
    forum_id: Optional[int] = None,
    uid: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    include_deleted: bool = False,
) -> int:
    """统计满足筛选条件的帖子总数（分页用）。"""
    stmt = _apply_filters(
        select(Topic.id),
        forum_id=forum_id,
        uid=uid,
        keyword=keyword,
        status=status,
        include_deleted=include_deleted,
    )
    return db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

def has_voted(db: Session, uid: str, topic_id: int) -> bool:
    """判断用户是否已点赞某帖子（topic_id 为对外暴露的帖子编号）。"""
    stmt = select(TopicVote.id).where(TopicVote.uid == uid, TopicVote.topic_id == topic_id)
    return db.execute(stmt).scalar_one_or_none() is not None


def has_favorited(db: Session, uid: str, topic_id: int) -> bool:
    """判断用户是否已收藏某帖子（topic_id 为对外暴露的帖子编号）。"""
    stmt = select(TopicFavorite.id).where(TopicFavorite.uid == uid, TopicFavorite.topic_id == topic_id)
    return db.execute(stmt).scalar_one_or_none() is not None


def get_user_topic_flags(db: Session, uid: str, topic_ids: List[int]) -> dict:
    """
    批量查询用户对一组帖子的点赞 / 收藏状态。

    :param uid: 用户 uid
    :param topic_ids: 对外暴露的帖子编号列表
    :return: {topic_id: {"is_votes": 0/1, "is_favorites": 0/1}}，未点赞 / 未收藏默认 0
    """
    flags = {tid: {"is_votes": 0, "is_favorites": 0} for tid in topic_ids}
    if not topic_ids:
        return flags

    voted_ids = set(
        db.execute(
            select(TopicVote.topic_id).where(TopicVote.uid == uid, TopicVote.topic_id.in_(topic_ids))
        ).scalars().all()
    )
    favorited_ids = set(
        db.execute(
            select(TopicFavorite.topic_id).where(
                TopicFavorite.uid == uid, TopicFavorite.topic_id.in_(topic_ids)
            )
        ).scalars().all()
    )
    for tid in voted_ids:
        flags[tid]["is_votes"] = 1
    for tid in favorited_ids:
        flags[tid]["is_favorites"] = 1
    return flags


def like_topic(db: Session, topic: Topic, uid: str) -> Topic:
    """点赞帖子：写入点赞记录并累加帖子点赞数。"""
    db.add(TopicVote(uid=uid, topic_id=topic.topic_id))
    topic.votes += 1
    db.commit()
    db.refresh(topic)
    return topic

def unlike_topic(db: Session, topic: Topic, uid: str) -> Topic:
    """取消点赞帖子：删除点赞记录并减少帖子点赞数。"""
    vote = db.execute(
        select(TopicVote).where(TopicVote.uid == uid, TopicVote.topic_id == topic.topic_id)
    ).scalar_one_or_none()
    if vote is not None:
        db.delete(vote)
    topic.votes -= 1
    db.commit()
    db.refresh(topic)
    return topic

def favorite_topic(db: Session, topic: Topic, uid: str) -> Topic:
    """收藏帖子：写入收藏记录并累加帖子收藏数。"""
    db.add(TopicFavorite(uid=uid, topic_id=topic.topic_id))
    topic.favorites += 1
    db.commit()
    db.refresh(topic)
    return topic

def unfavorite_topic(db: Session, topic: Topic, uid: str) -> Topic:
    """取消收藏帖子：删除收藏记录并减少帖子收藏数。"""
    favorite = db.execute(
        select(TopicFavorite).where(TopicFavorite.uid == uid, TopicFavorite.topic_id == topic.topic_id)
    ).scalar_one_or_none()
    if favorite is not None:
        db.delete(favorite)
    topic.favorites -= 1
    db.commit()
    db.refresh(topic)
    return topic