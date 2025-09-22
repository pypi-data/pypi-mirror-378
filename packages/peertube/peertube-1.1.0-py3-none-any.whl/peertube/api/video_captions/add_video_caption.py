from typing import Any
from uuid import UUID

import httpx

from peertube import errors
from peertube.api.shared_utils import build_response
from peertube.client import AuthenticatedClient, Client
from peertube.models.add_video_caption_body import AddVideoCaptionBody
from peertube.types import Response


def _get_kwargs(
    id: UUID | int | str, caption_language: str, *, body: AddVideoCaptionBody
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/videos/{id}/captions/{caption_language}",
    }
    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
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


def sync_detailed(
    id: UUID | int | str,
    caption_language: str,
    *,
    client: AuthenticatedClient,
    body: AddVideoCaptionBody,
) -> Response[Any]:
    """Add or replace a video caption


    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        caption_language (str): language id of the video (see
            [/videos/languages](#operation/getLanguages)) Example: en.
        body (AddVideoCaptionBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(id=id, caption_language=caption_language, body=body)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    id: UUID | int | str,
    caption_language: str,
    *,
    client: AuthenticatedClient,
    body: AddVideoCaptionBody,
) -> Any | None:
    """Add or replace a video caption


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(
        id=id, caption_language=caption_language, client=client, body=body
    ).parsed


async def asyncio_detailed(
    id: UUID | int | str,
    caption_language: str,
    *,
    client: AuthenticatedClient,
    body: AddVideoCaptionBody,
) -> Response[Any]:
    """Add or replace a video caption


    Args:
        id (Union[UUID, int, str]): Unique identifier for the entity.
        caption_language (str): language id of the video (see
            [/videos/languages](#operation/getLanguages)) Example: en.
        body (AddVideoCaptionBody): Request body data.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(id=id, caption_language=caption_language, body=body)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
