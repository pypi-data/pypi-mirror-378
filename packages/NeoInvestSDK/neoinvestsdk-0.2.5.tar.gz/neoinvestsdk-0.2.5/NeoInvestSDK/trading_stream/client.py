"""
TradingStream WebSocket client for authenticated trading operations
"""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from NeoInvestSDK.common import SDKConfig
from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.common import constants
from NeoInvestSDK.trading_stream import models


class TradingStream:
    """WebSocket client for authenticated trading stream

    Example:
        ::

            config = SDKConfig()
            config.log_config.level = "DEBUG"
            trading_stream = TradingStream(config)
            trading_stream.on_connected = lambda: logger.success("Connected to trading stream!")
            trading_stream.on_authenticated = lambda: logger.success("Authenticated successfully!")
            trading_stream.on_authentication_error = lambda msg: logger.error(f"Auth failed: {msg}")
            trading_stream.on_disconnected = lambda: logger.warning("Disconnected from trading stream")

            await trading_stream.connect(jwt_token)
            await trading_stream.subscribe_order_status(handle_order_status)
            await trading_stream.subscribe_cash_notification(handle_cash_notification)
            await trading_stream.disconnect()

    Args:
        config: SDK configuration object

    Attributes:
        config: SDK configuration object
        is_connected: Connection status
        is_authenticated: Authentication status
        message_queue: Message queue
        on_connected: Connected event handler
        on_disconnected: Disconnected event handler
        on_error: Error event handler

    """

    def __init__(self, config: Optional[SDKConfig] = None):
        """
        Initialize TradingStream client

        Args:
            config: SDK configuration object
        """
        self.config = config or SDKConfig()
        self.config.setup_logging()

        self._ws: Optional[ClientConnection] = None
        self.is_connected: bool = False
        self.is_authenticated: bool = False
        self._jwt_token: Optional[str] = None

        # Message queue for pending messages
        self.message_queue: List[Dict[str, Any]] = []

        # Event handlers - can be sync or async functions
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_authenticated: Optional[Callable] = None
        self.on_authentication_error: Optional[Callable] = None

        # Message handlers - should be async functions
        self._handlers: Dict[str, List[Callable]] = {}

        logger.info("TradingStream client initialized")

    async def _call_event_handler(self, handler: Callable, *args) -> None:
        """Call event handler, supporting both sync and async functions"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args)
            else:
                handler(*args)
        except Exception as e:
            logger.error(f"Event handler error: {e}")

    async def connect(self, jwt_token: str) -> None:
        """
        Establish WebSocket connection and authenticate

        Args:
            jwt_token: JWT authentication token
        """
        try:
            self._jwt_token = jwt_token
            logger.info(f"Connecting to {self.config.api_endpoints.trading_stream_url}")

            self._ws = await connect(self.config.api_endpoints.trading_stream_url, additional_headers=self.config.http_client_config.headers)
            self.is_connected = True
            logger.success("Connected to TradingStream WebSocket")

            # Trigger connected event
            if self.on_connected:
                await self._call_event_handler(self.on_connected)

            # Start authentication
            await self._authenticate(jwt_token)

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
            self.is_authenticated = False
            logger.info("Disconnected from TradingStream")

            if self.on_disconnected:
                await self._call_event_handler(self.on_disconnected)

    async def _authenticate(self, jwt_token: str) -> None:
        """
        Authenticate with JWT token

        Args:
            jwt_token: JWT authentication token
        """
        auth_message = models.AuthMessage(action="auth", data=jwt_token)

        await self._send_message(auth_message.dict(), bypass_queue=True)
        logger.info("Sent authentication request")

    async def _listen_messages(self) -> None:
        """Listen for incoming WebSocket messages"""
        while self.is_connected:
            try:
                message = await self._ws.recv()

                if isinstance(message, str):
                    await self._route_message(message)

            except ConnectionClosed:
                logger.warning("WebSocket connection closed")
                await self._handle_disconnect()
                break
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await self._handle_error(e)

    async def _route_message(self, message: str) -> None:
        """Handle incoming message"""
        try:
            data = json.loads(message)
            msg = models.TradingResponseMessage(**data)

            # Handle authentication response
            if msg.type == "auth":
                await self._handle_auth_response(msg)

            if msg.type in self._handlers:
                handlers = self._handlers[msg.type]
                for handler in handlers:
                    if msg.type == constants.TradingStreamChannel.ORDER_STATUS.value:
                        await handler(models.OrderStatusData(**msg.data))
                    elif msg.type == constants.TradingStreamChannel.CASH_NOTIFICATION.value:
                        await handler(models.CashNotification(**msg.data))
                    else:
                        await handler(msg.data)
            else:
                logger.debug(f"No handler found for message type: {msg.type}")

        except Exception as e:
            logger.error(f"Failed to handle message: {e}")

    async def _handle_auth_response(self, msg: models.TradingResponseMessage) -> None:
        """Handle authentication response"""
        if msg.status == "success":
            self.is_authenticated = True
            logger.success("Authentication successful")

            if self.on_authenticated:
                await self._call_event_handler(self.on_authenticated)

            # Process queued messages
            await self._process_message_queue()

        else:
            error_msg = msg.data if isinstance(msg.data, str) else "Authentication failed"
            logger.error(f"Authentication failed: {error_msg}")
            self.is_authenticated = False

            if self.on_authentication_error:
                await self._call_event_handler(self.on_authentication_error, error_msg)

            raise NeoInvestSDKAuthenticationError(error_msg)

    async def subscribe_order_status(self, handler: Callable[[models.OrderStatusData], Any]) -> None:
        """
        Subscribe to order status updates

        Args:
            handler: Async handler function for order status updates
        """
        channel = constants.TradingStreamChannel.ORDER_STATUS.value

        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

        logger.debug(f"registered handler for channel '{channel}', total handlers: {len(self._handlers[channel])}")

        sub_message = {"action": "subscribe", "type": "order_status"}
        await self._send_message(sub_message)
        logger.success("Subscribed to order status updates")

    async def subscribe_cash_notification(self, handler: Callable[[models.CashNotification], Any]) -> None:
        """
        Subscribe to cash notifications

        Args:
            handler: Async handler function for cash notifications
        """
        channel = constants.TradingStreamChannel.CASH_NOTIFICATION.value

        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

        logger.debug(f"registered handler for channel '{channel}', total handlers: {len(self._handlers[channel])}")

        sub_message = {"action": "subscribe", "type": "cash_notification"}
        await self._send_message(sub_message)
        logger.success("Subscribed to cash notifications")

    async def _send_message(self, message: dict, bypass_queue: bool = False) -> None:
        """
        Send message to WebSocket server

        Args:
            message: Message to send
            bypass_queue: Whether to bypass the queue (for auth messages)
        """
        if not self.is_connected:
            logger.warning("Not connected, cannot send message")
            return

        if not self.is_authenticated and not bypass_queue:
            # Queue message until authenticated
            self.message_queue.append(message)
            logger.debug(f"Queued message: {message}")
            return

        if self._ws:
            await self._ws.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")

    async def _process_message_queue(self) -> None:
        """Process queued messages after authentication"""
        if self.message_queue:
            logger.info(f"Processing {len(self.message_queue)} queued messages")

            for message in self.message_queue:
                await self._send_message(message, bypass_queue=True)
                await asyncio.sleep(0.1)  # Small delay between messages

            self.message_queue.clear()

    async def _handle_disconnect(self) -> None:
        """Handle disconnection"""
        self.is_connected = False
        self.is_authenticated = False

        if self.on_disconnected:
            await self._call_event_handler(self.on_disconnected)

        # Auto-reconnect logic can be added here
        if self._jwt_token:
            logger.info("Attempting to reconnect...")
            await asyncio.sleep(self.config.http_client_config.retry_delay)
            try:
                await self.connect(self._jwt_token)
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")

    async def _handle_error(self, error: Exception) -> None:
        """Handle errors"""
        if self.on_error:
            await self._call_event_handler(self.on_error, error)
