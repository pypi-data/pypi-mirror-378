"""Tests for peertube.types module"""

import io

import pytest

from peertube.types import File


class TestTypes:
    """Test cases for peertube type utilities"""

    def test_unset_bool_returns_false(self, unset_instance):
        """Test that Unset.__bool__() always returns False"""
        result = bool(unset_instance)
        assert result is False

    @pytest.mark.parametrize(
        ("payload", "file_name", "mime_type"),
        [
            (b"test content", "test.txt", "text/plain"),
            (b"binary data", "image.png", "image/png"),
            (b"", "empty.txt", None),
        ],
        ids=["text_file", "binary_file", "empty_file"],
    )
    def test_file_to_tuple_returns_correct_format(self, payload, file_name, mime_type):
        """Test that File.to_tuple() returns the correct httpx-compatible format"""
        file_obj = File(
            payload=io.BytesIO(payload), file_name=file_name, mime_type=mime_type
        )
        result = file_obj.to_tuple()
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == file_name  # filename
        assert hasattr(result[1], "read")  # file-like object
        assert result[2] == mime_type  # mime_type
