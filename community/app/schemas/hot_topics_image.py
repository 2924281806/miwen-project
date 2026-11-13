"""
文件名：app/schemas/hot_topics_image.py
作用：热门话题图片请求校验与返回序列化 schema，与 ORM 模型解耦。
说明：热门话题图片ID 由数据库自增生成，创建时间与删除时间属于审计字段，均不接受调用方设置。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HotTopicsImageOut(BaseModel):
    """热门话题图片响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="图片ID，自动生成的唯一编号")
    img_url: str = Field(..., description="图片URL")
    created_at: datetime = Field(..., description="创建时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间，未删除为 null")