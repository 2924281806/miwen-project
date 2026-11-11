"""
文件名：app/schemas/topics.py
作用：帖子相关请求校验与返回序列化 schema，与 ORM 模型解耦。
说明：is_top / is_essence / is_closed / status / views / reply_count 属于运营、审核与统计字段，
      不接受发帖人自行设置，因此只出现在返回 schema 中。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================== 请求 schema ====================
class TopicCreate(BaseModel):
    """发帖请求。"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "forum_id": 1,
                "title": "如何优雅地使用 FastAPI",
                "content": "FastAPI 是一个高性能的 Python Web 框架……",
                "cover": "https://cdn.example.com/c.png",
            }
        },
    )

    forum_id: int = Field(..., ge=1, description="所属圈子编号，对应 forum.forum_id")
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题，1-200 字")
    content: str = Field(..., min_length=1, max_length=10000, description="帖子内容，1-10000 字")
    cover: Optional[str] = Field(None, max_length=255, description="封面图地址，可空")

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("帖子标题不能为空")
        return value

    @field_validator("content")
    @classmethod
    def check_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("帖子内容不能为空")
        return value

    @field_validator("cover")
    @classmethod
    def normalize_cover(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


class TopicUpdate(BaseModel):
    """修改帖子请求：只允许改标题、内容与封面，圈子归属、置顶、加精等由运营后台维护。"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "title": "修改后的标题",
                "content": "修改后的内容",
                "cover": "https://cdn.example.com/c2.png",
            }
        },
    )

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="帖子标题，1-200 字")
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="帖子内容，1-10000 字")
    cover: Optional[str] = Field(None, max_length=255, description="封面图地址，传 null 表示清空封面")

    @field_validator("title")
    @classmethod
    def check_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("帖子标题不能为空")
        return value

    @field_validator("content")
    @classmethod
    def check_content(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not value.strip():
            raise ValueError("帖子内容不能为空")
        return value

    @field_validator("cover")
    @classmethod
    def normalize_cover(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


# ==================== 返回 schema ====================
class AuthorOut(BaseModel):
    """帖子作者信息（仅帖子详情接口返回）。"""

    uid: str = Field(..., description="作者 uid")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像地址")
    level: int = Field(0, description="用户等级")
    posts: int = Field(0, description="发帖数")
    fans: int = Field(0, description="粉丝数（关注功能上线前恒为 0）")


class TopicOut(BaseModel):
    """帖子完整信息（列表、发帖、改帖均复用）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="主题ID")
    topic_id: int = Field(..., description="帖子唯一编号，对外暴露的编号")
    forum_id: int = Field(..., description="所属圈子编号，对应 forum.forum_id")
    uid: str = Field(..., description="发帖用户 uid")
    title: str = Field(..., description="帖子标题")
    content: str = Field(..., description="帖子内容")
    cover: Optional[str] = Field(None, description="封面图")
    is_top: int = Field(..., description="是否置顶：0否1是")
    is_essence: int = Field(..., description="是否精华：0否1是")
    is_closed: int = Field(..., description="是否关闭回复：0否1是")
    views: int = Field(..., description="浏览量")
    reply_count: int = Field(..., description="回复数量")
    last_post_at: datetime = Field(..., description="最后回复时间")
    last_post_uid: Optional[int] = Field(None, description="最后回复人ID")
    status: int = Field(..., description="0待审核，1正常，2隐藏")
    created_at: datetime = Field(..., description="发帖时间")
    updated_at: datetime = Field(..., description="更新时间")
    favorites: int = Field(..., description="收藏数")
    votes: int = Field(..., description="点赞数")
    comments: int = Field(..., description="评论数")
    is_votes: int = Field(0, description="当前用户是否已点赞该帖子：0否1是（未登录恒为0）")
    is_favorites: int = Field(0, description="当前用户是否已收藏该帖子：0否1是（未登录恒为0）")
    author: Optional[AuthorOut] = Field(None, description="作者信息，仅帖子详情接口返回")
    