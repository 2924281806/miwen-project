"""
文件名：app/schemas/common.py
作用：通用响应与分页 schema，供所有接口复用。
"""

from math import ceil
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """统一返回结构：{"code": int, "msg": str, "data": any}。"""

    model_config = ConfigDict(json_schema_extra={"example": {"code": 200, "msg": "success", "data": None}})

    code: int = Field(200, description="业务状态码：200成功 400参数错误 401未登录 403权限不足 404不存在 500服务异常")
    msg: str = Field("success", description="提示信息")
    data: Optional[DataT] = Field(None, description="业务数据")

    @classmethod
    def ok(cls, data: Optional[DataT] = None, msg: str = "success") -> "ApiResponse[DataT]":
        """成功响应快捷构造。"""
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def fail(cls, code: int, msg: str, data: Optional[DataT] = None) -> "ApiResponse[DataT]":
        """失败响应快捷构造（一般由全局异常处理器生成，这里预留）。"""
        return cls(code=code, msg=msg, data=data)


class PageParams(BaseModel):
    """分页请求参数（预留，后续列表接口复用）。"""

    page: int = Field(1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(10, ge=1, le=100, description="每页条数，1-100")

    @property
    def offset(self) -> int:
        """数据库查询偏移量。"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """数据库查询条数。"""
        return self.page_size


class PageResult(BaseModel, Generic[DataT]):
    """分页返回结构（预留，后续列表接口复用）。"""

    items: List[DataT] = Field(default_factory=list, description="当前页数据")
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页条数")
    pages: int = Field(0, description="总页数")

    @classmethod
    def create(cls, items: List[DataT], total: int, page: int, page_size: int) -> "PageResult[DataT]":
        """根据查询结果构造分页对象，自动计算总页数。"""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=ceil(total / page_size) if page_size else 0,
        )