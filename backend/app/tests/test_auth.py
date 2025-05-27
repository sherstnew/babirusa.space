import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login(client, test_teacher):
    form_data = {
        "username": test_teacher["login"],
        "password": test_teacher["password"]
    }
    
    response = await client.post(
        "/api/teacher/login",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50