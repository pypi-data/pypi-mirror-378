"""Market information models"""

from typing import Optional

from pydantic import BaseModel


class MarketInfo(BaseModel):
    """Market index information"""

    dateString: Optional[str] = None
    indexValue: Optional[str] = None
    indexTime: Optional[str] = None
    indexChange: Optional[float] = None
    indexPercentChange: Optional[float] = None
    totalVolume: Optional[int] = None
    totalValue: Optional[int] = None
    marketStatus: Optional[str] = None
    advances: Optional[int] = None
    declines: Optional[int] = None
    noChange: Optional[int] = None
    indexCode: Optional[str] = None
    marketCode: Optional[str] = None
    numberOfCe: Optional[int] = None
    numberOfFl: Optional[int] = None
    oddLotTotalVolume: Optional[int] = None
    oddLotTotalValue: Optional[int] = None
