"""
Schema ID to Channel Mapping
Centralized mapping configuration for routing Stock Stream messages to appropriate handlers
Note: Only used for Stock Stream. Trading Stream uses different message routing mechanism.
"""

from typing import Dict, Optional

from .constants import StockStreamChannel


class SchemaChannelMapping:
    """Centralized schema ID to channel mapping for Stock Stream only"""

    # Stock Stream Schema Mappings
    STOCK_STREAM_MAPPING: Dict[int, str] = {
        # Stock Info schemas
        1: StockStreamChannel.MARKET_DATA.value,
        2: StockStreamChannel.MARKET_INFO.value,
        3: StockStreamChannel.STOCK_INFO.value,
        10: StockStreamChannel.MARKET_VOLUME.value,
        23: StockStreamChannel.FU_TOP_N_PRICE.value,
        26: StockStreamChannel.MARKET_SESSION.value,
    }

    @classmethod
    def get_channel(cls, schema_id: int) -> Optional[str]:
        """
        Get channel for stock stream schema ID

        Args:
            schema_id: Schema ID from Avro message

        Returns:
            Channel name or None if not found
        """
        return cls.STOCK_STREAM_MAPPING.get(schema_id)

    @classmethod
    def get_all_mappings(cls) -> Dict[int, str]:
        """Get all schema mappings"""
        return cls.STOCK_STREAM_MAPPING.copy()

    @classmethod
    def has_schema(cls, schema_id: int) -> bool:
        """Check if schema ID is mapped"""
        return schema_id in cls.STOCK_STREAM_MAPPING


# Export for easy imports
__all__ = ["SchemaChannelMapping"]
