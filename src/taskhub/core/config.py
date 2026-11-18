from typing import Literal

from pydantic import Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt
    REFRESH_TOKEN_EXPIRE_DAYS: PositiveInt

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
