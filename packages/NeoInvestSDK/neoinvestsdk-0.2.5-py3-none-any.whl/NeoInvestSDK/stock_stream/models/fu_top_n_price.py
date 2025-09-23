"""Market information models"""

from typing import Optional

from pydantic import BaseModel


class FuTopNPrice(BaseModel):
    """Fu Top N Price information"""

    symbol: Optional[str] = None
    top: Optional[int] = None
    buyPrice: Optional[float] = None
    buyVolume: Optional[float] = None
    cumulativeBuyVolume: Optional[float] = None
    sellPrice: Optional[float] = None
    sellVolume: Optional[float] = None
    cumulativeSellVolume: Optional[float] = None
    action: Optional[str] = None
