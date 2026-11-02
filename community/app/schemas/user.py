"""
文件名：app/schemas/user.py
作用：用户相关请求校验与返回序列化 schema，与 ORM 模型解耦。
说明：所有返回 schema 均不包含 password_hash，杜绝密码泄露。
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


# ==================== 请求 schema ====================
class UserRegister(BaseModel):
    """注册请求。"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"username": "tom", "email": "tom@example.com", "password": "123456"}
        }
    )

    username: str = Field(..., min_length=3, max_length=50, description="用户名，唯一，仅字母数字下划线")
    email: EmailStr = Field(..., max_length=100, description="邮箱，唯一")
    password: str = Field(..., min_length=6, max_length=72, description="明文密码，6-72 位")

    @field_validator("username")
    @classmethod
    def check_username(cls, value: str) -> str:
        value = value.strip()
        if not USERNAME_PATTERN.match(value):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserLogin(BaseModel):
    """登录请求：用户名或邮箱二选一 + 密码。"""

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "tom@example.com", "password": "123456"}}
    )

    username: Optional[str] = Field(None, max_length=50, description="用户名（与 email 二选一）")
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱（与 username 二选一）")
    password: str = Field(..., min_length=6, max_length=72, description="明文密码")

    @model_validator(mode="after")
    def check_account(self) -> "UserLogin":
        if not self.username and not self.email:
            raise ValueError("username 与 email 至少填写一个")
        if self.username:
            self.username = self.username.strip()
        if self.email:
            self.email = str(self.email).strip().lower()
        return self


class RefreshTokenRequest(BaseModel):
    """刷新 token 请求。"""

    refresh_token: str = Field(..., min_length=1, description="登录时下发的 refresh_token")


class UserUpdate(BaseModel):
    """修改个人资料请求：只允许改头像和个性签名，禁止改 username / email。"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"avatar": "https://cdn.example.com/a.png", "bio": "这个人很懒"}},
    )

    avatar: Optional[str] = Field(None, max_length=255, description="头像地址")
    bio: Optional[str] = Field(None, max_length=500, description="个性签名（对应数据库 signature 字段）")

    @field_validator("avatar", "bio")
    @classmethod
    def strip_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip()


# ==================== 返回 schema ====================
class UserOut(BaseModel):
    """当前登录用户完整信息（不含 password_hash）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uid: str
    username: str
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    status: int
    level: int
    points: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserPublicOut(BaseModel):
    """他人主页公开信息（不含邮箱、状态、登录时间等隐私字段）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uid: str
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    level: int
    points: int
    created_at: datetime


class TokenOut(BaseModel):
    """登录成功返回的 token 信息。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="access_token 有效秒数")


class RefreshTokenOut(BaseModel):
    """刷新 token 返回的 access_token 信息。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="access_token 有效秒数")