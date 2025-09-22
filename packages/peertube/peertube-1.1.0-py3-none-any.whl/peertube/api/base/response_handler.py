from http import HTTPStatus
from typing import TypeVar

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response

T = TypeVar("T")


def handle_response(
    *,
    client: AuthenticatedClient | Client,
    response: httpx.Response,
    response_model: type[T] | None = None,
) -> T | None:
    """Generic response handler for API endpoints.

    Args:
        client: The HTTP client instance.
        response: The HTTP response.
        response_model: The model class to parse the response into, if any.

    Returns:
        Parsed response model or None.

    Raises:
        errors.UnexpectedStatus: If the status code is unexpected and client.raise_on_unexpected_status is True.
    """
    if response.status_code == 200:
        if response_model is not None:
            return response_model.from_dict(response.json())  # type: ignore[reportAttributeAccessIssue]
        else:
            return response.json()
    if response.status_code == 404:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def build_response(
    *,
    client: AuthenticatedClient | Client,
    response: httpx.Response,
    response_model: type[T] | None = None,
) -> Response[T]:
    """Build a Response object with parsed content.

    Args:
        client: The HTTP client instance.
        response: The HTTP response.
        response_model: The model class to parse the response into, if any.

    Returns:
        Response object with parsed content.
    """
    parsed = handle_response(
        client=client,
        response=response,
        response_model=response_model,
    )
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=parsed,
    )
