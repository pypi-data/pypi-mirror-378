from typing import Any, Generic, Optional, TypeVar, Union

from pydantic import BaseModel


T = TypeVar("T")


class Result(Generic[T]):
    """
    Result wrapper that can contain either success data or error

    Usage:
        ::

            result = await api.account.get_account_list()
            if result.is_success:
                accounts = result.data  # Type: AccountsListResponse
            else:
                print(f"Error: {result.error}")
    """

    def __init__(self, data: Optional[T] = None, error: Optional[Exception] = None):
        if data is not None and error is not None:
            raise ValueError("Result cannot have both data and error")
        if data is None and error is None:
            raise ValueError("Result must have either data or error")

        self._data = data
        self._error = error

    @property
    def is_success(self) -> bool:
        """Check if result contains success data"""
        return self._error is None

    @property
    def is_error(self) -> bool:
        """Check if result contains error"""
        return self._error is not None

    @property
    def data(self) -> T:
        """Get success data (raises if error)"""
        if self._error is not None:
            raise self._error
        return self._data

    @property
    def error(self) -> Optional[Exception]:
        """Get error (None if success)"""
        return self._error

    def unwrap(self) -> T:
        """Get data or raise error"""
        return self.data

    def unwrap_or(self, default: T) -> T:
        """Get data or return default if error"""
        if self.is_success:
            return self._data
        return default

    def unwrap_or_else(self, func) -> T:
        """Get data or call function if error"""
        if self.is_success:
            return self._data
        return func(self._error)

    @classmethod
    def success(cls, data: T) -> "Result[T]":
        """Create success result"""
        return cls(data=data)

    @classmethod
    def from_error(cls, error: Exception) -> "Result[T]":
        """Create error result"""
        return cls(error=error)

    def __repr__(self) -> str:
        if self.is_success:
            return f"Result.success({self._data})"
        else:
            return f"Result.error({self._error})"


class ApiResponse(BaseModel):
    """Standard API response"""

    status: int
    code: Optional[str] = None
    message: Optional[str] = None
    messageEn: Optional[str] = None
    messageVi: Optional[str] = None
    timestamp: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[Any] = None


class Pageable(BaseModel):
    """Pageable model"""

    pageNumber: int = None
    paged: bool = None
    unpaged: bool = None
    pageSize: int = None
    offset: int = None


class PageableResponse(BaseModel):
    """Pageable response"""

    totalElements: int = None
    totalPages: int = None
    numberOfElements: int = None
    last: bool = None
    first: bool = None
    size: int = None
    pageable: Union[Pageable, str] = None
