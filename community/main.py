"""
文件名：main.py
作用：项目入口，初始化日志、注册 CORS、全局异常处理器与路由。
"""

import logging
import sys
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.exceptions import register_exception_handlers
from config import settings

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """初始化日志：控制台 + 按大小滚动的文件日志（logs/app.log）。"""
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # 避免 uvicorn reload 场景下重复添加 handler
    if not any(getattr(h, "_community_handler", False) for h in root_logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler._community_handler = True  # type: ignore[attr-defined]

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler._community_handler = True  # type: ignore[attr-defined]

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)


setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期：启动 / 关闭时记录日志。"""
    logger.info("服务启动 | env=%s debug=%s", settings.APP_ENV, settings.DEBUG)
    yield
    logger.info("服务关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="社区论坛 - 用户 / 帖子 / 圈子模块后端（注册 / 登录 / 刷新 token / 退出登录 / 个人资料 / 帖子增删改查 / 圈子增删改查 / 圈子分类增删改查 / 图片上传）",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS：allow_origins 为 "*" 时浏览器不允许携带凭证，因此按配置自动切换
allow_credentials = settings.cors_origins_list != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器：统一返回 {"code", "msg", "data"}
register_exception_handlers(app)

# 业务路由统一挂载在 /api 前缀下
app.include_router(api_router, prefix="/api")

# 上传图片静态目录：uploads 下文件通过 /uploads/xxx 直接访问
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.UPLOAD_URL_PREFIX, StaticFiles(directory=upload_dir), name="uploads")


@app.get("/health", tags=["系统"], summary="健康检查")
def health_check() -> dict:
    """服务存活探针。"""
    return {"code": 200, "msg": "success", "data": {"status": "ok", "env": settings.APP_ENV}}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )