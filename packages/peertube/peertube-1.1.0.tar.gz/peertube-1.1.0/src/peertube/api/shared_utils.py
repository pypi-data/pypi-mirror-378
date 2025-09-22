"""Shared utilities for API client functions."""

from http import HTTPStatus
from typing import Any

import httpx

from peertube import errors
from peertube.client import AuthenticatedClient, Client
from peertube.types import Response


def build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    """Build a Response object from httpx response."""
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=parse_response(client=client, response=response),
    )


def parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    """Parse response, raising error if configured."""
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None
