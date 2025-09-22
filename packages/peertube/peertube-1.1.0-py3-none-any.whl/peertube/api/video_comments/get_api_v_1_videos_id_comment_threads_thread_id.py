from typing import Any
from uuid import UUID

import httpx

from peertube.api.shared_utils import build_response, parse_response
from peertube.client import AuthenticatedClient, Client
from peertube.types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID | int | str,
    thread_id: int,
    *,
    x_peertube_video_password: Unset | str = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_peertube_video_password, Unset):
        headers["x-peertube-video-password"] = x_peertube_video_password
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/videos/{id}/comment-threads/{thread_id}",
    }

    _kwargs["headers"] = headers
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
    id: UUID | int | str,
    thread_id: int,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any]:
    """Get a thread


    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        thread_id (int): Parameter for thread id.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id, thread_id=thread_id, x_peertube_video_password=x_peertube_video_password
    )

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    thread_id: int,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> Any | None:
    """Get a thread


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(
        id=id,
        thread_id=thread_id,
        client=client,
        x_peertube_video_password=x_peertube_video_password,
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    thread_id: int,
    *,
    client: AuthenticatedClient | Client,
    x_peertube_video_password: Unset | str = UNSET,
) -> Response[Any]:
    """Get a thread


    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        thread_id (int): Parameter for thread id.
        x_peertube_video_password (Union[Unset, str]): Video-related parameter.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id, thread_id=thread_id, x_peertube_video_password=x_peertube_video_password
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
