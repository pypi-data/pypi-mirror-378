from typing import Any

import httpx

from peertube.api.shared_utils import build_response, parse_response
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_users_sort import GetUsersSort
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: Unset | str = UNSET,
    blocked: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetUsersSort = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["blocked"] = blocked

    params["start"] = start

    params["count"] = count
    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/users",
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
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    blocked: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetUsersSort = UNSET,
) -> Response[Any]:
    """List users


    Args:
        search (Union[Unset, str]): Search query filter.
        blocked (Union[Unset, bool]): Parameter for blocked.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetUsersSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search, blocked=blocked, start=start, count=count, sort=sort
    )

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    blocked: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetUsersSort = UNSET,
) -> Any | None:
    """List users


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(
        client=client,
        search=search,
        blocked=blocked,
        start=start,
        count=count,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    search: Unset | str = UNSET,
    blocked: Unset | bool = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetUsersSort = UNSET,
) -> Response[Any]:
    """List users


    Args:
        search (Union[Unset, str]): Search query filter.
        blocked (Union[Unset, bool]): Parameter for blocked.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetUsersSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        search=search, blocked=blocked, start=start, count=count, sort=sort
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
