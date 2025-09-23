"""Trading stream message models"""

from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel


class TradingResponseMessage(BaseModel):
    """Trading stream message"""

    type: str
    data: Optional[Union[Dict, Any]] = None
    status: Optional[str] = None


class AuthMessage(BaseModel):
    """Authentication message"""

    action: Literal["auth"]
    data: str
