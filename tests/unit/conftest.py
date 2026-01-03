from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_asyncio_sleep():
    """Mock asyncio.sleep to speed up async tests."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        yield
