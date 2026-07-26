import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.log = MagicMock()
    context.request = MagicMock()
    context.add_requests = AsyncMock()
    context.http_response = MagicMock()
    context.http_response.status_code = 200
    mock_context._page = None
    return context


@pytest.fixture
def mock_session_factory():
    session = AsyncMock()
    session.add = MagicMock()
    session.get_bind = MagicMock()

    factory = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock()
        )
    )
    return factory, session
