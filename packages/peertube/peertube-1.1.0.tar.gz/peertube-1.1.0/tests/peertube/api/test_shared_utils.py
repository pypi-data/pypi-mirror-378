"""Tests for peertube.api.shared_utils module"""

import httpx
import pytest

from peertube.api.shared_utils import build_response, parse_response
from peertube.errors import UnexpectedStatus


class TestSharedUtils:
    """Test cases for peertube API shared utilities"""

    def test_build_response_returns_response_object(self, client, httpx_mock):
        """Test build_response returns Response object"""
        httpx_mock.add_response(
            method="GET",
            url="https://test.example/api",
            json={"key": "value"},
            status_code=200,
        )

        with httpx.Client() as http_client:
            response = http_client.get("https://test.example/api")
            result = build_response(client=client, response=response)
            assert hasattr(result, "status_code")
            assert hasattr(result, "content")
            assert hasattr(result, "headers")
            assert hasattr(result, "parsed")

    def test_parse_response_returns_none_when_no_raise(self, client, mocker):
        """Test parse_response returns None when raise_on_unexpected_status is False"""
        mock_response = mocker.Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b"response content"

        # Mock client to not raise on unexpected status
        mocker.patch.object(client, "raise_on_unexpected_status", new=False)

        result = parse_response(client=client, response=mock_response)
        assert result is None

    def test_parse_response_raises_when_configured(self, client, mocker):
        """Test parse_response raises UnexpectedStatus when configured"""
        mock_response = mocker.Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.content = b"Bad Request"

        # Mock client to raise on unexpected status
        mocker.patch.object(client, "raise_on_unexpected_status", new=True)

        with pytest.raises(UnexpectedStatus):
            parse_response(client=client, response=mock_response)
