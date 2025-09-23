"""Market information models"""

from typing import Optional

from pydantic import BaseModel


class MarketData(BaseModel):
    """Market Data information"""

    symbol: Optional[str] = None
    sequenceMsg: Optional[int] = None
    matchedPrice: Optional[float] = None
    tradingVolume: Optional[float] = None
    timestamp: Optional[int] = None
    lastColor: Optional[str] = None
