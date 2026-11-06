"""
文件名：app/schemas/forum.py
作用：圈子相关请求校验与返回序列化 schema，与 ORM 模型解耦。
说明：status / created_at / updated_at / deleted_at 属于运营与审计字段，
      不接受调用方自行设置，因此只出现在返回 schema 中。
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

JOIN_TYPE_PUBLIC = "public"
JOIN_TYPE_PRIVATE = "private"
JoinType = Literal["public", "private"]


def _check_name(v: str) -> str:
    """校验圈子名称：非空、不含特殊字符、长度 1-200。"""
    if not v:
        raise ValueError("圈子名称不能为空")
    if any(char in v for char in "!@#$%^&*()_+{}|\":;<>,.?/"):
        raise ValueError("圈子名称不能包含特殊字符")
    if len(v) not in range(1, 201):
        raise ValueError("圈子名称长度必须在 1-200 字之间")
    return v


def _check_description(v: str) -> str:
    """校验圈子描述：非空、长度 1-255。"""
    if not v:
        raise ValueError("圈子描述不能为空")
    if len(v) not in range(1, 256):
        raise ValueError("圈子描述长度必须在 1-255 字之间")
    return v


def _check_icon(v: Optional[str]) -> Optional[str]:
    """校验圈子图标地址：可空，空字符串归一为 None。"""
    if v is None:
        return None
    v = v.strip()
    return v or None


class ForumCreate(BaseModel):
    """创建圈子请求。"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "FastAPI 圈子",
                "description": "一个关于 FastAPI 的圈子",
                "join_type": "public",
            }
        },
    )

    name: str = Field(..., min_length=1, max_length=200, description="圈子名称，1-200 字")
    description: str = Field(..., min_length=1, max_length=255, description="圈子描述，1-255 字")
    icon: Optional[str] = Field(None, max_length=255, description="圈子图标地址，可空")
    category_id: Optional[int] = Field(
        None, ge=1, description="所属分类ID，不传则归入默认分类；分类名称由服务端按分类表回填"
    )
    join_type: JoinType = Field(
        JOIN_TYPE_PUBLIC,
        validation_alias=AliasChoices("join_type", "joinType"),
        description="加入圈子方式：public 公开加入，private 需要申请；不传默认 public",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证圈子名称。"""
        return _check_name(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """验证圈子描述。"""
        return _check_description(v)

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """验证圈子图标地址。"""
        return _check_icon(v)


class ForumUpdate(BaseModel):
    """修改圈子请求，所有字段可选，只更新传入的字段。"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "修改后的圈子名称",
                "description": "修改后的圈子描述",
            }
        },
    )

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="圈子名称，1-200 字")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="圈子描述，1-255 字")
    icon: Optional[str] = Field(None, max_length=255, description="圈子图标地址，可空")
    category_id: Optional[int] = Field(
        None, ge=1, description="所属分类ID，修改后分类名称由服务端按分类表同步"
    )
    join_type: Optional[JoinType] = Field(
        None,
        validation_alias=AliasChoices("join_type", "joinType"),
        description="加入圈子方式：public 公开加入，private 需要申请；不传保持不变",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证圈子名称。"""
        return None if v is None else _check_name(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """验证圈子描述。"""
        return None if v is None else _check_description(v)

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """验证圈子图标地址。"""
        return _check_icon(v)


class ForumOut(BaseModel):
    """圈子响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="圈子 ID")
    forum_id: int = Field(..., description="圈子唯一编号，对外暴露的编号")
    uid: int = Field(..., description="圈子创建用户 ID")
    category_id: int = Field(..., description="所属分类 ID，对应 forum_category.id")
    category_name: str = Field(..., description="所属分类名称，对应 forum_category.name")
    name: str = Field(..., description="圈子名称")
    description: Optional[str] = Field(None, description="圈子描述")
    icon: Optional[str] = Field(None, description="圈子图标地址")
    status: int = Field(..., description="是否启用：0关闭，1启用")
    join_type: JoinType = Field(..., description="加入圈子方式：public 公开加入，private 需要申请")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")