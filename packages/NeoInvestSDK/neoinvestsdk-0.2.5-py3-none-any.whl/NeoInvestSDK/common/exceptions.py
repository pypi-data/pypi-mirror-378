"""
Custom exceptions for NeoInvestSDK
"""

from typing import Any, Optional


class NeoInvestSDKException(Exception):
    """Base exception for NeoInvestSDK"""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class NeoInvestSDKConnectionError(NeoInvestSDKException):
    """WebSocket connection error"""

    pass


class NeoInvestSDKAuthenticationError(NeoInvestSDKException):
    """Authentication error"""

    pass


class NeoInvestSDKSchemaError(NeoInvestSDKException):
    """Schema synchronization or decoding error"""

    pass


class NeoInvestSDKAPIError(NeoInvestSDKException):
    """API request error"""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data


class NeoInvestSDKOrderError(NeoInvestSDKException):
    """Order-related error"""

    pass


class NeoInvestSDKDataError(NeoInvestSDKException):
    """Data validation or parsing error"""

    pass


class NeoInvestSDKTimeoutError(NeoInvestSDKException):
    """Request timeout error"""

    pass


class NeoInvestSDKRateLimitError(NeoInvestSDKException):
    """Rate limit exceeded error"""

    pass
