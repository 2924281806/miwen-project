"""
文件名：app/dependencies.py
作用：JWT 登录依赖与当前登录用户获取，供所有需要鉴权的接口复用。
"""

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.database import get_db
from app.exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.utils.jwt_util import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    decode_token,
    is_token_revoked,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="请求头携带：Authorization: Bearer <access_token>",
)


def _parse_payload(token: str, expected_type: str) -> dict:
    """解析 token 并校验类型，把 jose 异常转换为统一业务异常。"""
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise UnauthorizedException("登录状态已过期，请重新登录")
    except JWTError:
        raise UnauthorizedException("无效的 token")

    if payload.get("type") != expected_type:
        raise UnauthorizedException(f"token 类型错误，需要 {expected_type} token")
    if not payload.get("sub"):
        raise UnauthorizedException("token 缺少用户标识")
    if is_token_revoked(payload):
        raise UnauthorizedException("登录状态已失效，请重新登录")
    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    鉴权依赖：解析 Authorization 头中的 access_token，返回当前登录用户。
    任何需要登录的接口直接 Depends(get_current_user) 即可。
    """
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("未携带 token，请先登录")

    payload = _parse_payload(credentials.credentials, TOKEN_TYPE_ACCESS)
    try:
        uid = int(payload["sub"])
    except (TypeError, ValueError):
        raise UnauthorizedException("无效的 token")
    user = crud_user.get_user_by_id(db, uid)
    if user is None:
        raise UnauthorizedException("用户不存在或已注销")
    if user.status == 0:
        raise ForbiddenException("账号已被禁用")
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    可选鉴权依赖：未携带 token 返回 None（游客），携带了 token 则必须有效。
    适用于"游客可看、登录后有增强信息"的接口（如帖子列表的点赞 / 收藏状态）。
    """
    if credentials is None or not credentials.credentials:
        return None

    payload = _parse_payload(credentials.credentials, TOKEN_TYPE_ACCESS)
    try:
        uid = int(payload["sub"])
    except (TypeError, ValueError):
        raise UnauthorizedException("无效的 token")

    user = crud_user.get_user_by_id(db, uid)
    if user is None:
        raise UnauthorizedException("用户不存在或已注销")
    if user.status == 0:
        raise ForbiddenException("账号已被禁用")
    return user


def get_user_by_refresh_token(db: Session, refresh_token: str) -> User:
    """
    校验 refresh_token 并返回对应用户（供刷新接口复用，不依赖请求头）。
    """
    payload = _parse_payload(refresh_token, TOKEN_TYPE_REFRESH)
    try:
        uid = int(payload["sub"])
    except (TypeError, ValueError):
        raise UnauthorizedException("无效的 token")

    user = crud_user.get_user_by_id(db, uid)
    if user is None:
        raise UnauthorizedException("用户不存在或已注销")
    if user.status == 0:
        raise ForbiddenException("账号已被禁用")
    if user.status == 2:
        raise ForbiddenException("账号待激活")
    return user