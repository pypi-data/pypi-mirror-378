import io

import httpx
import pytest

from peertube.client import AuthenticatedClient, Client
from peertube.types import File, Unset


@pytest.fixture
def base_url():
    """Base URL for test instances"""
    return "https://test.peertube.example"


@pytest.fixture
def test_token():
    """Test authentication token"""
    return "test_auth_token_123"


@pytest.fixture
def client(base_url):
    """Basic Client instance for testing"""
    return Client(base_url=base_url)


@pytest.fixture
def auth_client(base_url, test_token):
    """AuthenticatedClient instance for testing"""
    return AuthenticatedClient(base_url=base_url, token=test_token)


@pytest.fixture
def sample_headers():
    """Sample headers for testing"""
    return {"User-Agent": "test-agent", "Accept": "application/json"}


@pytest.fixture
def sample_cookies():
    """Sample cookies for testing"""
    return {"session": "abc123", "prefs": "dark_mode"}


@pytest.fixture
def timeout_config():
    """Sample timeout configuration for testing"""
    return httpx.Timeout(10.0)


@pytest.fixture
def mock_httpx_client(mocker):
    """Mock httpx.Client for testing"""
    return mocker.Mock(spec=httpx.Client)


@pytest.fixture
def mock_async_httpx_client(mocker):
    """Mock httpx.AsyncClient for testing"""
    return mocker.Mock(spec=httpx.AsyncClient)


@pytest.fixture
def sample_file():
    """Sample File object for testing"""
    return File(payload=io.BytesIO(b"test content"), file_name="test.txt")


@pytest.fixture
def unset_instance():
    """Unset instance for testing"""
    return Unset()


@pytest.fixture
def unexpected_status_args():
    """Arguments for UnexpectedStatus exception testing"""
    return {"status_code": 400, "content": b"Bad Request"}
