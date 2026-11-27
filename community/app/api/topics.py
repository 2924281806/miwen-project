"""
文件名：app/api/topics.py
作用：帖子接口（列表 / 发帖 / 改帖 / 删帖），负责路由、参数校验、权限判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.crud import crud_comment, crud_forum, crud_topic, crud_user
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.exceptions import AppException, BadRequestException, ForbiddenException, NotFoundException
from app.models.topics import Topic
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.schemas.comment import (
    CommentAuthorOut,
    CommentCreate,
    CommentOut,
    ReplyCreate,
    ReplyOut,
    ReplyToCommentOut,
)
from app.schemas.topics import AuthorOut, TopicCreate, TopicOut, TopicUpdate

logger = logging.getLogger(__name__)

topic_router = APIRouter(prefix="/topic", tags=["帖子"])


def _generate_topic_id(db: Session) -> int:
    """生成对外暴露的帖子唯一编号（8 位数字），极小概率重复时重试。"""
    for _ in range(5):
        topic_id = secrets.randbelow(90_000_000) + 10_000_000
        if crud_topic.get_topic_by_topic_id(db, topic_id, include_deleted=True) is None:
            return topic_id
    raise AppException("帖子编号生成失败，请稍后重试", code=500)


def _generate_comment_id(db: Session) -> int:
    """生成对外暴露的评论唯一编号（四位数随机），极小概率重复时重试。"""
    for _ in range(5):
        comment_id = secrets.randbelow(9000) + 1000
        if crud_comment.get_comment_by_comment_id(db, comment_id) is None:
            return comment_id
    raise AppException("评论编号生成失败，请稍后重试", code=500)


def _generate_reply_id(db: Session) -> int:
    """生成对外暴露的回复唯一编号（四位数随机），极小概率重复时重试。"""
    for _ in range(5):
        reply_id = secrets.randbelow(9000) + 1000
        if crud_comment.get_reply_by_reply_id(db, reply_id) is None:
            return reply_id
    raise AppException("回复编号生成失败，请稍后重试", code=500)


def _get_own_topic(db: Session, topic_id: int, current_user: User) -> Topic:
    """取出帖子并校验归属：只有作者本人可以修改或删除自己的帖子。"""
    topic = crud_topic.get_topic_by_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if topic.uid != current_user.uid:
        raise ForbiddenException("只能操作自己发布的帖子")
    return topic


def _topic_out(topic: Topic, current_user: Optional[User] = None, db: Session = None) -> TopicOut:
    """序列化帖子并填充当前用户的点赞 / 收藏状态（未登录时 is_votes / is_favorites 恒为 0）。"""
    out = TopicOut.model_validate(topic)
    if current_user is not None and db is not None:
        flags = crud_topic.get_user_topic_flags(db, current_user.uid, [topic.topic_id])
        flag = flags[topic.topic_id]
        out.is_votes = flag["is_votes"]
        out.is_favorites = flag["is_favorites"]
    return out


@topic_router.get(
    "/list",
    response_model=ApiResponse[PageResult[TopicOut]],
    summary="获取帖子列表",
    description="分页查询帖子，置顶优先、其次按最后回复时间倒序；可按圈子、作者、标题关键字与状态筛选，默认只返回正常状态（status=1）的帖子。",
)
def list_topics(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    forum_id: Optional[int] = Query(None, ge=1, description="按所属圈子筛选"),
    uid: Optional[str] = Query(None, max_length=32, description="按发帖用户uid筛选"),
    keyword: Optional[str] = Query(None, max_length=200, description="标题关键字，模糊匹配"),
    status: Optional[int] = Query(1, ge=0, le=2, description="状态：0待审核 1正常 2隐藏，不传表示全部"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ApiResponse[PageResult[TopicOut]]:
    """查询帖子列表（游客可访问，登录后附带当前用户的点赞 / 收藏状态）。"""
    offset = (page - 1) * pageSize
    topics = crud_topic.list_topics(
        db,
        offset=offset,
        limit=pageSize,
        forum_id=forum_id,
        uid=uid,
        keyword=keyword,
        status=status,
    )
    total = crud_topic.count_topics(
        db,
        forum_id=forum_id,
        uid=uid,
        keyword=keyword,
        status=status,
    )
    lists = [_topic_out(topic, current_user, db) for topic in topics]
    if current_user is not None:
        # 批量填充当前用户对这批帖子的点赞 / 收藏状态
        flags = crud_topic.get_user_topic_flags(db, current_user.uid, [t.topic_id for t in topics])
        for topic, out in zip(topics, lists):
            flag = flags[topic.topic_id]
            out.is_votes = flag["is_votes"]
            out.is_favorites = flag["is_favorites"]
    return ApiResponse.ok(PageResult.create(lists, total, page, pageSize=pageSize))


@topic_router.post(
    "/createPost",
    response_model=ApiResponse[TopicOut],
    summary="发布帖子",
    description="登录用户发帖，发帖人自动取自当前登录用户，并自动生成帖子唯一编号 topic_id；所属圈子必须存在且处于启用状态；置顶、加精、关闭回复、浏览量等运营字段使用数据库默认值。",
)
def create_topic(
    payload: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """发布新帖子。"""
    forum = crud_forum.get_forum_by_forum_id(db, payload.forum_id)
    if forum is None:
        raise BadRequestException("圈子不存在")
    if forum.status != 1:
        raise BadRequestException("圈子已关闭，无法发帖")

    topic = crud_topic.create_topic(
        db,
        topic_id=_generate_topic_id(db),
        forum_id=payload.forum_id,
        uid=current_user.uid,
        title=payload.title,
        content=payload.content,
        cover=payload.cover,
    )
    logger.info(
        "用户发帖 | uid=%s topic_id=%s forum_id=%s title=%s",
        current_user.id,
        topic.topic_id,
        topic.forum_id,
        topic.title,
    )
    return ApiResponse.ok(TopicOut.model_validate(topic), msg="发布成功")


@topic_router.post(
    "/update/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="修改帖子",
    description="仅作者本人可修改，只允许修改标题与封面（cover 传 null 表示清空封面）。",
)
def update_topic(
    payload: TopicUpdate,
    topic_id: int = Path(..., ge=1, description="帖子ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """修改自己发布的帖子。"""
    topic = _get_own_topic(db, topic_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException("没有需要更新的字段")

    topic = crud_topic.update_topic(db, topic, update_data)
    logger.info("用户修改帖子 | uid=%s topic_id=%s fields=%s", current_user.id, topic.id, list(update_data))
    return ApiResponse.ok(_topic_out(topic, current_user, db), msg="修改成功")


@topic_router.post(
    "/delete/{topic_id}",
    response_model=ApiResponse[None],
    summary="删除帖子",
    description="仅作者本人可删除，采用软删除（写入 deleted_at），删除后不再出现在列表与查询结果中。",
)
def delete_topic(
    topic_id: int = Path(..., ge=1, description="帖子ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """删除自己发布的帖子。"""
    topic = _get_own_topic(db, topic_id, current_user)
    crud_topic.soft_delete_topic(db, topic)
    logger.info("用户删除帖子 | uid=%s topic_id=%s", current_user.id, topic.id)
    return ApiResponse.ok(None, msg="删除成功")

@topic_router.post(
    "/like/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="点赞帖子",
    description="登录用户点赞帖子（每个用户对同一帖子只能点赞一次），点赞后帖子的 votes 累加，返回中 is_votes 为 1。",
)
def like_topic(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """点赞帖子。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if crud_topic.has_voted(db, current_user.uid, topic.topic_id):
        raise BadRequestException("您已点赞该帖子")
    topic = crud_topic.like_topic(db, topic, current_user.uid)
    logger.info("用户点赞帖子 | uid=%s topic_id=%s", current_user.uid, topic.topic_id)
    return ApiResponse.ok(_topic_out(topic, current_user, db), msg="点赞成功")

