"""
文件名：app/crud/crud_comment.py
作用：topic_comments / comment_likes 表纯数据库操作（增删改查），不处理业务规则判断。
说明：业务校验（帖子是否存在、父评论归属、是否重复点赞等）一律放在 api 层。
"""

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.topic_comment import CommentLike, TopicComment
from app.models.user import User


def get_comment_by_id(db: Session, comment_id: int) -> Optional[TopicComment]:
    """按主键查询评论。"""
    stmt = select(TopicComment).where(TopicComment.id == comment_id)
    return db.execute(stmt).scalar_one_or_none()


def list_topic_comments(db: Session, topic_id: int) -> List[TopicComment]:
    """查询帖子的全部顶级评论（parent_id 为空），按评论时间正序。"""
    stmt = (
        select(TopicComment)
        .where(TopicComment.topic_id == topic_id, TopicComment.parent_id.is_(None))
        .order_by(TopicComment.created_at.asc(), TopicComment.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_replies(db: Session, parent_ids: List[int]) -> List[TopicComment]:
    """查询一组评论的回复（parent_id 非空），按评论时间正序。"""
    if not parent_ids:
        return []
    stmt = (
        select(TopicComment)
        .where(TopicComment.parent_id.in_(parent_ids))
        .order_by(TopicComment.created_at.asc(), TopicComment.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_like_users(db: Session, comment_ids: List[int]) -> Dict[int, List[User]]:
    """查询一组评论的点赞用户信息，返回 {comment_id: [User, ...]}（按点赞时间正序）。"""
    if not comment_ids:
        return {}
    stmt = (
        select(CommentLike.comment_id, User)
        .join(User, User.uid == CommentLike.uid)
        .where(CommentLike.comment_id.in_(comment_ids))
        .order_by(CommentLike.created_at.asc())
    )
    result: Dict[int, List[User]] = {}
    for comment_id, user in db.execute(stmt).all():
        result.setdefault(comment_id, []).append(user)
    return result


def create_comment(
    db: Session,
    *,
    topic_id: int,
    uid: str,
    content: str,
    parent_id: Optional[int] = None,
) -> TopicComment:
    """新增评论 / 回复。"""
    comment = TopicComment(topic_id=topic_id, uid=uid, content=content, parent_id=parent_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def like_comment(db: Session, *, comment_id: int, uid: str) -> CommentLike:
    """新增评论点赞记录（唯一索引兜底，业务层已保证不重复点赞）。"""
    record = CommentLike(comment_id=comment_id, uid=uid)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def unlike_comment(db: Session, *, comment_id: int, uid: str) -> bool:
    """删除评论点赞记录，返回是否删除了记录（未点赞时返回 False）。"""
    stmt = select(CommentLike).where(
        CommentLike.comment_id == comment_id, CommentLike.uid == uid
    )
    record = db.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def count_comments_by_topic(db: Session, topic_id: int) -> int:
    """统计帖子的评论总数（含回复）。"""
    stmt = (
        select(func.count())
        .select_from(TopicComment)
        .where(TopicComment.topic_id == topic_id)
    )
    return db.execute(stmt).scalar_one()
