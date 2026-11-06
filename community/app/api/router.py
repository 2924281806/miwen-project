"""
文件名：app/api/router.py
作用：汇总所有子路由，main.py 只需注册这一层。
"""

from fastapi import APIRouter

from app.api.auth import auth_router, user_router
from app.api.forum import forum_router
from app.api.forum_category import forum_category_router
from app.api.topics import topic_router
from app.api.upload import upload_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(topic_router)
api_router.include_router(forum_router)
api_router.include_router(forum_category_router)
api_router.include_router(upload_router)