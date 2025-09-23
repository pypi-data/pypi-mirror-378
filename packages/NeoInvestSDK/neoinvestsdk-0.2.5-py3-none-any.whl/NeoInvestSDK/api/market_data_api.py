"""
Market Data API - Stock and market information
"""

from typing import Optional
from loguru import logger

from NeoInvestSDK.api.models import Result
from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.api import models
from NeoInvestSDK.common.config import APIEndpointsConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeoInvestSDK import NeoInvestAPI


class MarketDataAPIEndpoints:
    """Market Data API endpoints"""

    def __init__(self, api_endpoints: APIEndpointsConfig):
        self.BASE = api_endpoints.base_url.rstrip("/") + api_endpoints.api_public_prefix
        self.STOCK_LIST = f"{self.BASE}{api_endpoints.stock_data_prefix}/stockList"
        self.STOCK_DETAIL = f"{self.BASE}{api_endpoints.stock_data_prefix}/stockDetail"
        self.STOCK_DETAIL_BY_INDEX = f"{self.BASE}{api_endpoints.stock_data_prefix}/stockDetailByIndex"
        self.STOCK_ODD_LOT_STOCK_DETAIL = f"{self.BASE}{api_endpoints.stock_data_prefix}/oddLotStockDetail"
        self.FU_STOCK_DETAIL = f"{self.BASE}{api_endpoints.stock_data_prefix}/fuStockDetail"
        self.MARKET_STATUS = f"{self.BASE}{api_endpoints.market_data_prefix}/marketStatus"
        self.MARKET_INDEX_DETAIL = f"{self.BASE}{api_endpoints.market_data_prefix}/marketIndexDetail"
        self.INTRADAY_MARKET_INDEX = f"{self.BASE}{api_endpoints.market_data_prefix}/intradayMarketIndex"
        self.INDEX_LIST = f"{self.BASE}{api_endpoints.market_data_prefix}/indexList"


