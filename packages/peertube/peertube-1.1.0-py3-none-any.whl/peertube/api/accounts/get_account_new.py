from typing import Any

from peertube.api.base.endpoint_base import BaseEndpoint
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response


class GetAccountEndpoint(BaseEndpoint):
    """Endpoint for getting an account."""

    @property
    def path(self) -> str:
        """API path for the endpoint."""
        return "/api/v1/accounts/{name}"

    @property
    def method(self) -> str:
        """HTTP method for the endpoint."""
        return "get"

    @property
    def response_model(self) -> type[Any] | None:
        """Response model class, if any."""
        return None  # Returns Any

    def _get_kwargs(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        name = args[0]  # First positional argument
        return {
            "method": self.method,
            "url": self.path.format(name=name),
        }


# Backward compatibility functions
def sync_detailed(name: str, *, client: AuthenticatedClient | Client) -> Response[Any]:
    """Get an account

    Args:
        name (str):  Example: chocobozzz | chocobozzz@example.org.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """
    endpoint = GetAccountEndpoint()
    return endpoint.sync_detailed(name, client=client)


def sync(name: str, *, client: AuthenticatedClient | Client) -> Any | None:
    """Get an account

    Args:
        name (str): Example: chocobozzz | chocobozzz@example.org.
        client: The HTTP client instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """
    endpoint = GetAccountEndpoint()
    return endpoint.sync(name, client=client)


async def asyncio_detailed(
    name: str, *, client: AuthenticatedClient | Client
) -> Response[Any]:
    """Get an account

    Args:
        name (str):  Example: chocobozzz | chocobozzz@example.org.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """
    endpoint = GetAccountEndpoint()
    return await endpoint.asyncio_detailed(name, client=client)


async def asyncio(name: str, *, client: AuthenticatedClient | Client) -> Any | None:
    """Get an account

    Args:
        name (str): Example: chocobozzz | chocobozzz@example.org.
        client: The HTTP client instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """
    endpoint = GetAccountEndpoint()
    return await endpoint.asyncio(name, client=client)
