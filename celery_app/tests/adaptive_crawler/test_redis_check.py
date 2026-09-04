import asyncio

import pytest
from tools.adaptive_crawler.helpers import check_redis_connection


def test_check_redis_connection_failure():
    invalid_url = "redis://127.0.0.1:9999"

    async def _run():
        with pytest.raises(RuntimeError) as exc_info:
            await check_redis_connection(invalid_url)
        assert "Cannot connect to Redis at redis://127.0.0.1:9999" in str(
            exc_info.value
        )

    asyncio.run(_run())
