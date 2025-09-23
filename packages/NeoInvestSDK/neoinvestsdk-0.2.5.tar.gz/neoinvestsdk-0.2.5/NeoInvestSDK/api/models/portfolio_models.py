"""Portfolio-related models for API"""

from typing import List, Optional
from pydantic import BaseModel
from NeoInvestSDK.api.models.common import PageableResponse


class Portfolio(BaseModel):
    """Portfolio position"""

    symbol: str
    total: Optional[float] = None
    trade: Optional[float] = None
    blocked: Optional[float] = None
    costPrice: Optional[float] = None
    marketPrice: Optional[float] = None
    pnlAmt: Optional[float] = None
    pnlRate: Optional[float] = None


class PortfolioStocksRes(BaseModel):
    """Portfolio stocks response item - exact match with OpenAPI schema"""

    custodyCd: Optional[str] = None
    accountId: Optional[str] = None
    symbol: Optional[str] = None
    secType: Optional[str] = None
    market: Optional[str] = None
    total: Optional[float] = None
    trade: Optional[float] = None
    blocked: Optional[float] = None
    vsdMortgage: Optional[float] = None
    mortgage: Optional[float] = None
    restrict: Optional[float] = None
    receivingRight: Optional[float] = None
    receivingT0: Optional[float] = None
    receivingT1: Optional[float] = None
    receivingT2: Optional[float] = None
    costPrice: Optional[float] = None
    costPriceAmt: Optional[float] = None
    basicPrice: Optional[float] = None
    basicPriceAmt: Optional[float] = None
    marginAmt: Optional[str] = None
    pnlAmt: Optional[str] = None
    pnlRate: Optional[str] = None
    isSell: Optional[str] = None
    closePrice: Optional[float] = None
    withdraw: Optional[float] = None
    matchIngAmt: Optional[float] = None
    totalPnl: Optional[float] = None
    productTypeName: Optional[str] = None


class PortfolioStocks(BaseModel):
    """Portfolio stocks main response - exact match with OpenAPI schema"""

    accountId: Optional[str] = None
    productTypeCd: Optional[str] = None
    portfolio: Optional[List[PortfolioStocksRes]] = None


class PortfolioStocksResponse(PageableResponse):
    """Portfolio stocks API response"""

    content: List[PortfolioStocks] = None


class OpenPositions(BaseModel):
    """Open derivatives positions - exact match with OpenAPI schema"""

    afacctno: Optional[str] = None
    custodycd: Optional[str] = None
    diff: Optional[int] = None
    dsp: Optional[int] = None
    isclose: Optional[str] = None
    isnet: Optional[str] = None
    istpsl: Optional[str] = None
    lastchange: Optional[str] = None
    nonrplamt: Optional[int] = None
    nvalue: Optional[int] = None
    pecentnonrplamt: Optional[int] = None
    pendinglqtty: Optional[int] = None
    pendingsqtty: Optional[int] = None
    position: Optional[str] = None
    pricesecured: Optional[int] = None
    qtty: Optional[int] = None
    quoteid: Optional[str] = None
    symbol: Optional[str] = None
    totalplamt: Optional[int] = None
    vmamt: Optional[int] = None
    vrdebtvmamt: Optional[int] = None
    vrimamt: Optional[int] = None
    vwap: Optional[int] = None


class ClosePositions(BaseModel):
    """Closed derivatives positions - exact match with OpenAPI schema"""

    closetime: Optional[str] = None
    diff: Optional[int] = None
    numofrow: Optional[str] = None
    nvalue: Optional[int] = None
    orderid: Optional[str] = None
    qtty: Optional[int] = None
    side: Optional[str] = None
    swap: Optional[int] = None
    symbol: Optional[str] = None
    vrdebtvmamt: Optional[int] = None
    vwap: Optional[int] = None


class DerivativesPositions(BaseModel):
    """Derivatives positions response - exact match with OpenAPI schema"""

    accountId: Optional[str] = None
    productTypeCd: Optional[str] = None
    openPositions: Optional[List[OpenPositions]] = None
    closePositions: Optional[List[ClosePositions]] = None


class DerivativesPositionsResponse(PageableResponse):
    """Derivatives positions API response"""

    content: List[DerivativesPositions] = None
