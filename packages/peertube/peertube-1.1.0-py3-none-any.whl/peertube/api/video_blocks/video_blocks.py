from typing import Any

import httpx

from peertube.api.shared_utils import build_response, parse_response
from peertube.client import AuthenticatedClient, Client
from peertube.models.get_video_blocks_sort import GetVideoBlocksSort
from peertube.models.get_video_blocks_type import GetVideoBlocksType
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: Unset | GetVideoBlocksType = UNSET,
    search: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoBlocksSort = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_type_: Unset | int = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params["search"] = search

    params["start"] = start

    params["count"] = count
    json_sort: Unset | str = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/videos/blacklist",
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
    type_: Unset | GetVideoBlocksType = UNSET,
    search: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoBlocksSort = UNSET,
) -> Response[Any]:
    """List video blocks


    Args:
        type_ (Union[Unset, GetVideoBlocksType]): Parameter for type (underscore avoids keyword conflict).
        search (Union[Unset, str]): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoBlocksSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        type_=type_, search=search, start=start, count=count, sort=sort
    )

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    type_: Unset | GetVideoBlocksType = UNSET,
    search: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoBlocksSort = UNSET,
) -> Any | None:
    """List video blocks


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(
        client=client, type_=type_, search=search, start=start, count=count, sort=sort
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    type_: Unset | GetVideoBlocksType = UNSET,
    search: Unset | str = UNSET,
    start: Unset | int = UNSET,
    count: Unset | int = 15,
    sort: Unset | GetVideoBlocksSort = UNSET,
) -> Response[Any]:
    """List video blocks


    Args:
        type_ (Union[Unset, GetVideoBlocksType]): Parameter for type (underscore avoids keyword conflict).
        search (Union[Unset, str]): Search query filter.
        start (Union[Unset, int]): Starting index for pagination.
        count (Union[Unset, int]):  Default: 15.
        sort (Union[Unset, GetVideoBlocksSort]): Sorting criteria for results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        type_=type_, search=search, start=start, count=count, sort=sort
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
