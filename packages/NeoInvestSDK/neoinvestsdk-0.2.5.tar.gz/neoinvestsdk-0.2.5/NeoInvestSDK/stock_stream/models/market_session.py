"""Market information models"""

from typing import Optional

from pydantic import BaseModel


class MarketSession(BaseModel):
    """Market index information"""

    marketCode: Optional[str] = None
    rawMarketCode: Optional[str] = None
    marketStatus: Optional[str] = None
    rawMarketStatus: Optional[str] = None
    time: Optional[str] = None
