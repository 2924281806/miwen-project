"""
文件名：config.py
作用：全局配置中心，统一从 .env 读取配置项。
说明：所有敏感信息（数据库账号密码、JWT 密钥）均来自环境变量，代码中禁止硬编码。
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """项目配置项，字段名与环境变量名保持一致（大小写不敏感）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 应用基础配置 ----------
    APP_NAME: str = "Community Forum API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ---------- 数据库配置 ----------
    DATABASE_URL: str
    DB_ECHO: bool = False

    # ---------- JWT 配置 ----------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------- 跨域配置 ----------
    CORS_ORIGINS: str = "*"

    # ---------- 日志配置 ----------
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @field_validator("SECRET_KEY")
    @classmethod
    def check_secret_key(cls, value: str) -> str:
        """密钥太短直接启动失败，避免误用弱密钥上线。"""
        if not value or len(value) < 32:
            raise ValueError("SECRET_KEY 长度必须大于等于 32 位，请在 .env 中配置强随机密钥")
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """把逗号分隔的 CORS_ORIGINS 解析成列表。"""
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """缓存配置实例，避免重复读取 .env。"""
    return Settings()


settings = get_settings()