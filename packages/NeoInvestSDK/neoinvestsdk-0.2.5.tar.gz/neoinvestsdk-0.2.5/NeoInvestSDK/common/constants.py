"""Base models and enums used across all components"""

from enum import Enum


# Common Enums
class OrderStatus(str, Enum):
    """Order status enumeration"""

    ALL = "ALL"
    PENDING_SEND = "PS"  # Pending Send
    WAITING = "WT"  # Waiting
    WAITING_APPROVAL = "WA"  # Waiting Approval
    WAITING_CANCEL = "WC"  # Waiting Cancel
    WAITING_EDIT = "WE"  # Waiting Edit
    SENT = "ST"  # Sent
    # PARTIALLY_FILLED = "PR"  # Partially Filled
    PARTIALLY_CANCELLED = "PC"  # Partially Cancelled
    OPEN = "OP"  # Open
    WAITING_DELETE = "WD"  # Waiting Delete
    PARTIALLY_FILLED = "PF"  # Partially Filled
    FULLY_FILLED = "FF"  # Fully Filled
    REPLACED = "RP"  # Replaced
    CANCELLED = "CN"  # Cancelled
    REJECTED = "RJ"  # Rejected
    EXPIRED = "EX"  # Expired
    EXPIRED_PARTIALLY = "EP"  # Expired Partially
    COMPLETED = "CP"  # Completed


class Side(str, Enum):
    """Order side enumeration"""

    BUY = "buy"
    SELL = "sell"


class MarketStatus(str, Enum):
    """Market status code enumeration"""

    PRE_OPEN = "PO"
    BUY_IN = "B"
    ATO = "ATO"
    LIMITED_ORDER = "LO"
    LUNCH_BREAK = "L"
    ATC = "ATC"
    PUT_THROUGH = "PT"
    POST_LIMIT_ORDER = "PLO"
    CLOSE = "C"
    F = "F"
    HALT = "H"
    PRE_OPEN_VPBANKS = "PRE"


class MarketCode(str, Enum):
    """Market code enumeration"""

    HOSE = "HOSE"
    HNX = "HNX"
    UPCOM = "UPCOM"
    FU = "FU"
    BOND = "BOND"
    ALL = "ALL"


class IndexCode(str, Enum):
    """Index code enumeration"""

    VNINDEX = "VNINDEX"
    VN30 = "VN30"
    HNXINDEX = "HNXINDEX"
    UPCOMINDEX = "UPCOMINDEX"
    HNX30 = "HNX30"
    VNXALL = "VNXALL"


class StockStreamChannel(str, Enum):
    """WebSocket channel enumeration"""

    STOCK_INFO = "stockInfo"
    MARKET_INFO = "marketInfo"
    MARKET_DATA = "marketData"
    MARKET_SESSION = "marketSession"
    FU_TOP_N_PRICE = "fuTopNPrice"
    MARKET_VOLUME = "marketVolume"


class TradingStreamChannel(str, Enum):
    """WebSocket channel enumeration"""

    ORDER_STATUS = "order_status"
    CASH_NOTIFICATION = "cash_notification"
