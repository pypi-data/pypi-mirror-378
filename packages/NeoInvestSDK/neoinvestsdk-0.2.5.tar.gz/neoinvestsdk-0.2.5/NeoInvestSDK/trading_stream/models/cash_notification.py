"""Cash notification model"""

from typing import Optional

from pydantic import BaseModel


class CashNotification(BaseModel):
    """Cash notification data"""

    eventType: Optional[str] = None
    custoDyCd: Optional[str] = None
    afAcctNo: Optional[str] = None
    balance: Optional[int] = None
    balDefOvd: Optional[int] = None
    avlAdvance: Optional[int] = None
