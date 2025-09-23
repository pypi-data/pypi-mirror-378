"""
Authentication API - User authentication and token management
"""

from typing import Callable, Dict, Optional

import httpx
from loguru import logger

from NeoInvestSDK.common.exceptions import *
from NeoInvestSDK.api.models import LoginResponse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NeoInvestSDK import NeoInvestAPI


class AuthenticationAPIEndpoints:
    """Authentication API endpoints"""

    def __init__(self, base: str):
        base = base.rstrip("/")
        self.BASE = base + "/auth"
        self.LOGIN = f"{self.BASE}/token"
        self.REFRESH = f"{self.BASE}/refresh"


class AuthenticationAPI:
    """Authentication operations API"""

    def __init__(self, client: "NeoInvestAPI"):
        """Initialize with HTTP client"""
        self._client = client
        self.config = client.config
        self.endpoints = AuthenticationAPIEndpoints(self.config.api_endpoints.auth_base_url)
        self.timeout = self.config.http_client_config.timeout

        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    async def login(self, username: str = None, password: str = None) -> Dict[str, str]:
        """
        Login with username and password to get access tokens

        Args:
            username: User login name
            password: User password

        Returns:
            Dictionary containing access_token and refresh_token

        Raises:
            AuthenticationError: If login fails
        """

        payload = {
            "username": username if username else self.config.auth_config.username,
            "password": password if password else self.config.auth_config.password,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoints.LOGIN, json=payload, timeout=self.timeout)

                response_data = response.json()
                logger.debug(f"login response: {response_data}")

                if response.status_code != 200:
                    error_msg = f"Login failed: {response_data.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise NeoInvestSDKAuthenticationError(error_msg)

                response_data = response_data.get("data", {})
                login_response = LoginResponse(**response_data)

                if not login_response.access_token:
                    raise NeoInvestSDKAuthenticationError("No access token received from server")

                # Store tokens
                self.access_token = login_response.access_token
                self.refresh_token = login_response.refresh_token

                # Update main client's JWT token
                self._client.set_token(login_response.access_token)

                logger.success(f"login successful for user: {username}")

                return {"access_token": login_response.access_token, "refresh_token": login_response.refresh_token}

        except httpx.RequestError as e:
            error_msg = f"Login request failed: {str(e)}"
            logger.error(error_msg)
            raise NeoInvestSDKAuthenticationError(error_msg)
        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            logger.error(error_msg)
            raise NeoInvestSDKAuthenticationError(error_msg)

    async def refresh_access_token(self) -> Dict[str, str]:
        """
        Refresh access token using refresh token

        Returns:
            Dictionary containing new access_token and refresh_token

        Raises:
            AuthenticationError: If refresh fails
        """
        if not self.refresh_token:
            raise NeoInvestSDKAuthenticationError("No refresh token available")

        payload = {"refresh_token": self.refresh_token}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoints.REFRESH, json=payload, timeout=self.timeout)

                response_data = response.json()
                logger.debug(f"refresh response: {response_data}")

                if response.status_code != 200 or response_data.get("code") != 0:
                    error_msg = f"Token refresh failed: {response_data.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise NeoInvestSDKAuthenticationError(error_msg)

                # Extract new tokens
                data = response_data.get("data", {})
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")

                if not access_token:
                    raise NeoInvestSDKAuthenticationError("No access token received from refresh")

                # Store new tokens
                self.access_token = access_token
                if refresh_token:  # Some systems may not return new refresh token
                    self.refresh_token = refresh_token

                # Update main client's JWT token
                self._client.set_token(access_token)

                logger.success("token refreshed successfully")

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token or self.refresh_token,
                }

        except httpx.RequestError as e:
            error_msg = f"Token refresh request failed: {str(e)}"
            logger.error(error_msg)
            raise NeoInvestSDKAuthenticationError(error_msg)
        except Exception as e:
            error_msg = f"Token refresh error: {str(e)}"
            logger.error(error_msg)
            raise NeoInvestSDKAuthenticationError(error_msg)

    def get_access_token(self) -> Optional[str]:
        """Get current access token"""
        return self.access_token

    def get_refresh_token(self) -> Optional[str]:
        """Get current refresh token"""
        return self.refresh_token

    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has valid access token)"""
        return self.access_token is not None

    def logout(self) -> None:
        """Clear stored tokens (logout)"""
        self.access_token = None
        self.refresh_token = None
        self._client.set_token(None)
        logger.info("user logged out - tokens cleared")
