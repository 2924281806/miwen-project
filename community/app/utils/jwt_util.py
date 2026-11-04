"""
文件名：app/utils/jwt_util.py
作用：JWT 签发、解析工具与已注销 token 黑名单，只处理 token 本身，不涉及权限判断。
"""

import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt

from config import settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

_revoked_tokens: Dict[str, float] = {}
_revoked_lock = threading.Lock()


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """签发 token：sub 存放用户 ID，type 区分 access / refresh，jti 为 token 唯一标识。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(uid: int) -> str:
    """签发 access_token。"""
    return _create_token(
        subject=str(uid),
        token_type=TOKEN_TYPE_ACCESS,
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
    )


def create_refresh_token(uid: int) -> str:
    """签发 refresh_token。"""
    return _create_token(
        subject=str(uid),
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
    """access_token 有效期（天），用于返回给前端。"""
    return settings.ACCESS_TOKEN_EXPIRE_DAYS


def _purge_expired_revoked(now: float) -> None:
    """清理已自然过期的黑名单记录，避免内存无限增长（调用方需持有锁）。"""
    for jti in [key for key, deadline in _revoked_tokens.items() if deadline <= now]:
        _revoked_tokens.pop(jti, None)


def revoke_token(payload: Dict[str, Any]) -> None:
    """
    把 token 记入黑名单，直到该 token 自身过期为止。
    说明：JWT 无状态，服务端无法真正删除客户端持有的 token，只能记录其 jti 使其失效。
    """
    jti = payload.get("jti")
    if not jti:
        return
    now = datetime.now(timezone.utc).timestamp()
    fallback = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()
    deadline = float(payload.get("exp") or fallback)
    with _revoked_lock:
        _purge_expired_revoked(now)
        _revoked_tokens[jti] = deadline


def is_token_revoked(payload: Dict[str, Any]) -> bool:
    """判断 token 是否已注销；不含 jti 的历史 token 视为未注销，靠自然过期失效。"""
    jti = payload.get("jti")
    if not jti:
        return False
    now = datetime.now(timezone.utc).timestamp()
    with _revoked_lock:
        _purge_expired_revoked(now)
        return jti in _revoked_tokens