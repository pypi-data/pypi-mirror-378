"""Market data related models for API"""

from typing import List, Optional
from pydantic import BaseModel, Field
from NeoInvestSDK.api.models.common import PageableResponse


class Stock(BaseModel):
    """Stock information"""

    exchangeCode: Optional[str] = None
    marketCode: Optional[str] = None
    orgShortName: Optional[str] = None
    otherName: Optional[str] = None
    stockName: Optional[str] = None
    stockType: Optional[str] = None
    symbol: Optional[str] = None


class StockListResponse(PageableResponse):
    """Stock list response"""

    content: List[Stock] = None


class StockDetailEvent(BaseModel):
    """Stock detail event"""

    eventId: Optional[str] = None
    evenTitle: Optional[str] = None
    eventListCode: Optional[str] = None
    eventName: Optional[str] = None
    exrightDate: Optional[str] = None
    issueDate: Optional[str] = None
    issueYear: Optional[str] = None
    publicDate: Optional[str] = None
    recordDate: Optional[str] = None


class StockDetail(BaseModel):
    """Detailed stock information"""

    askPrice1: Optional[str] = None
    askPrice2: Optional[int] = None
    askPrice3: Optional[int] = None
    askVol1: Optional[int] = None
    askVol2: Optional[int] = None
    askVol3: Optional[int] = None
    averagePrice: Optional[float] = None
    bidPrice1: Optional[str] = None
    bidPrice2: Optional[int] = None
    bidPrice3: Optional[int] = None
    bidVol1: Optional[int] = None
    bidVol2: Optional[int] = None
    bidVol3: Optional[int] = None
    breakEvenPoint: Optional[int] = None
    ceilingPrice: Optional[int] = None
    closePrice: Optional[int] = None
    closeVol: Optional[int] = None
    coveredWarrantType: Optional[str] = None
    diff: Optional[float] = None
    exchangeCode: Optional[str] = None
    exercisePrice: Optional[int] = None
    exerciseRatio: Optional[str] = None
    firstTradingDate: Optional[str] = None
    floorPrice: Optional[int] = None
    foreignBuyValue: Optional[int] = None
    foreignBuyVolume: Optional[int] = None
    foreignRemain: Optional[int] = None
    foreignRoom: Optional[int] = None
    foreignSellValue: Optional[int] = None
    foreignSellVolume: Optional[int] = None
    highPrice: Optional[int] = None
    id: Optional[str] = None
    issuerName: Optional[str] = None
    lastTradingDate: Optional[str] = None
    listedShare: Optional[int] = None
    lowPrice: Optional[int] = None
    marketCode: Optional[str] = None
    maturityDate: Optional[str] = None
    openInterest: Optional[float] = None
    openPrice: Optional[int] = None
    otherName: Optional[str] = None
    percentPriceChange: Optional[float] = None
    priceChange: Optional[int] = None
    ptTotalTradedQTTY: Optional[int] = None
    ptTotalTradedValue: Optional[int] = None
    refPrice: Optional[int] = None
    stockId: Optional[str] = None
    stockName: Optional[str] = None
    stockStatus: Optional[str] = None
    stockType: Optional[str] = None
    symbol: Optional[str] = None
    totalAskQTTY: Optional[int] = None
    totalBidQTTY: Optional[int] = None
    totalTradingValue: Optional[int] = None
    totalTradingVolume: Optional[int] = None
    tradingDate: Optional[str] = None
    tradingSession: Optional[str] = None
    tradingStatus: Optional[str] = None
    underlyingSymbol: Optional[str] = None
    events: Optional[List[StockDetailEvent]] = None


class StockDetailResponse(PageableResponse):
    """Stock detail response"""

    content: List[StockDetail] = None


class MarketIndexStatus(BaseModel):
    """Market status information"""

    indexCode: Optional[str] = None
    marketCode: Optional[str] = None
    marketStatus: Optional[str] = None
    test: str = None


class MarketIndexStatusResponse(BaseModel):
    """Market status response"""

    content: List[MarketIndexStatus] = None


class MarketIndexDetail(BaseModel):
    """Market index information"""

    advances: Optional[float] = None
    declines: Optional[float] = None
    indexChange: Optional[float] = None
    indexCode: Optional[str] = None
    indexColor: Optional[str] = None
    indexPercentChange: Optional[float] = None
    indexTime: Optional[str] = None
    indexValue: Optional[float] = None
    marketStatus: Optional[str] = None
    noChange: Optional[float] = None
    numberOfCe: Optional[float] = None
    numberOfFl: Optional[float] = None
    oddLotTotalValue: Optional[int] = None
    oddLotTotalVolume: Optional[int] = None
    prevIndexValue: Optional[float] = None
    sumValue: Optional[int] = None
    sumVolume: Optional[int] = None
    totalTrading: Optional[int] = None
    totalValue: Optional[int] = None
    totalVolume: Optional[int] = None


class MarketIndexDetailResponse(BaseModel):
    """Market index detail response"""

    content: Optional[List[MarketIndexDetail]] = None


class IntradayMarketIndexItem(BaseModel):
    """Intraday market index data point"""

    indexTime: str = None
    indexValue: float = None
    totalVolume: int = None
    volume: int = None


