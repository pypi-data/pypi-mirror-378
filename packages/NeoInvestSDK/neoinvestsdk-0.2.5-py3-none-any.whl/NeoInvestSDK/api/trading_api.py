"""
Trading API - Order management and trading operations
"""

import uuid
from typing import Optional, Union
from loguru import logger

from NeoInvestSDK.api.models import Result
from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.api import models
from NeoInvestSDK.common.config import APIEndpointsConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeoInvestSDK import NeoInvestAPI


class TradingAPIEndpoints:
    """Trading API endpoints"""

    def __init__(self, api_endpoints: APIEndpointsConfig):
        self.BASE = api_endpoints.base_url.rstrip("/") + api_endpoints.trading_prefix
        self.ORDERS = f"{self.BASE}/orders"
        self.ORDER_HISTORY = f"{self.BASE}/orderHistory"
        self.ORDER_BOOK = f"{self.BASE}/orderBook"


class TradingAPI:
    """Trading operations API"""

    def __init__(self, client: "NeoInvestAPI"):
        """Initialize with HTTP client"""
        self._client = client
        self.config = client.config
        self.endpoints = TradingAPIEndpoints(self.config.api_endpoints)
        self.timeout = self.config.http_client_config.timeout
        self.mfa_headers = {
            "method": "pin",
            "value": self.config.auth_config.pin,
            "keep_session": "false",
        }

    async def create_order(
        self,
        account_id: str,
        symbol: str,
        side: models.OrderSide,
        qty: int,
        price: Union[float, models.OrderMarketPriceType],
        type: models.OrderType = "limit",
        request_id: Optional[str] = None,
    ) -> Result[models.OrderResponse]:
        """
        Create a new order

        Args:
            account_id: Trading account ID
            symbol: Stock symbol
            side: Order side (BUY/SELL)
            qty: Order quantity
            price: Order price or market price type
            type: Order type (limit, market)
            request_id: Request ID (auto-generated if not provided)

        Returns:
            Result containing OrderResponse on success or error

        Example:
            ::

                result = await api.trading.create_order(
                    account_id="123456",
                    symbol="VIC",
                    side="BUY",
                    qty=100,
                    price=50000,
                    type="limit",
                    request_id="123456",
                )
                if result.is_success:
                    order = result.data  # Type: OrderResponse
                    print(f"Order created: {order.orderId}")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            if not request_id:
                request_id = str(uuid.uuid4())

            order_request = models.OrderCreateRequest(
                requestId=request_id,
                accountId=account_id,
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                price=price,
            )

            response = await self._client._request(
                method="POST",
                endpoint=self.endpoints.ORDERS,
                json_data=order_request.model_dump(by_alias=True),
                timeout=self.timeout,
                headers=self.mfa_headers,
            )

            logger.info(f"Order create response: {response}")
            # Parse response data into OrderResponse
            if response.data:
                order_data = models.OrderResponse(**response.data)
                logger.info(f"Order created successfully: {order_data}")
                return Result.success(order_data)
            else:
                error = NeoInvestSDKAPIError("No order response data received", response_data=response)
                logger.error(f"Create order error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Create order API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error creating order: {str(e)}")
            logger.error(f"Create order unexpected error: {error}")
            return Result.from_error(error)

    async def update_order(
        self,
        account_id: str,
        order_id: str,
        qty: int,
        price: Union[float, models.OrderMarketPriceType],
        request_id: Optional[str] = None,
    ) -> Result[models.OrderResponse]:
        """
        Update an existing order

        Args:
            account_id: Trading account ID
            order_id: Order ID to update
            qty: New quantity
            price: New price or market price type
            request_id: Request ID (auto-generated if not provided)

        Returns:
            Result containing OrderResponse on success or error
        """
        try:
            if not request_id:
                request_id = str(uuid.uuid4())

            order_request = models.OrderUpdateRequest(
                requestId=request_id,
                accountId=account_id,
                orderId=order_id,
                qty=qty,
                price=price,
            )

            response = await self._client._request(
                method="PUT",
                endpoint=f"{self.endpoints.ORDERS}/{order_id}",
                json_data=order_request.model_dump(by_alias=True),
                timeout=self.timeout,
                headers=self.mfa_headers,
            )

            logger.debug(f"Order update response: {response.data}")
            # Parse response data into OrderResponse
            if response.data:
                order_data = models.OrderResponse(**response.data)
                logger.info(f"Order updated successfully: {order_id}")
                return Result.success(order_data)
            else:
                error = NeoInvestSDKAPIError("No order update response data received", response_data=response)
                logger.error(f"Update order error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Update order API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error updating order: {str(e)}")
            logger.error(f"Update order unexpected error: {error}")
            return Result.from_error(error)

    async def cancel_order(
        self,
        account_id: str,
        order_id: str,
        request_id: Optional[str] = None,
    ) -> Result[models.OrderResponse]:
        """
        Cancel an order

        Args:
            account_id: Trading account ID
            order_id: Order ID to cancel
            request_id: Request ID (auto-generated if not provided)

        Returns:
            Result containing OrderResponse on success or error
        """
        try:
            if not request_id:
                request_id = str(uuid.uuid4())

            cancel_request = models.OrderCancelRequest(
                requestId=request_id,
                accountId=account_id,
                orderId=order_id,
            )

            response = await self._client._request(
                method="DELETE",
                endpoint=f"{self.endpoints.ORDERS}/{order_id}",
                json_data=cancel_request.model_dump(by_alias=True),
                timeout=self.timeout,
            )

            logger.debug(f"Order cancel response: {response.data}")
            # Parse response data into OrderResponse
            if response.data:
                order_data = models.OrderResponse(**response.data)
                logger.info(f"Order cancelled successfully: {order_id}")
                return Result.success(order_data)
            else:
                error = NeoInvestSDKAPIError("No order cancel response data received", response_data=response)
                logger.error(f"Cancel order error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Cancel order API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error cancelling order: {str(e)}")
            logger.error(f"Cancel order unexpected error: {error}")
            return Result.from_error(error)

    async def get_order_history(
        self,
        account_id: str = None,
        productTypeCd: str = None,
        symbol: Optional[str] = None,
        from_date: str = None,
        to_date: str = None,
        side: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 100,
    ) -> Result[models.OrderHistoryResponse]:
        """
        Get order history

        Args:
            account_id: Trading account ID filter
            productTypeCd: Product type code filter
            symbol: Stock symbol filter
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            side: Order side filter (BUY/SELL)
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing OrderHistoryResponse on success or error

        Example:
            ::

                result = await api.trading.get_order_history(
                    account_id="123456",
                    symbol="VIC"
                )
                if result.is_success:
                    order_history: models.OrderHistoryResponse = result.data
                    print(f"Order history: {order_history.content}")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "pageNo": page_no,
                "pageSize": page_size,
            }

            if account_id:
                params["accountId"] = account_id
            if productTypeCd:
                params["productTypeCd"] = productTypeCd
            if symbol:
                params["symbol"] = symbol
            if from_date:
                params["fromDate"] = from_date
            if to_date:
                params["toDate"] = to_date
            if side:
                params["side"] = side

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.ORDER_HISTORY,
                params=params,
                timeout=self.timeout,
            )

            logger.debug(f"Order history response: {response.data}")
            # Parse response data into OrderHistoryResponse
            if response.data:
                history_data = models.OrderHistoryResponse(**response.data)
                logger.debug(f"Retrieved order history: {history_data.totalElements or 0} orders")
                return Result.success(history_data)
            else:
                error = NeoInvestSDKAPIError("No order history data received", response_data=response)
                logger.error(f"Order history error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Order history API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting order history: {str(e)}")
            logger.error(f"Order history unexpected error: {error}")
            return Result.from_error(error)

    async def get_order_book(
        self,
        account_id: str = None,
        productTypeCd: Optional[str] = None,
        symbol: Optional[str] = None,
        order_id: Optional[str] = None,
        order_status: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 100,
    ) -> Result[models.OrderBookResponse]:
        """
        Get order book (active orders)

        Args:
            account_id: Trading account ID filter
            productTypeCd: Product type code filter
            symbol: Stock symbol filter
            order_id: Order ID filter
            order_status: Order status filter
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing OrderBookResponse on success or error

        Example:
            ::

                result = await api.trading.get_order_book(
                    account_id="123456",
                    symbol="VIC"
                )
                if result.is_success:
                    order_book: models.OrderBookResponse = result.data
                    print(f"Order book: {order_book.content}")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "pageNo": page_no,
                "pageSize": page_size,
            }

            if account_id:
                params["accountId"] = account_id
            if productTypeCd:
                params["productTypeCd"] = productTypeCd
            if symbol:
                params["symbol"] = symbol
            if order_id:
                params["orderId"] = order_id
            if order_status:
                params["orderStatus"] = order_status

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.ORDER_BOOK,
                params=params,
                timeout=self.timeout,
            )

            logger.info(f"Order book response: {response.data}")
            # Parse response data into OrderBookResponse
            if response.data:
                book_data = models.OrderBookResponse(**response.data)
                logger.debug(f"Retrieved order book: {book_data.totalElements or 0} orders")
                return Result.success(book_data)
            else:
                error = NeoInvestSDKAPIError("No order book data received", response_data=response)
                logger.error(f"Order book error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Order book API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting order book: {str(e)}")
            logger.error(f"Order book unexpected error: {error}")
            return Result.from_error(error)
