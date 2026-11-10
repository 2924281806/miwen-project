"""
文件名：app/api/forum.py
作用：圈子接口（列表 / 创建 / 更新 / 删除），负责路由、参数校验、权限判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.crud import crud_forum, crud_forum_category
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import AppException, ForbiddenException, NotFoundException
from app.models.forum import Forum
from app.models.forum_category import ForumCategory
from app.models.user import User
from app.schemas.common import ApiResponse, PageResult
from app.schemas.forum import ForumCreate, ForumOut, ForumUpdate

logger = logging.getLogger(__name__)

forum_router = APIRouter(prefix="/forum", tags=["圈子"])

def _generate_forum_id(db: Session) -> int:
    """生成对外暴露的圈子唯一编号（5 位数字），极小概率重复时重试。"""
    for _ in range(5):
        forum_id = secrets.randbelow(90_000) + 10_000
        if crud_forum.get_forum_by_forum_id(db, forum_id, include_deleted=True) is None:
            return forum_id
    raise AppException("圈子编号生成失败，请稍后重试", code=500)


def _get_own_forum(db: Session, forum_id: int, current_user: User) -> Forum:
    """取出圈子并校验归属：只有作者本人可以修改或删除自己的圈子。"""
    forum = crud_forum.get_forum_by_id(db, forum_id)
    if forum is None:
        raise NotFoundException("圈子不存在")
    if forum.uid != current_user.uid:
        raise ForbiddenException("只能操作自己发布的圈子")
    return forum


def _resolve_category(db: Session, category_id: Optional[int]) -> ForumCategory:
    """解析圈子所属分类：指定了分类则校验存在，未指定则归入默认分类。"""
    if category_id is None:
        category = crud_forum_category.get_default_category(db)
        if category is None:
            raise NotFoundException("暂无可用分类，请先创建分类")
        return category
    category = crud_forum_category.get_category_by_id(db, category_id)
    if category is None:
        raise NotFoundException("分类不存在")
    return category


@forum_router.get(
    "/allForumList",
    response_model=ApiResponse[List[ForumOut]],
    summary="查询所有圈子",
    description="返回全部未删除圈子，按创建时间倒序，无任何入参，供下拉选择等场景使用。",
)
def get_all_forum_list(
    db: Session = Depends(get_db),
) -> ApiResponse[List[ForumOut]]:
    """查询所有圈子（游客可访问）。"""
    forums = crud_forum.all_list(db)
    data = [ForumOut.model_validate(item) for item in forums]
    return ApiResponse.ok(data, msg="查询成功")


@forum_router.get(
    "/list",
    response_model=ApiResponse[PageResult[ForumOut]],
    summary="查询圈子列表",
    description="分页查询圈子，按创建时间倒序；可按名称、作者、关键字、状态与所属分类筛选，默认不返回已删除圈子。",
)
def get_forum_list(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="圈子名称，模糊匹配"),
    uid: Optional[str] = Query(None, max_length=32, description="作者用户uid"),
    keyword: Optional[str] = Query(None, description="圈子名称或描述关键字"),
    status: Optional[int] = Query(None, ge=0, le=1, description="圈子状态：0关闭，1启用"),
    category_id: Optional[int] = Query(None, ge=1, description="所属分类ID，按分类筛选圈子"),
    include_deleted: Optional[bool] = Query(None, description="是否包含已删除圈子"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
) -> ApiResponse[PageResult[ForumOut]]:
    """分页查询圈子列表（游客可访问）。"""
    forums = crud_forum.list_forums(
        db,
        offset=(page - 1) * pageSize,
        limit=pageSize,
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        category_id=category_id,
        include_deleted=include_deleted,
    )
    total = crud_forum.count_forums(
        db,
        name=name,
        uid=uid,
        keyword=keyword,
        status=status,
        category_id=category_id,
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
    summary="创建圈子",
    description="登录用户创建圈子，作者自动取当前登录用户；join_type 表示加入方式（public 公开加入，private 需要申请），不传默认 public。",
)
def create_forum(
    payload: ForumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ForumOut]:
    """创建圈子。"""
    category = _resolve_category(db, payload.category_id)
    forum = crud_forum.create_forum(
        db,
        forum_id=_generate_forum_id(db),
        uid=current_user.uid,
        category_id=category.id,
        category_name=category.name,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
        join_type=payload.join_type,
    )
    logger.info(
        "用户创建圈子 | uid=%s forum_id=%s category_id=%s name=%s join_type=%s",
        current_user.id,
        forum.id,
        forum.category_id,
        forum.name,
        forum.join_type,
    )
    return ApiResponse.ok(ForumOut.model_validate(forum), msg="创建成功")


@forum_router.post(
    "/update/{forum_id}",
    response_model=ApiResponse[ForumOut],
    summary="修改圈子",
    description="仅作者本人可修改，可修改名称、描述、图标、所属分类与加入方式，未传字段保持不变。",
)
def update_forum(
    payload: ForumUpdate,
    forum_id: int = Path(..., ge=1, description="圈子ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ForumOut]:
    """修改圈子。"""
    forum = _get_own_forum(db, forum_id, current_user)
    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = _resolve_category(db, update_data["category_id"])
        update_data["category_id"] = category.id
        update_data["category_name"] = category.name
    forum = crud_forum.update_forum(db, forum, update_data)
    logger.info(
        "用户修改圈子 | uid=%s forum_id=%s fields=%s",
        current_user.id,
        forum.id,
        list(update_data.keys()),
    )
    return ApiResponse.ok(ForumOut.model_validate(forum), msg="修改成功")


@forum_router.post(
    "/delete/{forum_id}",
    response_model=ApiResponse[None],
    summary="删除圈子",
    description="仅作者本人可删除，采用软删除（写入 deleted_at），删除后不再出现在列表与查询结果中。",
)
def delete_forum(
    forum_id: int = Path(..., ge=1, description="圈子ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """删除自己发布的圈子。"""
    forum = _get_own_forum(db, forum_id, current_user)
    crud_forum.soft_delete_forum(db, forum)
    logger.info("用户删除圈子 | uid=%s forum_id=%s", current_user.id, forum.id)
    return ApiResponse.ok(None, msg="删除成功")