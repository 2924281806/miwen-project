"""
文件名：app/crud/crud_user.py
作用：用户表纯数据库操作（增删改查），不处理权限、token、业务规则判断。
说明：唯一性校验、密码比对、状态判断等业务逻辑一律放在 api 层。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, uid: int, include_deleted: bool = False) -> Optional[User]:
    """按主键查询用户，默认过滤软删除数据。"""
    stmt = select(User).where(User.id == uid)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_uid(db: Session, uid: str, include_deleted: bool = False) -> Optional[User]:
    """按用户唯一标识 uid 查询用户。"""
    stmt = select(User).where(User.uid == uid)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_last_uid(db: Session) -> int:
    """取当前 uid 的最大数值（无数据返回 0），用于生成下一个递增 uid。

    uid 是字符串数字，直接 MAX 会按字典序比较，因此先转数值再取最大值；
    统计包含软删除数据，避免已删除用户的 uid 被重复分配。
    """
    stmt = select(func.max(cast(User.uid, Integer)))
    value = db.execute(stmt).scalar_one_or_none()
    return int(value) if value is not None else 0


def get_user_by_username(db: Session, username: str, include_deleted: bool = False) -> Optional[User]:
    """按用户名查询用户。"""
    stmt = select(User).where(User.username == username)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email(db: Session, email: str, include_deleted: bool = False) -> Optional[User]:
    """按邮箱查询用户。"""
    stmt = select(User).where(User.email == email)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_account(db: Session, account: str, include_deleted: bool = False) -> Optional[User]:
    """按用户名或邮箱查询用户（登录场景使用）。"""
    stmt = select(User).where((User.username == account) | (User.email == account))
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def create_user(
    db: Session,
    *,
    uid: str,
    username: str,
    email: Optional[str],
    password_hash: str,
    nickname: Optional[str] = None,
    avatar: Optional[str] = None,
    signature: Optional[str] = None,
    status: int = 1,
) -> User:
    """新增用户并返回持久化后的实例。"""
    user = User(
        uid=uid,
        username=username,
        email=email,
        password_hash=password_hash,
        nickname=nickname,
        avatar=avatar,
        signature=signature,
        status=status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, update_data: dict) -> User:
    """按字段字典更新用户信息（只更新传入的字段）。"""
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user: User, login_at: Optional[datetime] = None) -> User:
    """更新最后登录时间。"""
    user.last_login_at = login_at or datetime.now()
    db.commit()
    db.refresh(user)
    return user


def count_users(db: Session, include_deleted: bool = False) -> int:
    """统计用户总数（分页预留）。"""
    stmt = select(func.count(User.id))
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one()


def list_users(db: Session, offset: int = 0, limit: int = 10, include_deleted: bool = False) -> List[User]:
    """分页查询用户列表（分页预留，按注册时间倒序）。"""
    stmt = select(User).order_by(User.id.desc()).offset(offset).limit(limit)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return list(db.execute(stmt).scalars().all())


def soft_delete_user(db: Session, user: User) -> User:
    """软删除用户（写入 deleted_at，不做物理删除）。"""
    user.deleted_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user