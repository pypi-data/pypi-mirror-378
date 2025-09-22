from typing import Any

import httpx

from peertube import errors
from peertube.api.shared_utils import build_response
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response


def _get_kwargs(account_name: str, list_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/watched-words/accounts/{account_name}/lists/{list_id}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 204:
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
    account_name: str, list_id: str, *, client: AuthenticatedClient
) -> Response[Any]:
    """Delete account watched words

     **PeerTube > = 6.2**
    Args:
        account_name (str): Parameter for account name.
        list_id (str): Parameter for list id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(account_name=account_name, list_id=list_id)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(account_name: str, list_id: str, *, client: AuthenticatedClient) -> Any | None:
    """Delete account watched words


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any
    """

    return sync_detailed(
        account_name=account_name, list_id=list_id, client=client
    ).parsed


async def asyncio_detailed(
    account_name: str, list_id: str, *, client: AuthenticatedClient
) -> Response[Any]:
    """Delete account watched words

     **PeerTube > = 6.2**
    Args:
        account_name (str): Parameter for account name.
        list_id (str): Parameter for list id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(account_name=account_name, list_id=list_id)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
