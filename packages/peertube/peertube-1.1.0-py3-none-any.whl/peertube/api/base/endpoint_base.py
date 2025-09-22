from abc import ABC, abstractmethod
from typing import Any, TypeVar

from peertube.types import Response

from .response_handler import build_response

T = TypeVar("T")


class BaseEndpoint(ABC):
    """Abstract base class for API endpoints."""

    @property
    @abstractmethod
    def path(self) -> str:
        """The API path for this endpoint."""
        raise NotImplementedError

    @property
    @abstractmethod
    def method(self) -> str:
        """The HTTP method for this endpoint."""
        raise NotImplementedError

    @property
    @abstractmethod
    def response_model(self) -> type[T] | None:
        """The response model class, or None if no parsing needed."""
        raise NotImplementedError

    @abstractmethod
    def _get_kwargs(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build the request kwargs including URL, method, params, etc."""
        raise NotImplementedError

    def sync_detailed(self, *args: Any, **kwargs: Any) -> Response[T]:
        """Synchronous detailed request."""
        client = kwargs.pop("client")
        request_kwargs = self._get_kwargs(*args, **kwargs)
        response = client.get_httpx_client().request(**request_kwargs)
        return build_response(
            client=client,
            response=response,
            response_model=self.response_model,
        )

    def sync(self, *args: Any, **kwargs: Any) -> T | None:
        """Synchronous request returning parsed response."""
        return self.sync_detailed(*args, **kwargs).parsed

    async def asyncio_detailed(self, *args: Any, **kwargs: Any) -> Response[T]:
        """Asynchronous detailed request."""
        client = kwargs.pop("client")
        request_kwargs = self._get_kwargs(*args, **kwargs)
        response = await client.get_async_httpx_client().request(**request_kwargs)
        return build_response(
            client=client,
            response=response,
            response_model=self.response_model,
        )

    async def asyncio(self, *args: Any, **kwargs: Any) -> T | None:
        """Asynchronous request returning parsed response."""
        return (await self.asyncio_detailed(*args, **kwargs)).parsed