class MarketDataAPI:
    """Market data operations API"""

    def __init__(self, client: "NeoInvestAPI"):
        """Initialize with HTTP client"""
        self._client = client
        self.config = client.config
        self.endpoints = MarketDataAPIEndpoints(self.config.api_endpoints)
        self.timeout = self.config.http_client_config.timeout

    async def get_stock_list(self, market_code: str = "ALL", page_no: int = 1, page_size: int = 1000) -> Result[models.StockListResponse]:
        """
        Get list of stocks

        Args:
            market_code: Market code filter
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing StockListResponse on success or error

        Example:
            ::

                result = await api.market_data.get_stock_list(market_code="HOSE")
                if result.is_success:
                    stocks: models.StockListResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "marketCode": market_code,
                "pageNo": page_no,
                "pageSize": page_size,
            }

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.STOCK_LIST,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into StockListResponse
            if response.data:
                stock_list = models.StockListResponse(**response.data)
                logger.debug(f"Retrieved stock list: {stock_list.totalElements or 0} stocks")
                return Result.success(stock_list)
            else:
                error = NeoInvestSDKAPIError("No stock list data received")
                logger.error(f"Stock list error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Stock list API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting stock list: {str(e)}")
            logger.error(f"Stock list unexpected error: {error}")
            return Result.from_error(error)

    async def get_stock_detail(
        self, symbol: str = None, market_code: str = "ALL", stock_type: str = None, issuer_name: str = None, page_no: int = 1, page_size: int = 1000
    ) -> Result[models.StockDetailResponse]:
        """
        Get detailed stock information

        Args:
            symbol: Stock symbol
            market_code: Market code
            stock_type: Stock type
            issuer_name: Issuer name
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing StockDetailResponse on success or error

        Example:
            ::

                result = await api.market_data.get_stock_detail(symbol="VPB")
                if result.is_success:
                    stock_detail: models.StockDetailResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "symbols": symbol,
                "marketCode": market_code,
                "stockType": stock_type,
                "issuerName": issuer_name,
                "pageNo": page_no,
                "pageSize": page_size,
            }

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.STOCK_DETAIL,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into StockDetailResponse
            if response.data:
                detail_data = models.StockDetailResponse(**response.data)
                logger.debug(f"Retrieved stock detail for: {symbol}")
                return Result.success(detail_data)
            else:
                error = NeoInvestSDKAPIError(f"No stock detail data received for {symbol}")
                logger.error(f"Stock detail error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Stock detail API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting stock detail: {str(e)}")
            logger.error(f"Stock detail unexpected error: {error}")
            return Result.from_error(error)

    async def get_stock_detail_by_index(self, index_code: str = "ALL", page_no: int = 1, page_size: int = 1000) -> Result[models.StockDetailResponse]:
        """
        Get stock details by index

        Args:
            index_code: Index code filter
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing StockDetailResponse on success or error

        Example:
            ::
                result = await api.market_data.get_stock_detail_by_index(index_code="VNINDEX")
                if result.is_success:
                    stock_detail: models.StockDetailResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "indexCode": index_code,
                "pageNo": page_no,
                "pageSize": page_size,
            }

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.STOCK_DETAIL_BY_INDEX,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into StockListResponse
            if response.data:
                stock_data = models.StockDetailResponse(**response.data)
                logger.debug(f"Retrieved stocks by index {index_code}: {stock_data.totalElements or 0} stocks")
                return Result.success(stock_data)
            else:
                error = NeoInvestSDKAPIError(f"No stock data received for index {index_code}")
                logger.error(f"Stock by index error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Stock by index API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting stocks by index: {str(e)}")
            logger.error(f"Stock by index unexpected error: {error}")
            return Result.from_error(error)

    async def get_odd_lot_stock_detail(
        self, symbol: str = None, market_code: str = "ALL", page_no: int = 1, page_size: int = 1000
    ) -> Result[models.OddLotStockDetailResponse]:
        """
        Get odd lot stock detail

        Args:
            symbol: Stock symbol
            market_code: Market code
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing OddLotStockDetailResponse on success or error

        Example:
            ::
                result = await api.market_data.get_odd_lot_stock_detail(symbol="VPB")
                if result.is_success:
                    odd_lot_stock_detail: models.OddLotStockDetailResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {"symbols": symbol, "marketCode": market_code, "pageNo": page_no, "pageSize": page_size}

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.STOCK_ODD_LOT_STOCK_DETAIL,
                params=params,
                timeout=self.timeout,
            )

            if response.data:
                stock_data = models.OddLotStockDetailResponse(**response.data)
                logger.debug(f"Retrieved odd lot stock detail for: {symbol}")
                return Result.success(stock_data)
            else:
                error = NeoInvestSDKAPIError(f"No odd lot stock detail data received for {symbol}")
                logger.error(f"Odd lot stock detail error: {error}")
                return Result.from_error(error)
        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Odd lot stock detail API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting odd lot stock detail: {str(e)}")
            logger.error(f"Odd lot stock detail unexpected error: {error}")
            return Result.from_error(error)

    async def get_fu_stock_detail(
        self, symbol: str = None, stock_type: str = "ALL", page_no: int = 1, page_size: int = 1000
    ) -> Result[models.FuStockDetailResponse]:
        """
        Get FU stock detail

        Args:
            symbol: Stock symbol
            stock_type: Stock type
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing FuStockDetailResponse on success or error

        Example:
            ::
                result = await api.market_data.get_fu_stock_detail(symbol="41I1G3000")
                if result.is_success:
                    fu_stock_detail: models.FuStockDetailResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {"symbols": symbol, "stockType": stock_type, "pageNo": page_no, "pageSize": page_size}

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.FU_STOCK_DETAIL,
                params=params,
                timeout=self.timeout,
            )

            if response.data:
                stock_data = models.FuStockDetailResponse(**response.data)
                logger.debug(f"Retrieved FU stock detail for: {symbol}")
                return Result.success(stock_data)
            else:
                error = NeoInvestSDKAPIError(f"No FU stock detail data received for {symbol}")
                logger.error(f"FU stock detail error: {error}")
                return Result.from_error(error)
        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"FU stock detail API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting FU stock detail: {str(e)}")
            logger.error(f"FU stock detail unexpected error: {error}")
            return Result.from_error(error)

    async def get_market_status(self, market_code: str = "ALL") -> Result[models.MarketIndexStatusResponse]:
        """
        Get market status information

        Args:
            market_code: Market code filter

        Returns:
            Result containing MarketIndexStatusResponse on success or error

        Example:
            ::
                result = await api.market_data.get_market_status(market_code="HOSE")
                if result.is_success:
                    market_status: models.MarketIndexStatusResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {"marketCode": market_code}

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.MARKET_STATUS,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into MarketIndexStatusResponse
            if response.data:
                status_data = models.MarketIndexStatusResponse(content=response.data)
                logger.debug(f"Retrieved market status for: {market_code}")
                return Result.success(status_data)
            else:
                error = NeoInvestSDKAPIError(f"No market status data received for {market_code}")
                logger.error(f"Market status error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Market status API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting market status: {str(e)}")
            logger.error(f"Market status unexpected error: {error}")
            return Result.from_error(error)

    async def get_market_index_detail(self, index_code: str = "ALL", market_code: str = "") -> Result[models.MarketIndexDetailResponse]:
        """
        Get market index details

        Args:
            index_code: Index code (VNINDEX, HNXINDEX, etc.)
            market_code: Market code filter

        Returns:
            Result containing MarketIndexDetailResponse on success or error

        Example:
            ::
                result = await api.market_data.get_market_index_detail(index_code="VNINDEX")
                if result.is_success:
                    market_index_detail: models.MarketIndexDetailResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {"indexCode": index_code, "marketCode": market_code}

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.MARKET_INDEX_DETAIL,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into MarketIndexResponse
            if response.data:
                index_data = models.MarketIndexDetailResponse(content=response.data)
                logger.debug(f"Retrieved market index detail for: {index_code}")
                return Result.success(index_data)
            else:
                error = NeoInvestSDKAPIError(f"No market index data received for {index_code}")
                logger.error(f"Market index error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Market index API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting market index: {str(e)}")
            logger.error(f"Market index unexpected error: {error}")
            return Result.from_error(error)

    async def get_intraday_market_index(self, index_code: str = "VNINDEX") -> Result[models.IntradayMarketIndexResponse]:
        """
        Get intraday market index data

        Args:
            index_code: Index code (VNINDEX, HNXINDEX, etc.)
            trade_date: Trade date (YYYY-MM-DD), defaults to today

        Returns:
            Result containing IntradayMarketIndexResponse on success or error

        Example:
            ::
                result = await api.market_data.get_intraday_market_index(index_code="VNINDEX")
                if result.is_success:
                    intraday_market_index: models.IntradayMarketIndexResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {"indexCode": index_code}

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.INTRADAY_MARKET_INDEX,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into IntradayMarketIndexResponse
            if response.data:
                intraday_data = models.IntradayMarketIndexResponse(**response.data)
                logger.debug(f"Retrieved intraday data for: {index_code}")
                return Result.success(intraday_data)
            else:
                error = NeoInvestSDKAPIError(f"No intraday data received for {index_code}")
                logger.error(f"Intraday index error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Intraday index API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting intraday index: {str(e)}")
            logger.error(f"Intraday index unexpected error: {error}")
            return Result.from_error(error)

    async def get_index_list(self, exchange_code: str = "ALL", page_no: int = 1, page_size: int = 1000) -> Result[models.MarketIndexListResponse]:
        """
        Get market index list

        Args:
            exchange_code: Exchange code filter
            page_no: Page number
            page_size: Page size

        Returns:
            Result containing MarketIndexListResponse on success or error

        Example:
            ::
                result = await api.market_data.get_index_list(exchange_code="HOSE")
                if result.is_success:
                    index_list: models.MarketIndexListResponse = result.data
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {
                "exchangeCode": exchange_code,
                "pageNo": page_no,
                "pageSize": page_size,
            }

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.INDEX_LIST,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into MarketIndexListResponse
            if response.data:
                index_list_data = models.MarketIndexListResponse(**response.data)
                logger.debug(f"Retrieved index list: {index_list_data.totalElements or 0} indices")
                return Result.success(index_list_data)
            else:
                error = NeoInvestSDKAPIError("No index list data received")
                logger.error(f"Index list error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Index list API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting index list: {str(e)}")
            logger.error(f"Index list unexpected error: {error}")
            return Result.from_error(error)
