"""
文件名：app/api/hot_topics_image.py
作用：热门话题图片接口（列表 / 新增 / 修改 / 删除），负责路由、参数校验、业务判断并调用 crud。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.crud import crud_hot_topics_image
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import BadRequestException, NotFoundException
from app.models.hot_topics_image import HotTopicsImage
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.hot_topics_image import HotTopicsImageOut

logger = logging.getLogger(__name__)

hot_topics_image_router = APIRouter(prefix="/hotTopicsImage", tags=["热门话题图片"])


@hot_topics_image_router.get(
    "/hotImageList",
    response_model=ApiResponse[List[HotTopicsImageOut]],
    summary="查询所有热门话题图片",
    description="返回全部未删除图片，按创建时间倒序，无任何入参，供热门话题图片下拉选择等场景使用。",
)
def get_hot_image_list(
    db: Session = Depends(get_db),
) -> ApiResponse[List[HotTopicsImageOut]]:
    """查询所有热门话题图片（游客可访问）。"""
    images = crud_hot_topics_image.list_images(db)
    data = [HotTopicsImageOut.model_validate(item) for item in images]
    return ApiResponse.ok(data, msg="查询成功")
