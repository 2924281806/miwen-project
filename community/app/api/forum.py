"""
文件名：app/api/forum.py
作用：版块接口（列表 / 创建 / 更新 / 删除），负责路由、参数校验、权限判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.crud import crud_forum
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import AppException, ForbiddenException, NotFoundException
from app.models.forum import Forum
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.schemas.forum import ForumCreate, ForumOut, ForumUpdate

logger = logging.getLogger(__name__)

forum_router = APIRouter(prefix="/forum", tags=["板块"])

def _generate_forum_id(db: Session) -> int:
    """生成对外暴露的板块唯一编号（5 位数字），极小概率重复时重试。"""
    for _ in range(5):
        forum_id = secrets.randbelow(90_000) + 10_000
        if crud_forum.get_forum_by_forum_id(db, forum_id, include_deleted=True) is None:
            return forum_id
    raise AppException("板块编号生成失败，请稍后重试", code=500)


def _get_own_forum(db: Session, forum_id: int, current_user: User) -> Forum:
    """取出板块并校验归属：只有作者本人可以修改或删除自己的板块。"""
    forum = crud_forum.get_forum_by_id(db, forum_id)
    if forum is None:
        raise NotFoundException("板块不存在")
    if forum.uid != current_user.id:
        raise ForbiddenException("只能操作自己发布的板块")
    return forum


@forum_router.get(
    "/list",
    response_model=ApiResponse[PageResult[ForumOut]],
    summary="查询板块列表",
    description="分页查询板块，按创建时间倒序；可按名称、作者、关键字与状态筛选，默认不返回已删除板块。",
)
def get_forum_list(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    name: Optional[str] = Query(None, description="板块名称，模糊匹配"),
    uid: Optional[int] = Query(None, ge=1, description="作者用户ID"),
    keyword: Optional[str] = Query(None, description="板块名称或描述关键字"),
    status: Optional[int] = Query(None, ge=0, le=1, description="板块状态：0关闭，1启用"),
    include_deleted: bool = Query(False, description="是否包含已删除板块"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
) -> ApiResponse[PageResult[ForumOut]]:
    """分页查询板块列表（需登录）。"""
    forums = crud_forum.list_forums(
        db,
        offset=(page - 1) * pageSize,
        limit=pageSize,
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        include_deleted=include_deleted,
    )
    total = crud_forum.count_forums(
        db,
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        include_deleted=include_deleted,
    )
    data = PageResult[ForumOut].create(
        items=[ForumOut.model_validate(item) for item in forums],
        total=total,
        page=page,
        pageSize=pageSize,
    )
    return ApiResponse.ok(data, msg="查询成功")


@forum_router.post(
    "/createForum",
    response_model=ApiResponse[ForumOut],
    summary="创建板块",
    description="登录用户创建板块，作者自动取当前登录用户。",
)
def create_forum(
    payload: ForumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ForumOut]:
    """创建板块。"""
    forum = crud_forum.create_forum(
        db,
        forumId=_generate_forum_id(db),
        userId=current_user.id,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
    )
    logger.info(
        "用户创建板块 | uid=%s forum_id=%s name=%s",
        current_user.id,
        forum.id,
        forum.name,
    )
    return ApiResponse.ok(ForumOut.model_validate(forum), msg="创建成功")


@forum_router.post(
    "/update/{forum_id}",
    response_model=ApiResponse[ForumOut],
    summary="修改板块",
    description="仅作者本人可修改，只允许修改名称、描述与图标，未传字段保持不变。",
)
def update_forum(
    payload: ForumUpdate,
    forum_id: int = Path(..., ge=1, description="板块ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ForumOut]:
    """修改板块。"""
    forum = _get_own_forum(db, forum_id, current_user)
    update_data = payload.model_dump(exclude_unset=True)
    forum = crud_forum.update_forum(db, forum, update_data)
    logger.info(
        "用户修改板块 | uid=%s forum_id=%s fields=%s",
        current_user.id,
        forum.id,
        list(update_data.keys()),
    )
    return ApiResponse.ok(ForumOut.model_validate(forum), msg="修改成功")


@forum_router.post(
    "/delete/{forum_id}",
    response_model=ApiResponse[None],
    summary="删除板块",
    description="仅作者本人可删除，采用软删除（写入 deleted_at），删除后不再出现在列表与查询结果中。",
)
def delete_forum(
    forum_id: int = Path(..., ge=1, description="板块ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """删除自己发布的板块。"""
    forum = _get_own_forum(db, forum_id, current_user)
    crud_forum.soft_delete_forum(db, forum)
    logger.info("用户删除板块 | uid=%s forum_id=%s", current_user.id, forum.id)
    return ApiResponse.ok(None, msg="删除成功")