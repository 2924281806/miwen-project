"""
文件名：app/schemas/comment.py
作用：帖子评论相关的 Pydantic 模型（请求入参 / 响应出参），只做数据校验与序列化，不包含业务逻辑。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CommentAuthorOut(BaseModel):
    """评论作者 / 回复作者 / 点赞用户的公开信息。"""

    uid: str = Field(..., description="用户uid")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")


class CommentCreate(BaseModel):
    """发布评论的请求体。"""

    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")


class ReplyCreate(BaseModel):
    """发布回复的请求体。"""

    content: str = Field(..., min_length=1, max_length=2000, description="回复内容")
    reply_to_id: Optional[int] = Field(
        None, ge=1000, le=9999, description="被回复的回复编号（toComment），回复其他回复时传，直接回复评论不传"
    )


class ReplyToCommentOut(BaseModel):
    """被回复的回复摘要（toComment）。"""

    reply_id: int = Field(..., description="被回复的回复编号")
    content: str = Field(..., description="被回复的回复内容")
    author: Optional[CommentAuthorOut] = Field(None, description="被回复的回复用户信息")


class ReplyOut(BaseModel):
    """回复出参：外链到帖子编号与评论编号；回复其他回复时带 toComment，并把下级回复挂在 children 中。"""

    reply_id: int = Field(..., description="回复唯一编号（四位数随机生成）")
    topic_id: int = Field(..., description="帖子唯一编号")
    comment_id: int = Field(..., description="所属评论唯一编号")
    content: str = Field(..., description="回复内容")
    uid: str = Field(..., description="回复用户uid")
    created_at: datetime = Field(..., description="回复时间")
    author: Optional[CommentAuthorOut] = Field(None, description="回复用户信息")
    reply_to_id: Optional[int] = Field(None, description="被回复的回复编号，直接回复评论为空")
    to_comment: Optional[ReplyToCommentOut] = Field(
        None, description="被回复的回复摘要（toComment），回复其他回复时返回"
    )
    children: List["ReplyOut"] = Field(default_factory=list, description="该回复下的下级回复列表")


class CommentOut(BaseModel):
    """评论出参：包含评论编号、作者、点赞数量、点赞用户信息列表与回复信息。"""

    comment_id: int = Field(..., description="评论唯一编号（四位数随机生成）")
    topic_id: int = Field(..., description="帖子唯一编号")
    content: str = Field(..., description="评论内容")
    uid: str = Field(..., description="评论用户uid")
    created_at: datetime = Field(..., description="评论时间")
    likes: int = Field(0, description="点赞数量")
    author: Optional[CommentAuthorOut] = Field(None, description="评论用户信息")
    liked_users: List[CommentAuthorOut] = Field(default_factory=list, description="点赞用户信息列表")
    replies: List[ReplyOut] = Field(default_factory=list, description="回复信息列表")
    topicTitle: str = Field(..., description="帖子标题")

ReplyOut.model_rebuild()
