"""
文件名：app/utils/password_util.py
作用：密码哈希与校验工具，基于 passlib + bcrypt。
说明：bcrypt 只接受 72 字节以内的密码，超出部分会被忽略，这里统一按字节截断。
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def _truncate(password: str) -> str:
    """按 UTF-8 字节截断到 72 字节，避免 bcrypt 超长报错或多字节被截半。"""
    raw = password.encode("utf-8")
    if len(raw) <= 72:
        return password
    return raw[:72].decode("utf-8", "ignore")


def get_password_hash(password: str) -> str:
    """明文密码 -> bcrypt 哈希。"""
    return pwd_context.hash(_truncate(password))


def verify_password(plain_password: str, password_hash: str) -> bool:
    """校验明文密码与数据库中的哈希是否匹配。"""
    if not plain_password or not password_hash:
        return False
    try:
        return pwd_context.verify(_truncate(plain_password), password_hash)
    except (ValueError, TypeError):
        # 哈希格式非法（如被篡改）时按校验失败处理，不抛出异常
        return False