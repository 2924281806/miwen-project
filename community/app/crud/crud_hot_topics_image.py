"""
文件名：app/crud/crud_hot_topics_image.py
作用：hot_topics_image 表纯数据库操作（增删改查），不处理业务规则判断。
说明：图片是否可删除、URL唯一性等业务规则一律放在 api 层。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.hot_topics_image import HotTopicsImage



def list_images(db: Session, include_deleted: bool = False) -> List[HotTopicsImage]:
    """查询图片列表：按创建时间倒序。"""
    stmt = select(HotTopicsImage)
    if not include_deleted:
        stmt = stmt.where(HotTopicsImage.deleted_at.is_(None))
    stmt = stmt.order_by(HotTopicsImage.created_at.desc())
    return list(db.execute(stmt).scalars().all())