"""
文件名：app/api/common.py
作用：公共接口，负责路由、参数校验、权限判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import crud_topic
from app.crud import crud_user
from app.database import get_db
from app.dependencies import get_optional_user
from app.models.topics import Topic
from app.models.user import User
from app.schemas.topics import TopicOut
from app.schemas.user import UserPublicOut
from app.schemas.common import ApiResponse, PageResult

common_router = APIRouter(prefix="/common", tags=["公共"])

@common_router.get(
    "/hot",
    response_model=ApiResponse[List[TopicOut]],
    summary="获取热门帖子",
    description="获取热门帖子（按点赞数倒序），默认只返回正常状态（status=1）的帖子，共 10 条。",
)
def get_hot_topics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ApiResponse[List[TopicOut]]:
    """获取热门帖子，默认返回 10 条，并附带当前用户的点赞 / 收藏状态。"""
    topics = crud_topic.get_hot_topics(db, limit=10)
    data = [TopicOut.model_validate(t) for t in topics]
    # 登录时批量填充当前用户的点赞 / 收藏状态（未登录恒为 0）
    if current_user is not None and data:
        flags = crud_topic.get_user_topic_flags(
            db, current_user.uid, [t.topic_id for t in topics]
        )
        for out in data:
            flag = flags[out.topic_id]
            out.is_votes = flag["is_votes"]
            out.is_favorites = flag["is_favorites"]
    return ApiResponse.ok(data)

@common_router.get(
    "/hot/images",
    response_model=ApiResponse[List[str]],
    summary="获取热门帖子的图片",
    description="获取热门帖子（按点赞数倒序），默认只返回正常状态（status=1）的帖子，共 10 条。",
)

def get_hot_topics_card(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ApiResponse[List[str]]:
    """获取热门帖子的图片，默认返回 5 条。"""
    topics = crud_topic.get_hot_topics(db, limit=5)
    hot_topics = [p.cover for p in topics if p.cover]
    return ApiResponse.ok(hot_topics)

@common_router.get(
    "/userList",
    response_model=ApiResponse[PageResult[UserPublicOut]],
    summary="获取所有用户列表",
    description="登录用户可查看所有用户的公开信息（不含邮箱、状态等隐私字段）。",
)

def read_user_list(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
) -> ApiResponse[PageResult[UserPublicOut]]:
    """获取所有用户列表。游客可访问，返回所有用户的公开信息。不包含邮箱、状态等隐私字段。"""
    users = crud_user.list_users(db, offset=(page - 1) * pageSize, limit=pageSize)
    data =  PageResult[UserPublicOut].create(
        lists=[UserPublicOut.model_validate(user) for user in users],
        total=crud_user.count_users(db),
        page=page,
        pageSize=pageSize,
    )
    return ApiResponse.ok(data, msg="查询成功")

