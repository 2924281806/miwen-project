"""
文件名：app/exceptions.py
作用：自定义业务异常 + 全局异常处理器。
说明：所有异常最终统一转换为 {"code": int, "msg": str, "data": any} 格式返回。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    """业务异常基类。"""

    code: int = 400
    msg: str = "请求失败"

    def __init__(self, msg: str | None = None, code: int | None = None, data: object = None):
        self.code = code or self.code
        self.msg = msg or self.msg
        self.data = data
        super().__init__(self.msg)


class BadRequestException(AppException):
    """参数错误 / 业务校验失败（如用户名已存在），code=400。"""

    code = 400
    msg = "参数错误"


class UnauthorizedException(AppException):
    """未登录 / token 无效或过期，code=401。"""

    code = 401
    msg = "未登录或登录已失效"


class ForbiddenException(AppException):
    """权限不足 / 账号被禁用，code=403。"""

    code = 403
    msg = "权限不足"


class NotFoundException(AppException):
    """数据不存在，code=404。"""

    code = 404
    msg = "数据不存在"


def _json(code: int, msg: str, data: object = None) -> JSONResponse:
    """按统一格式构造响应体。"""
    return JSONResponse(status_code=code, content={"code": code, "msg": msg, "data": data})


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """业务异常处理：直接按异常自带 code/msg 返回。"""
    logger.warning("业务异常 | %s %s | code=%s msg=%s", request.method, request.url.path, exc.code, exc.msg)
    return _json(exc.code, exc.msg, exc.data)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Pydantic 参数校验失败，统一转成 400 + 可读提示。"""
    errors = exc.errors()
    details = []
    for err in errors:
        # loc 形如 ("body", "password")，去掉第一段来源标识
        field = ".".join(str(item) for item in err.get("loc", []) if item != "body")
        details.append(f"{field}: {err.get('msg', '参数不合法')}" if field else str(err.get("msg", "参数不合法")))
    msg = "; ".join(details) or "参数错误"
    logger.warning("参数校验失败 | %s %s | %s", request.method, request.url.path, msg)
    return _json(400, msg)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """兼容框架/第三方抛出的 HTTPException。"""
    logger.warning("HTTP异常 | %s %s | status=%s detail=%s", request.method, request.url.path, exc.status_code, exc.detail)
    return _json(exc.status_code, str(exc.detail))


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """数据库异常：记录堆栈，对外只返回通用提示，避免泄露表结构。"""
    logger.exception("数据库异常 | %s %s | %s", request.method, request.url.path, exc)
    return _json(500, "数据库操作失败，请稍后重试")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底异常：任何未捕获异常都返回 500，并记录完整堆栈。"""
    logger.exception("未捕获异常 | %s %s | %s", request.method, request.url.path, exc)
    return _json(500, "服务器内部错误")


def register_exception_handlers(app: FastAPI) -> None:
    """在 main.py 中统一注册所有异常处理器。"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)