class IntradayMarketIndexResponse(BaseModel):
    """Intraday market index response"""

    advances: Optional[float] = None
    declines: Optional[float] = None
    indexChange: Optional[float] = None
    indexCode: Optional[str] = None
    indexColor: Optional[str] = None
    indexPercentChange: Optional[float] = None
    indexTime: Optional[str] = None
    indexValue: Optional[float] = None
    marketCode: Optional[str] = None
    marketStatus: Optional[str] = None
    noChange: Optional[float] = None
    numberOfCe: Optional[float] = None
    numberOfFl: Optional[float] = None
    oddLotTotalValue: Optional[float] = None
    oddLotTotalVolume: Optional[float] = None
    prevIndexValue: Optional[float] = None
    sumValue: Optional[int] = None
    sumVolume: Optional[int] = None
    totalTrading: Optional[int] = None
    totalValue: Optional[int] = None
    totalVolume: Optional[int] = None
    index: List[IntradayMarketIndexItem] = None


class MarketIndexItem(BaseModel):
    """Index information"""

    indexCode: Optional[str] = None
    indexName: Optional[str] = None
    indexNameEn: Optional[str] = None
    exchangeCode: Optional[str] = None
    marketCode: Optional[str] = None
    typeIndex: Optional[str] = None
    baseDate: Optional[str] = None
    baseValue: Optional[float] = None


class MarketIndexListResponse(PageableResponse):
    """Index list response"""

    content: List[MarketIndexItem] = None


class OddLotStockDetailItem(BaseModel):
    """Odd lot stock detail item"""

    askPrice1: Optional[str] = None
    askPrice2: Optional[int] = None
    askPrice3: Optional[int] = None
    askVol1: Optional[int] = None
    askVol2: Optional[int] = None
    askVol3: Optional[int] = None
    averagePrice: Optional[float] = None
    bidPrice1: Optional[str] = None
    bidPrice2: Optional[int] = None
    bidPrice3: Optional[int] = None
    bidVol1: Optional[int] = None
    bidVol2: Optional[int] = None
    bidVol3: Optional[int] = None
    ceilingPrice: Optional[int] = None
    closePrice: Optional[int] = None
    closeVol: Optional[int] = None
    coveredWarrantType: Optional[str] = None
    exchangeCode: Optional[str] = None
    firstTradingDate: Optional[str] = None
    floorPrice: Optional[int] = None
    highPrice: Optional[int] = None
    issuerName: Optional[str] = None
    lastTradingDate: Optional[str] = None
    lowPrice: Optional[int] = None
    marketCode: Optional[str] = None
    maturityDate: Optional[str] = None
    percentPriceChange: Optional[float] = None
    priceChange: Optional[int] = None
    refPrice: Optional[int] = None
    stockId: Optional[str] = None
    stockName: Optional[str] = None
    stockStatus: Optional[str] = None
    stockType: Optional[str] = None
    symbol: Optional[str] = None
    totalBidQTTY: Optional[int] = None
    totalOfferQTTY: Optional[int] = None
    totalTradingValue: Optional[int] = None
    totalTradingVolume: Optional[int] = None
    tradingDate: Optional[str] = None
    tradingSession: Optional[str] = None
    underlyingSymbol: Optional[str] = None
    events: Optional[List[StockDetailEvent]] = None


class OddLotStockDetailResponse(PageableResponse):
    """Odd lot stock detail"""

    content: List[OddLotStockDetailItem] = None


class FuStockDetailItem(BaseModel):
    """FU stock detail item"""

    askPrice1: Optional[str] = None
    askPrice2: Optional[int] = None
    askPrice3: Optional[int] = None
    askVol1: Optional[int] = None
    askVol2: Optional[int] = None
    askVol3: Optional[int] = None
    averagePrice: Optional[float] = None
    bidPrice1: Optional[str] = None
    bidPrice2: Optional[int] = None
    bidPrice3: Optional[int] = None
    bidVol1: Optional[int] = None
    bidVol2: Optional[int] = None
    bidVol3: Optional[int] = None
    ceilingPrice: Optional[int] = None
    closePrice: Optional[float] = None
    closeVol: Optional[int] = None
    coveredWarrantType: Optional[str] = None
    diff: Optional[float] = None
    exchangeCode: Optional[str] = None
    exercisePrice: Optional[int] = None
    exerciseRatio: Optional[str] = None
    firstTradingDate: Optional[str] = None
    floorPrice: Optional[int] = None
    foreignBuyValue: Optional[int] = None
    foreignBuyVolume: Optional[int] = None
    foreignRemain: Optional[int] = None
    foreignRoom: Optional[int] = None
    foreignSellValue: Optional[int] = None
    foreignSellVolume: Optional[int] = None
    highPrice: Optional[int] = None
    issuerName: Optional[str] = None
    lastTradingDate: Optional[str] = None
    listedShare: Optional[int] = None
    lowPrice: Optional[int] = None
    marketCode: Optional[str] = None
    maturityDate: Optional[str] = None
    openInterest: Optional[float] = None
    openPrice: Optional[int] = None
    otherName: Optional[str] = None
    percentPriceChange: Optional[float] = None
    priceChange: Optional[int] = None
    ptTotalTradedQTTY: Optional[int] = None
    ptTotalTradedValue: Optional[int] = None
    refPrice: Optional[int] = None
    stockId: Optional[str] = None
    stockName: Optional[str] = None
    stockStatus: Optional[str] = None
    stockType: Optional[str] = None
    symbol: Optional[str] = None
    totalAskQTTY: Optional[int] = None
    totalBidQTTY: Optional[int] = None
    totalTradingValue: Optional[int] = None
    totalTradingVolume: Optional[int] = None
    tradingDate: Optional[str] = None
    tradingSession: Optional[str] = None
    underlyingSymbol: Optional[str] = None


class FuStockDetailResponse(PageableResponse):
    """FU stock detail response"""

    content: List[FuStockDetailItem] = []
