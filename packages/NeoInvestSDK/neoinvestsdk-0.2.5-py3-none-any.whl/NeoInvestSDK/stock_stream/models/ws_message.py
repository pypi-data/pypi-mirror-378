"""WebSocket message models for StockStream"""

from typing import Any, List, Optional

from pydantic import BaseModel


class WSMessage(BaseModel):
    """Base WebSocket message"""

    type: str
    data: Optional[Any] = None


class SyncMessage(WSMessage):
    """Sync message for schema synchronization"""

    type: str = "sync"
    data: str  # Hash value


class SubMessage(WSMessage):
    """Subscribe message"""

    type: str = "sub"
    channel: str
    listId: List[str]


class UnsubMessage(WSMessage):
    """Unsubscribe message"""

    type: str = "unsub"
    channel: str
    listId: List[str]


class Ops:
    SCHEMA_ID_SYNC = 101
    SYNC_SUCCESS = b"\x00"
