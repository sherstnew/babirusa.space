import pytest_asyncio
import pytest

from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport
from beanie import init_beanie, Document, UnionDoc
from motor.motor_asyncio import AsyncIOMotorClient

from app import MONGO_DSN_TEST
from app.main import app
from app.data.models import Teacher, Pupil


@pytest_asyncio.fixture
async def client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )
    
@pytest_asyncio.fixture(autouse=True)
async def initialize_beanie():
    client = AsyncIOMotorClient(MONGO_DSN_TEST, uuidRepresentation='standard')
    await init_beanie(
        database=client.get_default_database(),
        document_models=Document.__subclasses__() + UnionDoc.__subclasses__()
    )
    yield
    await Teacher.delete_all()
    await Pupil.delete_all()
    
@pytest_asyncio.fixture
async def test_teacher(client):
    teacher_data = {
        "login": "a",
        "password": "a"
    }
    await client.post("/api/teacher/create", json=teacher_data)
    return teacher_data
    
        
@pytest.mark.asyncio
async def test_ping(client):
        response = await client.get("/api/system/ping")
        assert response.status_code == 200
        
        data = response.json()
        assert data == "pong"
        
@pytest.mark.asyncio
async def test_login_success(client, test_teacher):
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

@pytest.mark.asyncio
async def test_create_pupil(client, test_teacher, monkeypatch):
    mock_docker = MagicMock()
    mock_container = MagicMock()
    mock_network = MagicMock()
    
    mock_docker.from_env.return_value = mock_docker
    mock_docker.containers.run.return_value = mock_container
    mock_container.id = "container123"
    mock_docker.networks.get.return_value = mock_network
    mock_network.attrs = {
        'Containers': {
            'container123': {
                'IPv4Address': '172.17.0.2/16'
            }
        }
    }
    
    monkeypatch.setattr("app.utils.security.verify_password", lambda x, y: True)
    
    with patch("app.routers.teacher.launch_codespace", new_callable=AsyncMock) as mock_launch:
        mock_launch.return_value = "172.17.0.2"
        
        login_response = await client.post(
            "/api/teacher/login",
            data={
                "username": test_teacher["login"],
                "password": test_teacher["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = login_response.json()["access_token"]
        
        pupil_data = {
            "username": "new_pupil",
            "password": "pupil_pass",
            "firstname": "John",
            "lastname": "Smith"
        }
        
        response = await client.post(
            "/api/teacher/pupils/new",
            json=pupil_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == pupil_data["username"]
        assert data["firstname"] == pupil_data["firstname"]

        teacher = await Teacher.find_one(
            Teacher.login == test_teacher["login"], 
            fetch_links=True
        )
        assert len(teacher.pupils) == 1
        assert teacher.pupils[0].username == pupil_data["username"]
        
        mock_launch.assert_awaited_once_with(
            pupil_data["username"],
            pupil_data["password"]
        )
        
