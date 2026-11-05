"""
文件名：app/api/topics.py
作用：帖子接口（列表 / 发帖 / 改帖 / 删帖），负责路由、参数校验、权限判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.crud import crud_forum, crud_topic
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import AppException, BadRequestException, ForbiddenException, NotFoundException
from app.models.topics import Topic
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate

logger = logging.getLogger(__name__)

topic_router = APIRouter(prefix="/topic", tags=["帖子"])


def _generate_topic_id(db: Session) -> int:
    """生成对外暴露的帖子唯一编号（8 位数字），极小概率重复时重试。"""
    for _ in range(5):
        topic_id = secrets.randbelow(90_000_000) + 10_000_000
        if crud_topic.get_topic_by_topic_id(db, topic_id, include_deleted=True) is None:
            return topic_id
    raise AppException("帖子编号生成失败，请稍后重试", code=500)


def _get_own_topic(db: Session, topic_id: int, current_user: User) -> Topic:
    """取出帖子并校验归属：只有作者本人可以修改或删除自己的帖子。"""
    topic = crud_topic.get_topic_by_id(db, topic_id)
    if topic is None:
        raise NotFoundException("帖子不存在")
    if topic.uid != current_user.id:
        raise ForbiddenException("只能操作自己发布的帖子")
    return topic


@topic_router.get(
    "/list",
    response_model=ApiResponse[PageResult[TopicOut]],
    summary="获取帖子列表",
    description="分页查询帖子，置顶优先、其次按最后回复时间倒序；可按版块、作者、标题关键字与状态筛选，默认只返回正常状态（status=1）的帖子。",
)
def list_topics(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    forum_id: Optional[int] = Query(None, ge=1, description="按所属版块筛选"),
    uid: Optional[int] = Query(None, ge=1, description="按发帖用户筛选"),
    keyword: Optional[str] = Query(None, max_length=200, description="标题关键字，模糊匹配"),
    status: Optional[int] = Query(1, ge=0, le=2, description="状态：0待审核 1正常 2隐藏，不传表示全部"),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResult[TopicOut]]:
    """查询帖子列表（游客可访问）。"""
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
    items = [TopicOut.model_validate(topic) for topic in topics]
    return ApiResponse.ok(PageResult.create(items, total, page, pageSize=pageSize))


@topic_router.post(
    "/createPost",
    response_model=ApiResponse[TopicOut],
    summary="发布帖子",
    description="登录用户发帖，发帖人自动取自当前登录用户，并自动生成帖子唯一编号 topic_id；所属版块必须存在且处于启用状态；置顶、加精、关闭回复、浏览量等运营字段使用数据库默认值。",
)
def create_topic(
    payload: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[TopicOut]:
    """发布新帖子。"""
    forum = crud_forum.get_forum_by_forum_id(db, payload.forum_id)
    if forum is None:
        raise BadRequestException("版块不存在")
    if forum.status != 1:
        raise BadRequestException("版块已关闭，无法发帖")

    topic = crud_topic.create_topic(
        db,
        topic_id=_generate_topic_id(db),
        forum_id=payload.forum_id,
        uid=current_user.id,
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
    return ApiResponse.ok(TopicOut.model_validate(topic), msg="修改成功")


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