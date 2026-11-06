"""
文件名：app/schemas/forum_category.py
作用：圈子分类请求校验与返回序列化 schema，与 ORM 模型解耦。
说明：分类ID 由数据库自增生成，创建时间与删除时间属于审计字段，均不接受调用方设置。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _check_name(v: str) -> str:
    """校验分类名称：去空格后非空、长度 1-100。"""
    v = (v or "").strip()
    if not v:
        raise ValueError("分类名称不能为空")
    if len(v) not in range(1, 101):
        raise ValueError("分类名称长度必须在 1-100 字之间")
    return v


class ForumCategoryCreate(BaseModel):
    """新增分类请求。"""

    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {"name": "技术交流"}})

    name: str = Field(..., min_length=1, max_length=100, description="分类名称，1-100 字，不可重名")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证分类名称。"""
        return _check_name(v)


class ForumCategoryUpdate(BaseModel):
    """修改分类请求。"""

    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {"name": "技术分享"}})

    name: str = Field(..., min_length=1, max_length=100, description="分类名称，1-100 字，不可重名")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证分类名称。"""
        return _check_name(v)


class ForumCategoryOut(BaseModel):
    """圈子分类响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="分类ID，自动生成的唯一编号")
    name: str = Field(..., description="分类名称")
    created_at: datetime = Field(..., description="创建时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间，未删除为 null")