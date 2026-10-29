"""
文件名：app/utils/jwt_util.py
作用：JWT 签发与解析工具，只做 token 编解码，不涉及权限判断。
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt

from config import settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """签发 token：sub 存放用户 ID，type 区分 access / refresh。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int) -> str:
    """签发 access_token。"""
    return _create_token(
        subject=str(user_id),
        token_type=TOKEN_TYPE_ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    """签发 refresh_token。"""
    return _create_token(
        subject=str(user_id),
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    解析并校验 token（签名、过期时间）。
    校验失败会抛出 jose.JWTError / jose.ExpiredSignatureError，由 dependencies 层转换业务异常。
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_access_token_expire_seconds() -> int:
    """access_token 有效期（秒），用于返回给前端。"""
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60