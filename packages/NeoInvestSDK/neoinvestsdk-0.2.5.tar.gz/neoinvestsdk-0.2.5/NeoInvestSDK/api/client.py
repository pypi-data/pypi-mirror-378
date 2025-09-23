"""
NeoInvestAPI REST client for trading, market data, asset, and account operations
"""

from typing import Dict, Optional

import httpx
from loguru import logger

from NeoInvestSDK.common import SDKConfig
from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.api import models
from .account_api import AccountAPI
from .asset_api import AssetAPI
from .authentication_api import AuthenticationAPI
from .market_data_api import MarketDataAPI
from .trading_api import TradingAPI


class NeoInvestAPI:
    """REST API client for NeoPro platform with hierarchical structure

    Example:
        ::

            config = SDKConfig()
            config.log_config.level = "DEBUG"
            api = NeoInvestAPI(config)

            api.set_token(jwt_token)

            await api.auth.login(username, password)
            await api.trading.create_order(...)
            await api.market_data.get_stock_list(...)
            await api.asset.get_portfolio_stocks(...)
            await api.account.get_account_list()

    Args:
            config: SDK configuration object

    Attributes:
        config: SDK configuration object
        jwt_token: JWT authentication token

        auth: Authentication API
        trading: Trading API
        market_data: Market Data API
        asset: Asset API
        account: Account API
    """

    def __init__(self, config: Optional[SDKConfig] = None):
        """
        Initialize API client

        """
        self.config = config or SDKConfig()
        self.config.setup_logging()
        self.jwt_token = None

        self.auth = AuthenticationAPI(self)
        self.trading = TradingAPI(self)
        self.market_data = MarketDataAPI(self)
        self.asset = AssetAPI(self)
        self.account = AccountAPI(self)

        logger.info("NeoInvestAPI client initialized with hierarchical structure")

    def set_token(self, jwt_token: Optional[str]) -> None:
        """Set or update JWT token"""
        self.jwt_token = jwt_token
        if jwt_token:
            logger.debug("JWT token updated")
        else:
            logger.debug("JWT token cleared")

    def get_token(self) -> str:
        """Get JWT token"""
        return self.jwt_token

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {}

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> models.ApiResponse:
        """
        Make HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            ApiResponse object
        """
        try:
            request_headers = self._get_headers(headers)
            request_timeout = timeout or self.config.http_client_config.timeout

            # Use a short-lived AsyncClient per request to avoid event loop binding issues
            async with httpx.AsyncClient(
                trust_env=self.config.http_client_config.trust_env,
                base_url=self.config.api_endpoints.base_url,
                timeout=request_timeout,
                headers={
                    **self.config.http_client_config.headers,
                    "User-Agent": "NeoAPI-PythonSDK",
                    "x-device": "NeoAPI-PythonSDK",
                    "x-devicetype": "edge",
                    **request_headers,
                },
                verify=self.config.http_client_config.verify,
                proxy=self.config.http_client_config.proxy,
            ) as client:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json_data,
                )

            response_data = response.json()
            api_response = models.ApiResponse(**response_data)

            if response.status_code >= 400:
                raise NeoInvestSDKAPIError(
                    f"API error: {api_response.message}",
                    status_code=response.status_code,
                    response_data=response_data,
                )

            return api_response

        except httpx.TimeoutException:
            raise NeoInvestSDKTimeoutError("Request timeout")
        except httpx.RequestError as e:
            raise NeoInvestSDKAPIError(f"Request failed: {e}")
