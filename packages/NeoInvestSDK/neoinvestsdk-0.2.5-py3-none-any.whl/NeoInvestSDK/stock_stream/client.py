"""
StockStream WebSocket client for real-time market data
"""

import asyncio
import base64
import hashlib
import json
import zlib
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional

import avro.io
import avro.schema
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed
from loguru import logger

from NeoInvestSDK.stock_stream import models
from NeoInvestSDK.common import constants
from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.common import SchemaChannelMapping
from NeoInvestSDK.common import SDKConfig


class StockStream:
    """WebSocket client for real-time stock market data streaming

    Example:
        ::

            config = SDKConfig()
            config.log_config.level = "DEBUG"
            stock_stream = StockStream(config)
            stock_stream.on_connected = lambda: logger.success("Connected to market data stream!")
            stock_stream.on_disconnected = lambda: logger.warning("Disconnected from market data stream")
            stock_stream.on_error = lambda e: logger.error(f"Stream error: {e}")

            await stock_stream.connect()
            await stock_stream.subscribe_stock_info(["VNM", "VIC"], handle_stock_update)
            await stock_stream.subscribe_market_info(["VNINDEX", "VN30"], handle_market_update)
            await stock_stream.subscribe_market_data(["VNM", "VIC"], handle_market_data)
            await stock_stream.subscribe_market_session(["HOSE", "HNX"], handle_market_session)
            await stock_stream.subscribe_fu_top_n_price(["VNM", "VIC"], handle_fu_top_n_price)
            await stock_stream.subscribe_market_volume(["VNINDEX", "VN30"], handle_market_volume)
            await stock_stream.disconnect()

    Args:
        config: SDK configuration object

    Attributes:
        config: SDK configuration object
        is_connected: Connection status
        is_synced: Schema synchronization status
        on_connected: Connected event handler
        on_disconnected: Disconnected event handler
        on_error: Error event handler

    """

    def __init__(self, config: Optional[SDKConfig] = None):
        """
        Initialize StockStream client

        Args:
            config: SDK configuration object
        """
        self.config = config or SDKConfig()
        self.config.setup_logging()

        self._ws: Optional[ClientConnection] = None
        self.is_connected: bool = False
        self.is_synced: bool = False
        self._schemas: Dict[int, Any] = {}
        self._handlers: Dict[str, List[Callable]] = {}
        self._schema_cache_file = self.config.schema_cache_dir / "stock_schemas.dat"

        # Message queue for messages sent before connection/sync is ready
        self._message_queue: List[Dict[str, Any]] = []

        # Event handlers - can be sync or async functions
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Create schema cache directory
        self.config.schema_cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("StockStream client initialized")

    async def _call_event_handler(self, handler: Callable, *args) -> None:
        """Call event handler, supporting both sync and async functions"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args)
            else:
                handler(*args)
        except Exception as e:
            logger.error(f"Event handler error: {e}")

    async def connect(self) -> None:
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to {self.config.api_endpoints.stock_stream_url}")
            self._ws = await connect(self.config.api_endpoints.stock_stream_url, additional_headers=self.config.http_client_config.headers)
            self.is_connected = True
            logger.success("Connected to StockStream WebSocket")

            # Trigger connected event
            if self.on_connected:
                await self._call_event_handler(self.on_connected)

            # Start schema synchronization
            await self._sync_schemas()

            # Start message listener
            asyncio.create_task(self._listen_messages())

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            await self._handle_error(NeoInvestSDKConnectionError(f"Failed to connect: {e}"))
            raise

    async def disconnect(self) -> None:
        """Close WebSocket connection"""
        if self._ws:
            await self._ws.close()
            self.is_connected = False
            self.is_synced = False

            # Clear message queue
            if self._message_queue:
                logger.info(f"Clearing {len(self._message_queue)} queued messages")
                self._message_queue.clear()

            logger.info("Disconnected from StockStream")

            if self.on_disconnected:
                await self._call_event_handler(self.on_disconnected)

    async def _sync_schemas(self) -> None:
        """Synchronize Avro schemas with server"""
        try:
            # Check for cached schemas
            schema_hash = ""
            if self._schema_cache_file.exists():
                cached_data = self._schema_cache_file.read_bytes()
                schema_hash = hashlib.sha1(cached_data).hexdigest()
                logger.info(f"Found cached schemas with hash: {schema_hash}")

            # Send sync message
            sync_msg = models.SyncMessage(data=schema_hash)
            await self._send_message(sync_msg.dict(), requires_sync=False)
            logger.info("sent schema sync request")

            # Wait for sync response
            response = await self._wait_for_sync_response()

            if response:
                logger.success("Schema synchronization completed")
                self.is_synced = True

                # Process queued messages
                await self._process_message_queue()

        except Exception as e:
            logger.error(f"Schema synchronization failed: {e}")
            raise NeoInvestSDKSchemaError(f"Failed to sync schemas: {e}")

    async def _wait_for_sync_response(self) -> bool:
        """Wait for schema sync response from server"""
        while True:
            try:
                message = await asyncio.wait_for(self._ws.recv(), timeout=10.0)

                if isinstance(message, bytes):
                    schema_id = message[0]

                    if schema_id == models.Ops.SCHEMA_ID_SYNC:
                        data = message[1:]

                        if data == models.Ops.SYNC_SUCCESS:
                            # Schemas already synced
                            logger.info("Schemas already synchronized")
                            await self._load_cached_schemas()
                            return True
                        else:
                            # New schemas received
                            logger.info("Received new schemas from server")
                            await self._process_new_schemas(data)

                            # Send confirmation
                            new_hash = hashlib.sha1(data).hexdigest()
                            sync_msg = models.SyncMessage(data=new_hash)
                            await self._send_message(sync_msg.dict())

                            # Wait for confirmation
                            confirm = await asyncio.wait_for(self._ws.recv(), timeout=5.0)
                            if confirm == bytes([models.Ops.SCHEMA_ID_SYNC]) + models.Ops.SYNC_SUCCESS:
                                logger.success("Schema sync confirmed")
                                return True

            except asyncio.TimeoutError:
                logger.error("Schema sync response timeout")
                return False
            except Exception as e:
                logger.error(f"Error waiting for sync response: {e}")
                return False

    async def _process_new_schemas(self, data: bytes) -> None:
        """Process and cache new schemas from server"""
        try:
            # Decompress and decode schemas
            decompressed = zlib.decompress(base64.b64decode(data))
            schema_dict = json.loads(decompressed.decode("utf-8"))

            # Parse and compile schemas
            for schema_id_str, schema_json in schema_dict.items():
                schema_id = int(schema_id_str)
                schema = avro.schema.parse(json.dumps(schema_json))
                self._schemas[schema_id] = schema
                logger.debug(f"Compiled schema ID {schema_id}")

            # Cache schemas
            self._schema_cache_file.write_bytes(data)
            logger.info(f"Cached {len(self._schemas)} schemas")

        except Exception as e:
            logger.error(f"Failed to process schemas: {e}")
            raise NeoInvestSDKSchemaError(f"Schema processing failed: {e}")

    async def _load_cached_schemas(self) -> None:
        """Load schemas from cache"""
        try:
            if self._schema_cache_file.exists():
                data = self._schema_cache_file.read_bytes()
                await self._process_new_schemas(data)
                logger.info("Loaded schemas from cache")
        except Exception as e:
            logger.error(f"Failed to load cached schemas: {e}")

    async def _process_message_queue(self) -> None:
        """Process messages that were queued before sync was complete"""
        if not self._message_queue:
            return

        logger.info(f"Processing {len(self._message_queue)} queued messages")

        while self._message_queue:
            message = self._message_queue.pop(0)
            try:
                if self._ws and self.is_connected and self.is_synced:
                    await self._ws.send(json.dumps(message))
                    logger.debug(f"sent -> {json.dumps(message)}")
                else:
                    # Put message back in queue if conditions not met
                    self._message_queue.insert(0, message)
                    logger.warning("Cannot process queued messages - connection/sync not ready")
                    break
            except Exception as e:
                logger.error(f"Error processing queued message {message}: {e}")

        if not self._message_queue:
            logger.success("All queued messages processed")

    async def _listen_messages(self) -> None:
        """Listen for incoming WebSocket messages"""
        while self.is_connected:
            try:
                message = await self._ws.recv()
                if isinstance(message, bytes) and self.is_synced:
                    await self._handle_binary_message(message)

            except ConnectionClosed:
                logger.warning("WebSocket connection closed")
                await self._handle_disconnect()
                break
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await self._handle_error(e)

    async def _handle_binary_message(self, message: bytes) -> None:
        """Handle binary Avro-encoded message"""
        try:
            schema_id = message[0]
            binary_data = message[1:]

            if schema_id in self._schemas:
                schema = self._schemas[schema_id]

                # Decode Avro message
                bytes_reader = BytesIO(binary_data)
                decoder = avro.io.BinaryDecoder(bytes_reader)
                reader = avro.io.DatumReader(schema)
                data = reader.read(decoder)

                logger.debug(f"recv <- schema_id={schema_id}: {json.dumps(data) if isinstance(data, dict) else str(data)}")

                # Route to handlers based on channel
                await self._route_message(schema_id, data)

            else:
                logger.warning(f"Unknown schema ID: {schema_id}")

        except Exception as e:
            logger.error(f"Failed to decode binary message: {e}")

    async def _route_message(self, schema_id: int, data: Any) -> None:
        """Route decoded message to appropriate handlers based on message content"""
        try:
            # Determine channel based on data content or schema_id
            channel = self._determine_channel(data, schema_id)

            if channel and channel in self._handlers:
                handlers = self._handlers[channel]
                for handler in handlers:
                    try:
                        if channel == constants.StockStreamChannel.STOCK_INFO.value:
                            await handler(models.StockInfo(**data))
                        elif channel == constants.StockStreamChannel.MARKET_INFO.value:
                            await handler(models.MarketInfo(**data))
                        elif channel == constants.StockStreamChannel.MARKET_DATA.value:
                            await handler(models.MarketData(**data))
                        elif channel == constants.StockStreamChannel.MARKET_SESSION.value:
                            await handler(models.MarketSession(**data))
                        elif channel == constants.StockStreamChannel.FU_TOP_N_PRICE.value:
                            await handler(models.FuTopNPrice(**data))
                        elif channel == constants.StockStreamChannel.MARKET_VOLUME.value:
                            await handler(models.MarketVolume(**data))
                        else:
                            await handler(data)
                    except Exception as e:
                        logger.error(f"Handler error for channel {channel}: {e}")
            else:
                logger.warning(f"No handler found for channel '{channel}', schema_id {schema_id}")

        except Exception as e:
            logger.error(f"Error routing message: {e}")

    def _determine_channel(self, data: Any, schema_id: int) -> Optional[str]:
        """Determine channel based on message data content or schema_id"""
        try:
            channel = SchemaChannelMapping.get_channel(schema_id)
            if channel:
                return channel

            logger.debug(
                f"Could not determine channel for schema_id {schema_id}, data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
            )
            return None

        except Exception as e:
            logger.error(f"Error determining channel: {e}")
            return None

    async def _send_message(self, message: dict, requires_sync: bool = True) -> None:
        """Send message to WebSocket server or queue if not ready"""
        if requires_sync and not self.is_synced:
            self._message_queue.append(message)
            logger.debug(f"queued (waiting sync) -> {json.dumps(message)}")
            return

        await self._ws.send(json.dumps(message))
        logger.debug(f"sent -> {json.dumps(message)}")

    async def _handle_subscribe(self, channel: str, listId: List[str], handler: Callable[[Any], Any]) -> None:
        """Handle subscribe message"""
        # Register handler
        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

        logger.debug(f"registered handler for channel '{channel}', total handlers: {len(self._handlers[channel])}")

        # Send subscription
        sub_msg = models.SubMessage(channel=channel, listId=listId)
        await self._send_message(sub_msg.dict())
        logger.success(f"subscribed to {channel} for {listId}")

    async def send_message_to_server(self, message: dict) -> None:
        """Send message to server"""
        await self._send_message(message)

    async def subscribe_stock_info(self, symbols: List[str], handler: Callable[[models.StockInfo], Any]) -> None:
        """
        Subscribe to stock info updates

        Args:
            symbols: List of stock symbols
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.STOCK_INFO.value

        await self._handle_subscribe(channel, symbols, handler)

    async def subscribe_market_info(self, index_codes: List[str], handler: Callable[[models.MarketInfo], Any]) -> None:
        """
        Subscribe to market info updates

        Args:
            index_codes: List of index codes (VNINDEX, VN30, HNXINDEX, UPCOMINDEX, VNXALL, HNX30, etc.)
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.MARKET_INFO.value

        await self._handle_subscribe(channel, index_codes, handler)

    async def subscribe_market_data(self, symbols: List[str], handler: Callable[[models.MarketData], Any]) -> None:
        """
        Subscribe to market data updates

        Args:
            symbols: List of stock symbols
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.MARKET_DATA.value

        await self._handle_subscribe(channel, symbols, handler)

    async def subscribe_market_session(self, market_codes: List[str], handler: Callable[[models.MarketSession], Any]) -> None:
        """
        Subscribe to market session updates

        Args:
            market_codes: List of market codes (HOSE, HNX, etc.)
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.MARKET_SESSION.value

        await self._handle_subscribe(channel, market_codes, handler)

    async def subscribe_fu_top_n_price(self, symbols: List[str], handler: Callable[[models.FuTopNPrice], Any]) -> None:
        """
        Subscribe to Fu Top N Price updates

        Args:
            symbols: List of stock symbols
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.FU_TOP_N_PRICE.value

        await self._handle_subscribe(channel, symbols, handler)

    async def subscribe_market_volume(self, index_codes: List[str], handler: Callable[[models.MarketVolume], Any]) -> None:
        """
        Subscribe to market volume updates

        Args:
            index_codes: List of Index codes (VNINDEX, VN30, HNXINDEX, UPCOMINDEX, VNXALL, HNX30, etc.)
            handler: Async handler function for updates
        """
        channel = constants.StockStreamChannel.MARKET_VOLUME.value

        await self._handle_subscribe(channel, index_codes, handler)

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current message queue status"""
        return {
            "queue_size": len(self._message_queue),
            "is_connected": self.is_connected,
            "is_synced": self.is_synced,
            "ready_to_send": self.is_connected and self.is_synced,
        }

    async def unsubscribe(self, channel: str, items: List[str]) -> None:
        """
        Unsubscribe from channel

        Args:
            channel: Channel name
            items: List of items to unsubscribe
        """
        unsub_msg = models.UnsubMessage(channel=channel, listId=items)
        await self._send_message(unsub_msg.dict())
        logger.info(f"unsubscribed from {channel} for {items}")

        # Log handler count after unsubscribe
        if channel in self._handlers:
            logger.debug(f"Channel '{channel}' still has {len(self._handlers[channel])} handlers")

    async def _handle_disconnect(self) -> None:
        """Handle disconnection"""
        self.is_connected = False
        self.is_synced = False

        # Clear message queue
        if self._message_queue:
            logger.info(f"Clearing {len(self._message_queue)} queued messages due to disconnect")
            self._message_queue.clear()

        if self.on_disconnected:
            await self._call_event_handler(self.on_disconnected)

        # Auto-reconnect logic can be added here

    async def _handle_error(self, error: Exception) -> None:
        """Handle errors"""
        if self.on_error:
            await self._call_event_handler(self.on_error, error)
