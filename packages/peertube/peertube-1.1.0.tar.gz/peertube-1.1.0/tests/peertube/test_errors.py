"""Tests for peertube.errors module"""

import pytest

from peertube.errors import UnexpectedStatus


class TestErrors:
    """Test cases for peertube error handling"""

    @pytest.mark.parametrize(
        ("status_code", "content"),
        [
            (400, b"Bad Request"),
            (401, b"Unauthorized"),
            (404, b"Not Found"),
            (500, b"Internal Server Error"),
        ],
        ids=["bad_request", "unauthorized", "not_found", "internal_error"],
    )
    def test_unexpected_status_init_sets_attributes(self, status_code, content):
        """Test that UnexpectedStatus stores status_code and content correctly"""
        exception = UnexpectedStatus(status_code, content)
        assert exception.status_code == status_code
        assert exception.content == content
