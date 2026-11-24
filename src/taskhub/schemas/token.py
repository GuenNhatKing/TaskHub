from typing import Literal

from pydantic import BaseModel

from taskhub.schemas.base import BaseRequest


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class LogoutRequest(BaseRequest):
    refresh_token: str
