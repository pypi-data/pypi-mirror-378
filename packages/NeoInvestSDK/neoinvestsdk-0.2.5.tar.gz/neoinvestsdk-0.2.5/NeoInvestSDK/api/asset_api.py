"""
Asset API - Portfolio and derivatives management
"""

from typing import Optional
from loguru import logger

from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.api.models import Result
from NeoInvestSDK.api import models
from NeoInvestSDK.common.config import APIEndpointsConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeoInvestSDK import NeoInvestAPI


class AssetAPIEndpoints:
    """Asset API endpoints"""

    def __init__(self, api_endpoints: APIEndpointsConfig):
        self.BASE = api_endpoints.base_url.rstrip("/") + api_endpoints.asset_prefix
        self.STOCKS = f"{self.BASE}/stocks"
        self.DERIVATIVES_POSITIONS = f"{self.BASE}/derivatives/positions"


class AssetAPI:
    """Asset management operations API"""

    def __init__(self, client: "NeoInvestAPI"):
        """Initialize with HTTP client"""
        self._client = client
        self.config = client.config
        self.endpoints = AssetAPIEndpoints(self.config.api_endpoints)
        self.timeout = self.config.http_client_config.timeout

    async def get_portfolio_stocks(self, account_id: Optional[str] = None, symbol: Optional[str] = None) -> Result[models.PortfolioStocksResponse]:
        """
        Get portfolio stock positions

        Args:
            account_id: Trading account ID filter
            symbol: Stock symbol filter

        Returns:
            Result containing PortfolioStocksResponse on success or error

        Example:
            ::

                result = await api.asset.get_portfolio_stocks(account_id="123456")
                if result.is_success:
                    portfolio: models.PortfolioStocksResponse = result.data  # Type: PortfolioStocksResponse
                    if portfolio.content and portfolio.content.content:
                        print(f"Found {len(portfolio.content.content)} portfolio items")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {}
            if account_id:
                params["accountId"] = account_id
            if symbol:
                params["symbol"] = symbol

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.STOCKS,
                params=params,
                timeout=self.timeout,
            )

            logger.debug(f"Portfolio stocks response: {response}")
            # Parse response data into PortfolioStocksResponse
            # Note: response.data should be the PagePortfolioStocks structure
            if response.data:
                portfolio_data = models.PortfolioStocksResponse(**response.data)
                logger.debug(f"Retrieved portfolio stocks successfully")
                return Result.success(portfolio_data)
            else:
                error = NeoInvestSDKAPIError("No portfolio stocks data received")
                logger.error(f"Portfolio stocks error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Portfolio stocks API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting portfolio stocks: {str(e)}")
            logger.error(f"Portfolio stocks unexpected error: {error}")
            return Result.from_error(error)

    async def get_derivatives_positions(
        self, account_id: Optional[str] = None, symbol: Optional[str] = None
    ) -> Result[models.DerivativesPositionsResponse]:
        """
        Get derivatives positions

        Args:
            account_id: Trading account ID filter
            symbol: Derivatives symbol filter

        Returns:
            Result containing DerivativesPositionsResponse on success or error

        Example:
            ::

                result = await api.asset.get_derivatives_positions(account_id="123456")
                if result.is_success:
                    positions: models.DerivativesPositionsResponse = result.data  # Type: DerivativesPositionsResponse
                    if positions.data and positions.data.content:
                        print(f"Found {len(positions.data.content)} derivatives positions")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {}
            if account_id:
                params["accountId"] = account_id
            if symbol:
                params["symbol"] = symbol

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.DERIVATIVES_POSITIONS,
                params=params,
                timeout=self.timeout,
            )

            logger.debug(f"Derivatives positions response: {response.data}")
            # Parse response data into DerivativesPositionsResponse
            # Note: response.data should be the PageDerivativesPositions structure
            if response.data:
                positions_data = models.DerivativesPositionsResponse(**response.data)
                logger.debug(f"Retrieved derivatives positions successfully")
                return Result.success(positions_data)
            else:
                error = NeoInvestSDKAPIError("No derivatives positions data received")
                logger.error(f"Derivatives positions error: {error}")
                return Result.from_error(error)

        except (NeoInvestSDKAPIError, NeoInvestSDKTimeoutError) as e:
            logger.error(f"Derivatives positions API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = NeoInvestSDKAPIError(f"Unexpected error getting derivatives positions: {str(e)}")
            logger.error(f"Derivatives positions unexpected error: {error}")
            return Result.from_error(error)
