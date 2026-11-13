"""
文件名：app/api/auth.py
作用：认证与用户接口（路由、参数校验、权限判断、调用 crud）。
说明：业务判断只允许出现在这一层，crud 层保持纯数据库操作。
"""

import logging
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.database import get_db
from app.dependencies import bearer_scheme, get_current_user, get_user_by_refresh_token
from app.exceptions import AppException, BadRequestException, ForbiddenException, NotFoundException
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    LogoutRequest,
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
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_access_token_expire_seconds,
    revoke_token,
)
from app.utils.password_util import get_password_hash, verify_password

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["认证"])
user_router = APIRouter(prefix="/user", tags=["用户"])


def _generate_uid(db: Session) -> str:
    """生成对外暴露的用户唯一标识（4位数开始，依次递增），极小概率重复时重试。"""
    for _ in range(5):
        uid = secrets.randbelow(90_00) + 10_00
        if crud_user.get_user_by_uid(db, uid, include_deleted=True) is None:
            return uid
    raise AppException("用户标识生成失败，请稍后重试", code=500)
        


# ==================== 认证相关（游客可访问）====================
@auth_router.post(
    "/register",
    response_model=ApiResponse[UserOut],
    summary="用户注册",
    description="用户名、邮箱唯一校验，密码以 bcrypt 哈希入库，自动生成用户唯一标识 uid，返回用户公开信息（不含 password_hash）。",
)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> ApiResponse[UserOut]:
    """注册新用户。"""
    if crud_user.get_user_by_username(db, payload.username):
        raise BadRequestException("用户名已存在")
    if crud_user.get_user_by_email(db, payload.email):
        raise BadRequestException("邮箱已被注册")

    user = crud_user.create_user(
        db,
        uid=_generate_uid(db),
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        nickname=payload.username,
        avatar=payload.avatar,
    )
    logger.info("用户注册成功 | id=%s uid=%s username=%s", user.uid, user.uid, user.username)
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
    logger.info("用户登录成功 | uid=%s username=%s", user.uid, user.username)

    return ApiResponse.ok(
        TokenOut(
            access_token=create_access_token(user.uid),
            refresh_token=create_refresh_token(user.uid),
            token_type="bearer",
            expires_in=get_access_token_expire_seconds(),
        ),
        msg="登录成功",
    )


@auth_router.post(
    "/refreshToken",
    response_model=ApiResponse[RefreshTokenOut],
    summary="刷新 access_token",
    description="使用登录时下发的 refresh_token 换取新的 access_token。",
)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> ApiResponse[RefreshTokenOut]:
    """刷新 access_token。"""
    user = get_user_by_refresh_token(db, payload.refresh_token)
    logger.info("刷新 token | uid=%s", user.uid)
    return ApiResponse.ok(
        RefreshTokenOut(
            access_token=create_access_token(user.uid),
            token_type="bearer",
            expires_in=get_access_token_expire_seconds(),
        ),
        msg="刷新成功",
    )


@auth_router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="退出登录",
    description="注销当前 access_token，token 立即失效；请求体可选携带 refresh_token，传入则一并注销。",
)
def logout(
    payload: Optional[LogoutRequest] = None,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """退出登录：把当前 access_token（及可选 refresh_token）记入黑名单。"""
    revoke_token(decode_token(credentials.credentials))

    if payload and payload.refresh_token:
        try:
            refresh_payload = decode_token(payload.refresh_token)
        except JWTError:
            refresh_payload = None
        if (
            refresh_payload
            and refresh_payload.get("type") == TOKEN_TYPE_REFRESH
            and refresh_payload.get("sub") == str(current_user.uid)
        ):
            revoke_token(refresh_payload)

    logger.info("用户退出登录 | uid=%s", current_user.uid)
    return ApiResponse.ok(None, msg="退出成功")


# ==================== 用户相关 ====================
# 注意：/user/me 必须声明在 /user/{uid} 之前，否则会被路径参数路由抢先匹配
@user_router.get(
    "/me",
    response_model=ApiResponse[UserOut],
    summary="获取当前登录用户信息",
)
def read_me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserOut]:
    """获取自己的完整信息。"""
    return ApiResponse.ok(UserOut.model_validate(current_user))


@user_router.post(
    "/updateUser",
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
    logger.info("用户修改资料 | uid=%s fields=%s", user.uid, list(update_data.keys()))
    return ApiResponse.ok(UserOut.model_validate(user), msg="资料更新成功")

@user_router.get(
    "/{uid}",
    response_model=ApiResponse[UserPublicOut],
    summary="查看他人主页信息",
    description="登录用户可查看其他用户的公开信息（不含邮箱、状态等隐私字段），"
                "并按当前登录用户计算 is_follow：已关注返回 1，未关注返回 0。",
)
def read_user(
    uid: int = Path(..., ge=1, description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserPublicOut]:
    """查看他人主页。"""
    user = crud_user.get_user_by_id(db, uid=uid)
    if user is None:
        raise NotFoundException("用户不存在")
    data = UserPublicOut.model_validate(user)
    data.is_follow = (
        1 if crud_user.is_following(db, follower_uid=current_user.uid, following_uid=user.uid) else 0
    )
    return ApiResponse.ok(data)


@user_router.post(
    "/follow/{uid}",
    response_model=ApiResponse[None],
    summary="关注用户",
    description="当前登录用户关注指定用户，重复关注返回错误。",
)
def follow_user(
    uid: int = Path(..., ge=1, description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """关注其他用户。"""
    if int(uid) == int(current_user.uid):
        raise BadRequestException("不能关注自己")
    target = crud_user.get_user_by_id(db, uid=uid)
    if target is None:
        raise NotFoundException("用户不存在")
    print(current_user.uid, target.uid)
    if crud_user.is_following(db, follower_uid=current_user.uid, following_uid=target.uid):
        raise BadRequestException("已关注该用户")

    crud_user.follow_user(db, follower_uid=current_user.uid, following_uid=target.uid)
    logger.info("用户关注 | follower_id=%s following_id=%s", current_user.uid, uid)
    return ApiResponse.ok(None, msg="关注成功")


@user_router.post(
    "/unfollow/{uid}",
    response_model=ApiResponse[None],
    summary="取消关注用户",
    description="当前登录用户取消关注指定用户，未关注时返回错误。",
)
def unfollow_user(
    uid: int = Path(..., ge=1, description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """取消关注其他用户。"""
    target = crud_user.get_user_by_id(db, uid=uid)
    if target is None:
        raise NotFoundException("用户不存在")
    if not crud_user.unfollow_user(db, follower_uid=current_user.uid, following_uid=target.uid):
        raise BadRequestException("尚未关注该用户")

    logger.info("用户取消关注 | follower_id=%s following_id=%s", current_user.uid, uid)
    return ApiResponse.ok(None, msg="取消关注成功")