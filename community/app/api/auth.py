"""
文件名：app/api/auth.py
作用：认证与用户接口（路由、参数校验、权限判断、调用 crud）。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.database import get_db
from app.dependencies import get_current_user, get_user_by_refresh_token
from app.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.user import User
from app.schemas.common import ApiResponse
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
from app.utils.jwt_util import (
    create_access_token,
    create_refresh_token,
    get_access_token_expire_seconds,
)
from app.utils.password_util import get_password_hash, verify_password

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["认证"])
user_router = APIRouter(prefix="/user", tags=["用户"])


# ==================== 认证相关（游客可访问）====================
@auth_router.post(
    "/register",
    response_model=ApiResponse[UserOut],
    summary="用户注册",
    description="用户名、邮箱唯一校验，密码以 bcrypt 哈希入库，返回用户公开信息（不含 password_hash）。",
)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> ApiResponse[UserOut]:
    """注册新用户。"""
    if crud_user.get_user_by_username(db, payload.username):
        raise BadRequestException("用户名已存在")
    if crud_user.get_user_by_email(db, payload.email):
        raise BadRequestException("邮箱已被注册")

    user = crud_user.create_user(
        db,
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        nickname=payload.username,
    )
    logger.info("用户注册成功 | user_id=%s username=%s", user.id, user.username)
    return ApiResponse.ok(UserOut.model_validate(user), msg="注册成功")


@auth_router.post(
    "/login",
    response_model=ApiResponse[TokenOut],
    summary="用户登录",
    description="使用 username 或 email + 明文密码登录，成功返回 access_token 与 refresh_token。",
)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> ApiResponse[TokenOut]:
    """登录并下发双 token。"""
    account = payload.username or str(payload.email or "")
    user = crud_user.get_user_by_account(db, account)

    # 用户不存在与密码错误返回同一提示，避免账号枚举
    if user is None or not verify_password(payload.password, user.password_hash):
        raise BadRequestException("用户名/邮箱或密码错误")
    if user.status == 0:
        raise ForbiddenException("账号已被禁用")
    if user.status == 2:
        raise ForbiddenException("账号待激活")

    crud_user.update_last_login(db, user)
    logger.info("用户登录成功 | user_id=%s username=%s", user.id, user.username)

    return ApiResponse.ok(
        TokenOut(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            token_type="bearer",
            expires_in=get_access_token_expire_seconds(),
        ),
        msg="登录成功",
    )


@auth_router.post(
    "/refresh-token",
    response_model=ApiResponse[RefreshTokenOut],
    summary="刷新 access_token",
    description="使用登录时下发的 refresh_token 换取新的 access_token。",
)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> ApiResponse[RefreshTokenOut]:
    """刷新 access_token。"""
    user = get_user_by_refresh_token(db, payload.refresh_token)
    logger.info("刷新 token | user_id=%s", user.id)
    return ApiResponse.ok(
        RefreshTokenOut(
            access_token=create_access_token(user.id),
            token_type="bearer",
            expires_in=get_access_token_expire_seconds(),
        ),
        msg="刷新成功",
    )


# ==================== 用户相关 ====================
# 注意：/user/me 必须声明在 /user/{user_id} 之前，否则会被路径参数路由抢先匹配
@user_router.get(
    "/me",
    response_model=ApiResponse[UserOut],
    summary="获取当前登录用户信息",
)
def read_me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserOut]:
    """获取自己的完整信息。"""
    return ApiResponse.ok(UserOut.model_validate(current_user))


@user_router.put(
    "/me",
    response_model=ApiResponse[UserOut],
    summary="修改当前登录用户资料",
    description="仅允许修改 avatar（头像）与 bio（个性签名），username / email 不可修改。",
)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[UserOut]:
    """修改自己的个人资料。"""
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException("没有需要更新的字段")

    # 前端字段 bio 对应数据库字段 signature
    if "bio" in update_data:
        update_data["signature"] = update_data.pop("bio")

    user = crud_user.update_user(db, current_user, update_data)
    logger.info("用户修改资料 | user_id=%s fields=%s", user.id, list(update_data.keys()))
    return ApiResponse.ok(UserOut.model_validate(user), msg="资料更新成功")


@user_router.get(
    "/{user_id}",
    response_model=ApiResponse[UserPublicOut],
    summary="查看他人主页信息",
    description="登录用户可查看其他用户的公开信息（不含邮箱、状态等隐私字段）。",
)
def read_user(
    user_id: int = Path(..., ge=1, description="用户ID"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse[UserPublicOut]:
    """查看他人主页。"""
    user = crud_user.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundException("用户不存在")
    return ApiResponse.ok(UserPublicOut.model_validate(user))