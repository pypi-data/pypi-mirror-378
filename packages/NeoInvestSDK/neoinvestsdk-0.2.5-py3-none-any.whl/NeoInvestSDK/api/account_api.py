"""
Account API - Account management and information
"""

from typing import Optional
from loguru import logger

from NeoInvestSDK.common import exceptions
from NeoInvestSDK.api.models import Result
from NeoInvestSDK.api import models
from NeoInvestSDK.common.config import APIEndpointsConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeoInvestSDK import NeoInvestAPI


class AccountAPIEndpoints:
    """Account API endpoints"""

    def __init__(self, api_endpoints: APIEndpointsConfig):
        self.BASE = api_endpoints.base_url.rstrip("/") + api_endpoints.accounts_prefix
        self.ACCOUNT_LIST = f"{self.BASE}/accountList"
        self.AVAILABLE_TRADE = f"{self.BASE}/availableTrade"


class AccountAPI:
    """Account management operations API"""

    def __init__(self, client: "NeoInvestAPI"):
        """Initialize with HTTP client"""
        self._client = client
        self.config = client.config
        self.endpoints = AccountAPIEndpoints(self.config.api_endpoints)
        self.timeout = self.config.http_client_config.timeout

    async def get_account_list(self) -> Result[models.AccountsListResponse]:
        """
        Get list of trading accounts

        Returns:
            Result containing AccountsListResponse on success or error

        Example:
            ::

                result = await api.account.get_account_list()
                if result.is_success:
                    accounts: models.AccountsListResponse = result.data  # Type: AccountsListResponse
                    print(f"Found {len(accounts.stockAccount or [])} stock accounts")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.ACCOUNT_LIST,
                timeout=self.timeout,
            )
            logger.debug(f"Account list response: {response}")
            # Parse response data into AccountsListResponse
            # Note: response.data should be the AccountsListResponse structure
            if response.data:
                account_data = models.AccountsListResponse(**response.data)
                logger.debug(f"Retrieved account list successfully")
                return Result.success(account_data)
            else:
                error = exceptions.NeoInvestSDKAPIError("No account data received")
                logger.error(f"Account list error: {error}")
                return Result.from_error(error)

        except (exceptions.NeoInvestSDKAPIError, exceptions.NeoInvestSDKTimeoutError) as e:
            logger.error(f"Account list API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = exceptions.NeoInvestSDKAPIError(f"Unexpected error getting account list: {str(e)}")
            logger.error(f"Account list unexpected error: {error}")
            return Result.from_error(error)

    async def get_available_trade(
        self,
        account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        quote_price: Optional[str] = None,
    ) -> Result[models.AvailableTradeResponse]:
        """
        Get available trading capacity

        Args:
            account_id: Trading account ID
            symbol: Stock symbol
            quote_price: Quote price

        Returns:
            Result containing AvailableTradeResponse on success or error

        Example:
            ::

                result = await api.account.get_available_trade(account_id="123", symbol="VIC")
                if result.is_success:
                    trade_info: models.AvailableTradeResponse = result.data  # Type: AvailableTradeResponse
                    print(f"Max buy quantity: {trade_info.maxBuyQty}")
                else:
                    print(f"Error: {result.error}")
        """
        try:
            params = {}
            if account_id:
                params["accountId"] = account_id
            if symbol:
                params["symbol"] = symbol
            if quote_price:
                params["quotePrice"] = quote_price

            response = await self._client._request(
                method="GET",
                endpoint=self.endpoints.AVAILABLE_TRADE,
                params=params,
                timeout=self.timeout,
            )

            # Parse response data into AvailableTradeResponse
            # Note: response.data should be the AvailableTradeResponse structure
            if response.data:
                trade_data = models.AvailableTradeResponse(**response.data)
                logger.debug(f"Retrieved available trade info successfully")
                return Result.success(trade_data)
            else:
                error = exceptions.NeoInvestSDKAPIError("No available trade data received")
                logger.error(f"Available trade error: {error}")
                return Result.from_error(error)

        except (exceptions.NeoInvestSDKAPIError, exceptions.NeoInvestSDKTimeoutError) as e:
            logger.error(f"Available trade API error: {e}")
            return Result.from_error(e)
        except Exception as e:
            error = exceptions.NeoInvestSDKAPIError(f"Unexpected error getting available trade: {str(e)}")
            logger.error(f"Available trade unexpected error: {error}")
            return Result.from_error(error)
