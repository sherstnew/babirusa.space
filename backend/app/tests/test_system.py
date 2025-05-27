import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ping(client):
    response = await client.get("/api/system/ping")
    assert response.status_code == 200
    assert response.json() == "pong"