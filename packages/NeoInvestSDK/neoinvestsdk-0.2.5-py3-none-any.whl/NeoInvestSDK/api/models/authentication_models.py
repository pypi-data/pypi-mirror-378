from typing import Optional
from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
