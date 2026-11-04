"""
文件名：app/models/__init__.py
作用：集中导出所有 ORM 模型，便于 alembic 自动生成迁移时一次性加载全部表。
"""

from app.models.topics import Topic  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.forum import Forum  # noqa: F401


__all__ = ["User", "Topic", "Forum"]