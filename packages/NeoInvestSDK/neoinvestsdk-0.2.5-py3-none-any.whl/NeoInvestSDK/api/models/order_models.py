"""Order-related models for API"""

from typing import Optional, List, Union
from pydantic import BaseModel
from enum import Enum
from NeoInvestSDK.api.models.common import PageableResponse


class OrderType(str, Enum):
    limit = "limit"
    market = "market"


class OrderMarketPriceType(str, Enum):
    LO = "LO"
    ATO = "ATO"
    ATC = "ATC"
    MOK = "MOK"
    MAK = "MAK"
    MTL = "MTL"
    PLO = "PLO"


class OrderCreateRequest(BaseModel):
    """Order creation request"""

    requestId: str
    accountId: str
    symbol: str
    qty: int
    side: str
    type: OrderType
    price: Union[float, OrderMarketPriceType]


class OrderUpdateRequest(BaseModel):
    """Order update request"""

    requestId: str
    accountId: str
    orderId: str
    qty: int
    price: Union[float, OrderMarketPriceType]


class OrderCancelRequest(BaseModel):
    """Order cancel request"""

    requestId: str
    accountId: str
    orderId: str


class OrderResponse(BaseModel):
    """Standard order operation response"""

    transId: str = None


class OrderBookRes(BaseModel):
    """Order book response"""

    accountId: Optional[str] = None
    productTypeCd: Optional[str] = None
    orderId: Optional[str] = None
    symbol: Optional[str] = None
    allowCancel: Optional[str] = None
    allowAmend: Optional[str] = None
    side: Optional[str] = None
    price: Optional[str] = None
    priceType: Optional[str] = None
    type: Optional[str] = None
    via: Optional[str] = None
    qty: Optional[int] = None
    execQty: Optional[int] = None
    execAmt: Optional[int] = None
    execPrice: Optional[int] = None
    remainQty: Optional[int] = None
    remainAmt: Optional[int] = None
    orderStatus: Optional[str] = None
    cancelQty: Optional[int] = None
    adjustQty: Optional[int] = None
    timeTypeValue: Optional[str] = None
    tradeDate: Optional[str] = None
    tradeTime: Optional[str] = None
    parentOrderId: Optional[str] = None
    createBy: Optional[str] = None
    marketPrice: Optional[int] = None
    ceilingPrice: Optional[int] = None
    refPrice: Optional[int] = None


class OrderBookResponse(PageableResponse):
    """Order book list response"""

    content: Optional[List[OrderBookRes]] = None


class MatchTypeValue(str, Enum):
    E = "E"
    N = "N"
    P = "P"


class OrderStatus(str, Enum):
    ALL = "ALL"
    CN = "CN"
    CP = "CP"
    EP = "EP"
    EX = "EX"
    FF = "FF"
    OP = "OP"
    PC = "PC"
    PF = "PF"
    PR = "PR"
    PS = "PS"
    RJ = "RJ"
    RP = "RP"
    ST = "ST"
    WA = "WA"
    WC = "WC"
    WD = "WD"
    WE = "WE"
    WT = "WT"


class OrderSide(str, Enum):
    buy = "buy"
    sell = "sell"


class OrderHistoryItem(BaseModel):
    """Order history response"""

    aright: Optional[int] = None
    createBy: Optional[str] = None
    execAmt: Optional[int] = None
    execPrice: Optional[float] = None
    execQty: Optional[int] = None
    execType: Optional[str] = None
    feeAmt: Optional[int] = None
    feeRate: Optional[float] = None
    isChildOrder: Optional[str] = None
    isForced: Optional[str] = None
    matchTypeValue: Optional[MatchTypeValue] = None
    orderId: Optional[str] = None
    orderStatus: Optional[OrderStatus] = None
    originOrderId: Optional[str] = None
    parentOrderId: Optional[str] = None
    price: Optional[float] = None
    priceType: Optional[str] = None
    qty: Optional[int] = None
    side: Optional[OrderSide] = None
    symbol: Optional[str] = None
    taxAmt: Optional[float] = None
    tradeDate: Optional[str] = None
    tradeTime: Optional[str] = None
    via: Optional[str] = None


class OrderHistoryResponse(PageableResponse):
    """Order history list response"""

    content: List[OrderHistoryItem] = []
