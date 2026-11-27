"""
文件名：app/crud/crud_comment.py
作用：topic_comments / topic_comment_replies / comment_likes 表纯数据库操作（增删改查），
      不处理业务规则判断。
说明：业务校验（帖子是否存在、评论归属、是否重复点赞等）一律放在 api 层。
"""

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.topic_comment import CommentLike, TopicComment, TopicCommentReply
from app.models.user import User


def get_comment_by_id(db: Session, comment_row_id: int) -> Optional[TopicComment]:
    """按主键查询评论（内部记录ID，一般不对外暴露）。"""
    stmt = select(TopicComment).where(TopicComment.id == comment_row_id)
    return db.execute(stmt).scalar_one_or_none()


def get_comment_by_comment_id(db: Session, comment_id: int) -> Optional[TopicComment]:
    """按对外暴露的评论唯一编号 comment_id 查询评论。"""
    stmt = select(TopicComment).where(TopicComment.comment_id == comment_id)
    return db.execute(stmt).scalar_one_or_none()


def get_reply_by_reply_id(db: Session, reply_id: int) -> Optional[TopicCommentReply]:
    """按对外暴露的回复唯一编号 reply_id 查询回复。"""
    stmt = select(TopicCommentReply).where(TopicCommentReply.reply_id == reply_id)
    return db.execute(stmt).scalar_one_or_none()


def list_topic_comments(db: Session, topic_id: int) -> List[TopicComment]:
    """查询帖子的全部评论，按评论时间正序。"""
    stmt = (
        select(TopicComment)
        .where(TopicComment.topic_id == topic_id)
        .order_by(TopicComment.created_at.asc(), TopicComment.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_replies(db: Session, comment_ids: List[int]) -> List[TopicCommentReply]:
    """查询一组评论（对外编号 comment_id）下的全部回复，按回复时间正序。"""
    if not comment_ids:
        return []
    stmt = (
        select(TopicCommentReply)
        .where(TopicCommentReply.comment_id.in_(comment_ids))
        .order_by(TopicCommentReply.created_at.asc(), TopicCommentReply.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_like_users(db: Session, comment_row_ids: List[int]) -> Dict[int, List[User]]:
    """查询一组评论（内部记录ID）的点赞用户信息，返回 {评论记录ID: [User, ...]}（按点赞时间正序）。"""
    if not comment_row_ids:
        return {}
    stmt = (
        select(CommentLike.comment_id, User)
        .join(User, User.uid == CommentLike.uid)
        .where(CommentLike.comment_id.in_(comment_row_ids))
        .order_by(CommentLike.created_at.asc())
    )
    result: Dict[int, List[User]] = {}
    for comment_id, user in db.execute(stmt).all():
        result.setdefault(comment_id, []).append(user)
    return result


def create_comment(
    db: Session,
    *,
    comment_id: int,
    topic_id: int,
    uid: str,
    content: str,
) -> TopicComment:
    """新增评论（comment_id 由 api 层随机生成并保证唯一）。"""
    comment = TopicComment(comment_id=comment_id, topic_id=topic_id, uid=uid, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def create_reply(
    db: Session,
    *,
    reply_id: int,
    topic_id: int,
    comment_id: int,
    uid: str,
    content: str,
    reply_to_id: Optional[int] = None,
) -> TopicCommentReply:
    """新增回复（reply_id 由 api 层随机生成并保证唯一，回复外链到帖子与评论；
    回复其他回复时记录 reply_to_id，新回复与被回复的回复同级挂在所属评论下）。"""
    reply = TopicCommentReply(
        reply_id=reply_id,
        topic_id=topic_id,
        comment_id=comment_id,
        uid=uid,
        content=content,
        reply_to_id=reply_to_id,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply

def count_comments(db: Session, uid: str) -> int:
    """统计用户发布的评论总数（含回复）。"""
    stmt = select(func.count()).select_from(TopicComment).where(TopicComment.uid == uid)
    return db.execute(stmt).scalar_one()

def like_comment(db: Session, *, comment_row_id: int, uid: str) -> CommentLike:
    """新增评论点赞记录（唯一索引兜底，业务层已保证不重复点赞）。"""
    record = CommentLike(comment_id=comment_row_id, uid=uid)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def unlike_comment(db: Session, *, comment_row_id: int, uid: str) -> bool:
    """删除评论点赞记录，返回是否删除了记录（未点赞时返回 False）。"""
    stmt = select(CommentLike).where(
        CommentLike.comment_id == comment_row_id, CommentLike.uid == uid
    )
    record = db.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def count_comments_by_topic(db: Session, topic_id: int) -> int:
    """统计帖子的评论总数（含回复）。"""
    comment_count = (
        db.execute(
            select(func.count())
            .select_from(TopicComment)
            .where(TopicComment.topic_id == topic_id)
        ).scalar_one()
    )
    reply_count = (
        db.execute(
            select(func.count())
            .select_from(TopicCommentReply)
            .where(TopicCommentReply.topic_id == topic_id)
        ).scalar_one()
    )
    return comment_count + reply_count

def list_comments_by_uid(db: Session, uid: str, offset: int = 0, limit: int = 10,) -> List[TopicComment]:
    """查询用户发布的评论（含回复）。"""
    stmt = (
        select(TopicComment)
        .where(TopicComment.uid == uid)
        .order_by(TopicComment.created_at.asc(), TopicComment.id.asc())
        .offset(offset)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()
