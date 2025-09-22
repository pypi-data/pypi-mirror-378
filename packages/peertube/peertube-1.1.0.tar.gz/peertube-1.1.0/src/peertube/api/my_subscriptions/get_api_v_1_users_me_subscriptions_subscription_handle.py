from typing import Any

import httpx

from peertube.api.shared_utils import build_response, parse_response
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response


def _get_kwargs(subscription_handle: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/users/me/subscriptions/{subscription_handle}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    return parse_response(client=client, response=response)


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return build_response(client=client, response=response)


def sync_detailed(
    subscription_handle: str, *, client: AuthenticatedClient
) -> Response[Any]:
    """Get subscription of my user


    Args:
        subscription_handle (str):  Example: my_username | my_username@example.com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(subscription_handle=subscription_handle)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(subscription_handle: str, *, client: AuthenticatedClient) -> Any | None:
    """Get subscription of my user


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(subscription_handle=subscription_handle, client=client).parsed


async def asyncio_detailed(
    subscription_handle: str, *, client: AuthenticatedClient
) -> Response[Any]:
    """Get subscription of my user


    Args:
        subscription_handle (str):  Example: my_username | my_username@example.com.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(subscription_handle=subscription_handle)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
