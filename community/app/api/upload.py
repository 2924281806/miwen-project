"""
文件名：app/api/upload.py
作用：图片上传接口，文件落地到本地 uploads 目录，并通过静态目录对外提供访问。
说明：返回结构为 {"code", "message", "data"}，data 为可直接访问的图片地址。
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Request, UploadFile
from pydantic import BaseModel, ConfigDict, Field

from app.dependencies import get_current_user
from app.exceptions import BadRequestException
from app.models.user import User
from config import settings

logger = logging.getLogger(__name__)

upload_router = APIRouter(tags=["上传"])


class UploadImageResponse(BaseModel):
    """图片上传返回结构：{"code": int, "message": str, "data": str}。"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "上传成功",
                "data": "http://127.0.0.1:8000/uploads/202611/9f2c7a1b3d4e5f60718293a4b5c6d7e8.png",
            }
        }
    )

    code: int = Field(200, description="业务状态码：200 上传成功")
    message: str = Field("success", description="提示信息")
    data: Optional[str] = Field(None, description="图片访问地址，可直接用于 <img src> 或头像字段")


def _detect_ext(header: bytes) -> Optional[str]:
    """按文件头魔数识别真实图片类型，避免仅凭后缀放行非图片文件。"""
    if header.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "gif"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "webp"
    if header.startswith(b"BM"):
        return "bmp"
    return None


def _ext_matches(suffix: str, detected: str) -> bool:
    """后缀与识别结果是否一致（jpeg 与 jpg 视为同一类型）。"""
    if suffix == detected:
        return True
    return detected == "jpg" and suffix == "jpeg"


@upload_router.post(
    "/uploadImage",
    response_model=UploadImageResponse,
    summary="上传图片",
    description=(
        "登录用户上传图片，支持 jpg/jpeg/png/gif/webp/bmp，单张最大 5MB；"
        "服务端按文件头校验真实类型，按年月分目录存储并返回可直接访问的图片地址。"
    ),
)
def upload_image(
    request: Request,
    file: UploadFile = File(..., description="图片文件，支持 jpg/jpeg/png/gif/webp/bmp"),
    current_user: User = Depends(get_current_user),
) -> UploadImageResponse:
    """上传图片并返回图片访问地址。"""
    suffix = Path(file.filename or "").suffix.lower().lstrip(".")
    if not suffix:
        raise BadRequestException("文件名缺少后缀，无法识别图片类型")
    if suffix not in settings.upload_allowed_exts:
        raise BadRequestException(f"不支持的图片格式，仅允许：{'、'.join(settings.upload_allowed_exts)}")
    if file.content_type and not file.content_type.startswith("image/"):
        raise BadRequestException("上传文件不是图片")

    content = file.file.read()
    if not content:
        raise BadRequestException("上传文件为空")
    if len(content) > settings.UPLOAD_MAX_SIZE:
        raise BadRequestException(f"图片大小超过限制（最大 {settings.UPLOAD_MAX_SIZE // (1024 * 1024)}MB）")

    detected = _detect_ext(content[:16])
    if detected is None:
        raise BadRequestException("文件内容不是有效图片")
    if not _ext_matches(suffix, detected):
        raise BadRequestException("文件内容与后缀不一致")

    sub_dir = datetime.now().strftime("%Y%m")
    save_dir = Path(settings.UPLOAD_DIR) / sub_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{detected}"
    (save_dir / filename).write_bytes(content)

    url = f"{str(request.base_url).rstrip('/')}{settings.UPLOAD_URL_PREFIX}/{sub_dir}/{filename}"
    logger.info("图片上传成功 | user_id=%s size=%s url=%s", current_user.id, len(content), url)
    return UploadImageResponse(code=200, message="上传成功", data=url)