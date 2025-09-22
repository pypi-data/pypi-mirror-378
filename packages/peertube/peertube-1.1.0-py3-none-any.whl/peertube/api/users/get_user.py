from typing import Any

import httpx

from peertube.api.shared_utils import build_response, parse_response
from peertube.client import AuthenticatedClient, Client
from peertube.types import UNSET, Response, Unset


def _get_kwargs(id: int, *, with_stats: Unset | bool = UNSET) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["withStats"] = with_stats
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/users/{id}",
        "params": params,
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
    id: int, *, client: AuthenticatedClient, with_stats: Unset | bool = UNSET
) -> Response[Any]:
    """Get a user


    Args:
        id (int):  Example: 42.
        with_stats (Union[Unset, bool]): Parameter for with stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(id=id, with_stats=with_stats)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    id: int, *, client: AuthenticatedClient, with_stats: Unset | bool = UNSET
) -> Any | None:
    """Get a user


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(id=id, client=client, with_stats=with_stats).parsed


async def asyncio_detailed(
    id: int, *, client: AuthenticatedClient, with_stats: Unset | bool = UNSET
) -> Response[Any]:
    """Get a user


    Args:
        id (int):  Example: 42.
        with_stats (Union[Unset, bool]): Parameter for with stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(id=id, with_stats=with_stats)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