@topic_router.post(
    "/unlike/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="取消点赞帖子",
    description="登录用户取消点赞帖子（每个用户只能取消点赞一次），取消点赞后帖子的 votes 减少，返回中 is_votes 为 0。",
)
def unlike_topic(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """取消点赞帖子。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if not crud_topic.has_voted(db, current_user.uid, topic.topic_id):
        raise BadRequestException("您未点赞该帖子")
    topic = crud_topic.unlike_topic(db, topic, current_user.uid)
    logger.info("用户取消点赞帖子 | uid=%s topic_id=%s", current_user.uid, topic.topic_id)
    return ApiResponse.ok(_topic_out(topic, current_user, db), msg="取消点赞成功")

@topic_router.post(
    "/favorite/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="收藏帖子",
    description="登录用户收藏帖子（每个用户对同一帖子只能收藏一次），收藏后帖子的 favorites 累加，返回中 is_favorites 为 1。",
)
def favorite_topic(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """收藏帖子。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if crud_topic.has_favorited(db, current_user.uid, topic.topic_id):
        raise BadRequestException("您已收藏该帖子")
    topic = crud_topic.favorite_topic(db, topic, current_user.uid)
    logger.info("用户收藏帖子 | uid=%s topic_id=%s", current_user.uid, topic.topic_id)
    return ApiResponse.ok(_topic_out(topic, current_user, db), msg="收藏成功") 

@topic_router.post(
    "/unfavorite/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="取消收藏帖子",
    description="登录用户取消收藏帖子（每个用户只能取消收藏一次），取消收藏后帖子的 favorites 减少，返回中 is_favorites 为 0。",
)
def unfavorite_topic(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """取消收藏帖子。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if not crud_topic.has_favorited(db, current_user.uid, topic.topic_id):
        raise BadRequestException("您未收藏该帖子")
    topic = crud_topic.unfavorite_topic(db, topic, current_user.uid)
    logger.info("用户取消收藏帖子 | uid=%s topic_id=%s", current_user.uid, topic.topic_id)
    return ApiResponse.ok(_topic_out(topic, current_user, db), msg="取消收藏成功")
 
@topic_router.get(
    "/listDetail/{topic_id}",
    response_model=ApiResponse[TopicOut],
    summary="获取帖子详情",
    description="获取帖子详情",
)
def get_topic_list_detail(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """获取帖子详情。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if current_user is None or current_user.uid is None:
        out = _topic_out(topic, None, db)
    else:
        out = _topic_out(topic, current_user, db)
    # 附加作者信息（头像、昵称、发帖数等），供详情页作者卡片展示
    author_user = crud_user.get_user_by_uid(db, topic.uid)
    if author_user is not None:
        out.author = AuthorOut(
            uid=author_user.uid,
            username=author_user.username,
            nickname=author_user.nickname,
            avatar=author_user.avatar,
            level=author_user.level,
            posts=crud_topic.count_topics_by_uid(db, topic.uid),
            fans=0,
        )
    return ApiResponse.ok(out)


# ==================== 帖子评论 ====================
def _comment_author_out(user: Optional[User]) -> Optional[CommentAuthorOut]:
    """把 User ORM 对象转为评论用户公开信息（不存在时返回 None）。"""
    if user is None:
        return None
    return CommentAuthorOut(
        uid=user.uid,
        username=user.username,
        nickname=user.nickname,
        avatar=user.avatar,
    )


def _build_comment_out(
    comment,
    users_map: dict,
    like_users_map: dict,
    topic,
) -> CommentOut:
    """组装单条评论出参：评论编号、作者、点赞数量、点赞用户信息列表（回复由调用方填充）。"""
    like_users = like_users_map.get(comment.id, [])
    return CommentOut(
        comment_id=comment.comment_id,
        topic_id=comment.topic_id,
        content=comment.content,
        uid=comment.uid,
        created_at=comment.created_at,
        likes=len(like_users),
        author=_comment_author_out(users_map.get(comment.uid)),
        liked_users=[_comment_author_out(user) for user in like_users],
        topicTitle=topic.title,
    )


def _build_reply_out(reply, users_map: dict, replies_map: Optional[dict] = None) -> ReplyOut:
    """组装单条回复出参：回复编号、外链的帖子编号与评论编号、回复用户信息；
    回复其他回复时（reply_to_id 非空）组装 toComment（被回复的回复摘要）。"""
    to_comment = None
    if reply.reply_to_id is not None:
        target = (replies_map or {}).get(reply.reply_to_id)
        if target is not None:
            to_comment = ReplyToCommentOut(
                reply_id=target.reply_id,
                content=target.content,
                author=_comment_author_out(users_map.get(target.uid)),
            )
    return ReplyOut(
        reply_id=reply.reply_id,
        topic_id=reply.topic_id,
        comment_id=reply.comment_id,
        content=reply.content,
        uid=reply.uid,
        created_at=reply.created_at,
        author=_comment_author_out(users_map.get(reply.uid)),
        reply_to_id=reply.reply_to_id,
        to_comment=to_comment,
    )


def _load_comment_context(db: Session, comments: list) -> tuple[dict, dict]:
    """批量加载评论作者信息与点赞用户信息，返回 (users_map, like_users_map)。"""
    users_map: dict = {}
    for comment in comments:
        if comment.uid not in users_map:
            user = crud_user.get_user_by_uid(db, comment.uid)
            if user is not None:
                users_map[comment.uid] = user
    like_users_map = crud_comment.list_like_users(db, [comment.id for comment in comments])
    return users_map, like_users_map


@topic_router.get(
    "/getComments/{topic_id}",
    response_model=ApiResponse[List[CommentOut]],
    summary="获取帖子评论列表",
    description="按帖子编号查询其全部评论，包含字段：评论唯一编号 comment_id（四位数随机生成）、评论内容、评论时间、"
                "评论用户uid与用户信息、点赞数量、点赞用户信息列表、回复信息（回复挂在所属评论下，"
                "每条回复含回复编号 reply_id、外链的帖子编号与评论编号），按评论时间正序排列，游客可访问。",
)
def get_topic_comments(
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    db: Session = Depends(get_db),
) -> ApiResponse[List[CommentOut]]:
    """获取帖子下的评论列表（含回复）。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)

    if topic is None:
        raise NotFoundException("帖子不存在")

    comments = crud_comment.list_topic_comments(db, topic_id)
    replies = crud_comment.list_replies(db, [comment.comment_id for comment in comments])
    users_map, like_users_map = _load_comment_context(db, comments)
    for reply in replies:
        if reply.uid not in users_map:
            user = crud_user.get_user_by_uid(db, reply.uid)
            if user is not None:
                users_map[reply.uid] = user

    replies_map = {reply.reply_id: reply for reply in replies}
    reply_outs = {
        reply.reply_id: _build_reply_out(reply, users_map, replies_map) for reply in replies
    }
    # reply_to_id 等于某条回复的 reply_id 时，挂到该回复的 children 下，展示在它下一级
    replies_by_comment: dict = {}
    for reply in replies:
        out = reply_outs[reply.reply_id]
        parent = reply_outs.get(reply.reply_to_id) if reply.reply_to_id is not None else None
        if parent is not None and parent.reply_id != out.reply_id and parent.comment_id == out.comment_id:
            parent.children.append(out)
        else:
            replies_by_comment.setdefault(reply.comment_id, []).append(out)

    outs = []
    for comment in comments:
        out = _build_comment_out(comment, users_map, like_users_map, topic)
        out.replies = replies_by_comment.get(comment.comment_id, [])
        outs.append(out)
    return ApiResponse.ok(outs, msg="查询成功")


@topic_router.post(
    "/comments/{topic_id}",
    response_model=ApiResponse[CommentOut],
    summary="发布评论",
    description="登录用户对指定帖子发表评论，自动生成四位数随机唯一评论编号 comment_id。",
)
def create_topic_comment(
    payload: CommentCreate,
    topic_id: int = Path(..., ge=1, description="帖子编号 topic_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CommentOut]:
    """发表评论。"""
    topic = crud_topic.get_topic_by_topic_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")

    content = payload.content.strip()
    if not content:
        raise BadRequestException("评论内容不能为空")

    comment = crud_comment.create_comment(
        db,
        comment_id=_generate_comment_id(db),
        topic_id=topic.topic_id,
        uid=current_user.uid,
        content=content,
    )
    logger.info("用户发表评论 | uid=%s topic_id=%s comment_id=%s",
                current_user.uid, topic.topic_id, comment.comment_id)
    return ApiResponse.ok(
        _build_comment_out(comment, {current_user.uid: current_user}, {}, topic),
        msg="评论成功",
    )


@topic_router.post(
    "/reply/{comment_id}",
    response_model=ApiResponse[ReplyOut],
    summary="发布回复",
    description="登录用户对指定评论发表回复（comment_id 为四位数评论编号），"
                "自动生成四位数随机唯一回复编号 reply_id，回复外链到帖子编号与评论编号；不支持回复的回复。",
)
def create_comment_reply(
    payload: ReplyCreate,
    comment_id: int = Path(..., ge=1000, le=9999, description="评论唯一编号 comment_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReplyOut]:
    """对评论发表回复。"""
    comment = crud_comment.get_comment_by_comment_id(db, comment_id)
    if comment is None:
        raise NotFoundException("评论不存在")

    content = payload.content.strip()
    if not content:
        raise BadRequestException("回复内容不能为空")

    reply_to_id = payload.reply_to_id
    if reply_to_id is not None:
        target = crud_comment.get_reply_by_reply_id(db, reply_to_id)
        if target is None or target.comment_id != comment.comment_id:
            raise BadRequestException("被回复的回复不存在")

    reply = crud_comment.create_reply(
        db,
        reply_id=_generate_reply_id(db),
        topic_id=comment.topic_id,
        comment_id=comment.comment_id,
        uid=current_user.uid,
        content=content,
        reply_to_id=reply_to_id,
    )
    logger.info("用户回复评论 | uid=%s topic_id=%s comment_id=%s reply_id=%s",
                current_user.uid, comment.topic_id, comment.comment_id, reply.reply_id)
    return ApiResponse.ok(
        _build_reply_out(reply, {current_user.uid: current_user}),
        msg="回复成功",
    )


@topic_router.post(
    "/commentLike/{comment_id}",
    response_model=ApiResponse[int],
    summary="点赞评论",
    description="登录用户点赞评论（comment_id 为四位数评论编号，每个用户对同一评论只能点赞一次），"
                "返回点赞后的最新点赞数量。",
)
def like_comment(
    comment_id: int = Path(..., ge=1000, le=9999, description="评论唯一编号 comment_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[int]:
    """点赞评论。"""
    comment = crud_comment.get_comment_by_comment_id(db, comment_id)
    if comment is None:
        raise NotFoundException("评论不存在")
    if current_user.uid in {
        user.uid for user in crud_comment.list_like_users(db, [comment.id]).get(comment.id, [])
    }:
        raise BadRequestException("您已点赞该评论")

    crud_comment.like_comment(db, comment_row_id=comment.id, uid=current_user.uid)
    logger.info("用户点赞评论 | uid=%s comment_id=%s", current_user.uid, comment_id)
    likes = len(crud_comment.list_like_users(db, [comment.id]).get(comment.id, []))
    return ApiResponse.ok(likes, msg="点赞成功")


@topic_router.post(
    "/commentUnlike/{comment_id}",
    response_model=ApiResponse[int],
    summary="取消点赞评论",
    description="登录用户取消点赞评论（comment_id 为四位数评论编号，未点赞时返回错误），"
                "返回取消后的最新点赞数量。",
)
def unlike_comment(
    comment_id: int = Path(..., ge=1000, le=9999, description="评论唯一编号 comment_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[int]:
    """取消点赞评论。"""
    comment = crud_comment.get_comment_by_comment_id(db, comment_id)
    if comment is None:
        raise NotFoundException("评论不存在")
    if not crud_comment.unlike_comment(db, comment_row_id=comment.id, uid=current_user.uid):
        raise BadRequestException("您未点赞该评论")

    logger.info("用户取消点赞评论 | uid=%s comment_id=%s", current_user.uid, comment_id)
    likes = len(crud_comment.list_like_users(db, [comment.id]).get(comment.id, []))
    return ApiResponse.ok(likes, msg="取消点赞成功")


@topic_router.get(
    "/commentsBy/{uid}",
    response_model=ApiResponse[PageResult[CommentOut]],
    summary="查询用户发布的评论（含回复）",
    description="登录用户查询指定用户发布的评论（含回复），返回评论列表。",
)
def list_comments_by_uid(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    uid: str = Path(..., description="用户唯一编号 uid"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResult[CommentOut]]:
    """查询用户发布的评论（含回复）。"""
    offset = (page - 1) * pageSize
    comments = crud_comment.list_comments_by_uid(db, uid, offset, pageSize)
    for comment in comments:
        comment.topicTitle = crud_topic.get_topic_title(db, comment.topic_id)
    total = crud_comment.count_comments(db, uid=uid)
    return ApiResponse.ok(PageResult.create(comments, total, page, pageSize=pageSize))
    
@topic_router.get(
    "/favoriteTopic/{uid}",
    response_model=ApiResponse[PageResult[TopicOut]],
    summary="查询用户收藏的帖子",
    description="登录用户查询指定用户收藏的帖子，返回帖子对象。",
)

def list_favorite_topics_by_uid(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    uid: str = Path(..., description="用户唯一编号 uid"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResult[TopicOut]]:
    """查询用户收藏的帖子。"""
    offset = (page - 1) * pageSize
    topics = crud_topic.list_favorite_topics_by_uid(db, uid, offset, pageSize)
    total = crud_topic.count_favorite_topics_by_uid(db, uid=uid)
    return ApiResponse.ok(PageResult.create(topics, total, page, pageSize=pageSize))