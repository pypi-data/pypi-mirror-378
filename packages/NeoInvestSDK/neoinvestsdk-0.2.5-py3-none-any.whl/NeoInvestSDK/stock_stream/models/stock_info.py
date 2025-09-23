"""Stock information models"""

from typing import Optional, Union

from pydantic import BaseModel


class StockInfo(BaseModel):
    """Stock information"""

    symbol: str
    ceilingPrice: Optional[float] = None
    floorPrice: Optional[float] = None
    refPrice: Optional[float] = None
    bidPrice3: Optional[float] = None
    bidVol3: Optional[float] = None
    bidPrice2: Optional[float] = None
    bidVol2: Optional[float] = None
    bidPrice1: Optional[Union[str, float]] = None
    bidVol1: Optional[float] = None
    closePrice: Optional[float] = None
    closeVol: Optional[float] = None
    priceChange: Optional[float] = None
    percentPriceChange: Optional[float] = None
    askPrice1: Optional[Union[str, float]] = None
    askVol1: Optional[float] = None
    askPrice2: Optional[float] = None
    askVol2: Optional[float] = None
    askPrice3: Optional[float] = None
    askVol3: Optional[float] = None
    totalTradingVolume: Optional[int] = None
    totalTradingValue: Optional[float] = None
    averagePrice: Optional[float] = None
    openPrice: Optional[float] = None
    highPrice: Optional[float] = None
    lowPrice: Optional[float] = None
    foreignBuyVolume: Optional[float] = None
    foreignSellVolume: Optional[float] = None
    foreignRemain: Optional[int] = None
    foreignRoom: Optional[int] = None
    totalAskQTTY: Optional[float] = None
    totalBidQTTY: Optional[float] = None
    foreignBuyValue: Optional[float] = None
    foreignSellValue: Optional[float] = None
    foreignNetValue: Optional[float] = None
    breakEvenPoint: Optional[float] = None
