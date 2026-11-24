"""
文件名：app/schemas/comment.py
作用：帖子评论相关的 Pydantic 模型（请求入参 / 响应出参），只做数据校验与序列化，不包含业务逻辑。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CommentAuthorOut(BaseModel):
    """评论作者 / 点赞用户的公开信息。"""

    uid: str = Field(..., description="用户uid")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")


class CommentCreate(BaseModel):
    """发布评论 / 回复的请求体。"""

    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    parent_id: Optional[int] = Field(None, ge=1, description="父评论ID，回复时传，顶级评论不传")


class CommentOut(BaseModel):
    """评论出参：包含作者、点赞数量、点赞用户信息列表与回复信息。"""

    id: int = Field(..., description="评论ID")
    content: str = Field(..., description="评论内容")
    uid: str = Field(..., description="评论用户uid")
    created_at: datetime = Field(..., description="评论时间")
    likes: int = Field(0, description="点赞数量")
    author: Optional[CommentAuthorOut] = Field(None, description="评论用户信息")
    liked_users: List[CommentAuthorOut] = Field(default_factory=list, description="点赞用户信息列表")
    replies: List["CommentOut"] = Field(default_factory=list, description="回复信息列表")


CommentOut.model_rebuild()
