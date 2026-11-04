"""
文件名：app/schemas/__init__.py
作用：集中导出 schema，方便 api 层统一 import。
"""

from app.schemas.common import ApiResponse, PageParams, PageResult
from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate
from app.schemas.forum import ForumCreate, ForumOut, ForumUpdate

from app.schemas.user import (
    RefreshTokenOut,
    RefreshTokenRequest,
    TokenOut,
    UserLogin,
    UserOut,
    UserPublicOut,
    UserRegister,
    UserUpdate,
)

__all__ = [
    "ApiResponse",
    "PageParams",
    "PageResult",
    "UserRegister",
    "UserLogin",
    "RefreshTokenRequest",
    "UserUpdate",
    "UserOut",
    "UserPublicOut",
    "TokenOut",
    "RefreshTokenOut",
    "TopicCreate",
    "TopicUpdate",
    "TopicOut",
    "ForumCreate",
    "ForumOut",
    "ForumUpdate",
]