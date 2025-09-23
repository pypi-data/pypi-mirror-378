"""Order status notification model"""

from typing import Optional

from pydantic import BaseModel


class OrderStatusData(BaseModel):
    """Order status notification data"""

    messageType: Optional[str] = None
    messageNo: Optional[str] = None
    market: Optional[str] = None
    clientRequestId: Optional[str] = None
    transId: Optional[str] = None
    serviceName: Optional[str] = None
    orderId: Optional[str] = None
    custodyId: Optional[str] = None
    accountId: Optional[str] = None
    symbol: Optional[str] = None
    price: Optional[str] = None
    side: Optional[str] = None
    execQty: Optional[int] = None
    orderStatus: Optional[str] = None
    remainQty: Optional[int] = None
    priceType: Optional[str] = None
    cancelQty: Optional[int] = None
    adjustQty: Optional[int] = None
    via: Optional[str] = None
    qty: Optional[int] = None
    timeTypeValue: Optional[str] = None
    execPrice: Optional[int] = None
    feedbackMessage: Optional[str] = None
