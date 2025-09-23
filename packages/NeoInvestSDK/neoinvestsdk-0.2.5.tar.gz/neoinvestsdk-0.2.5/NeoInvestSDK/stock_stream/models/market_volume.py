"""Market information models"""

from typing import Optional

from pydantic import BaseModel


class MarketVolume(BaseModel):
    """Market Volume information"""

    indexCode: Optional[str] = None
    indexValue: Optional[float] = None
    indexTime: Optional[str] = None
    totalVolume: Optional[float] = None
    volume: Optional[float] = None
