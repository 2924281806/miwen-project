"""
文件名：app/api/forum_category.py
作用：版块分类接口（列表 / 新增 / 修改 / 删除），负责路由、参数校验、业务判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.crud import crud_forum, crud_forum_category
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import BadRequestException, NotFoundException
from app.models.forum_category import ForumCategory
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.forum_category import (
    ForumCategoryCreate,
    ForumCategoryOut,
    ForumCategoryUpdate,
)

logger = logging.getLogger(__name__)

forum_category_router = APIRouter(prefix="/forumCategory", tags=["板块分类"])


def _get_category(db: Session, category_id: int) -> ForumCategory:
    """按 ID 取出未删除的分类，不存在则抛 404。"""
    category = crud_forum_category.get_category_by_id(db, category_id)
    if category is None:
        raise NotFoundException("分类不存在")
    return category


def _ensure_name_available(db: Session, name: str, exclude_id: int | None = None) -> None:
    """校验分类名称未被占用（含已软删除的分类，避免与唯一索引 uk_name 冲突）。"""
    exists = crud_forum_category.get_category_by_name(
        db, name, include_deleted=True, exclude_id=exclude_id
    )
    if exists is not None:
        raise BadRequestException("分类名称已存在")


@forum_category_router.get(
    "/allCategoryList",
    response_model=ApiResponse[List[ForumCategoryOut]],
    summary="查询所有板块分类",
    description="返回全部未删除分类，按创建时间倒序，无任何入参，供版块分类下拉选择等场景使用。",
)
def get_all_category_list(
    db: Session = Depends(get_db),
) -> ApiResponse[List[ForumCategoryOut]]:
    """查询所有板块分类（游客可访问）。"""
    categories = crud_forum_category.list_categories(db)
    data = [ForumCategoryOut.model_validate(item) for item in categories]
    return ApiResponse.ok(data, msg="查询成功")


@forum_category_router.post(
    "/create",
    response_model=ApiResponse[ForumCategoryOut],
    summary="新增板块分类",
    description="登录用户新增分类，分类ID 由数据库自增生成；分类名称不可重复。",
)
def create_category(
    payload: ForumCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ForumCategoryOut]:
    """新增分类。"""
    _ensure_name_available(db, payload.name)
    category = crud_forum_category.create_category(db, name=payload.name)
    logger.info("用户新增分类 | uid=%s category_id=%s name=%s", current_user.id, category.id, category.name)
    return ApiResponse.ok(ForumCategoryOut.model_validate(category), msg="创建成功")


@forum_category_router.post(
    "/update/{id}",
    response_model=ApiResponse[ForumCategoryOut],
    summary="修改板块分类",
    description="登录用户修改分类名称；改名后同步该分类下所有板块的 category_name 冗余字段。",
)
def update_category(
    payload: ForumCategoryUpdate,
    id: int = Path(..., ge=1, description="分类ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ForumCategoryOut]:
    """修改分类。"""
    category = _get_category(db, id)
    _ensure_name_available(db, payload.name, exclude_id=id)
    category = crud_forum_category.update_category(db, category, {"name": payload.name})
    synced = crud_forum.update_category_name_by_category_id(db, category.id, category.name)
    logger.info(
        "用户修改分类 | uid=%s category_id=%s name=%s synced_forums=%s",
        current_user.id,
        category.id,
        category.name,
        synced,
    )
    return ApiResponse.ok(ForumCategoryOut.model_validate(category), msg="修改成功")


@forum_category_router.post(
    "/delete/{id}",
    response_model=ApiResponse[None],
    summary="删除板块分类",
    description="采用软删除（写入 deleted_at）；分类下仍有未删除板块时不允许删除。",
)
def delete_category(
    id: int = Path(..., ge=1, description="分类ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """删除分类。"""
    category = _get_category(db, id)
    forum_count = crud_forum.count_forums_by_category(db, category.id)
    if forum_count > 0:
        raise BadRequestException(f"该分类下还有 {forum_count} 个板块，请先移除后再删除分类")
    crud_forum_category.soft_delete_category(db, category)
    logger.info("用户删除分类 | uid=%s category_id=%s", current_user.id, category.id)
    return ApiResponse.ok(None, msg="删除成功")