from typing import Any

import httpx

from peertube import errors
from peertube.api.shared_utils import build_response
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response


def _get_kwargs(handle: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/server/followers/{handle}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 204:
        return None

    if response.status_code == 404:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return build_response(client=client, response=response)


def sync_detailed(handle: str, *, client: AuthenticatedClient) -> Response[Any]:
    """Remove or reject a follower to your server


    Args:
        handle (str): Parameter for handle.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(handle=handle)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(handle: str, *, client: AuthenticatedClient) -> Any | None:
    """Remove or reject a follower to your server


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(handle=handle, client=client).parsed


async def asyncio_detailed(
    handle: str, *, client: AuthenticatedClient
) -> Response[Any]:
    """Remove or reject a follower to your server


    Args:
        handle (str): Parameter for handle.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(handle=handle)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
