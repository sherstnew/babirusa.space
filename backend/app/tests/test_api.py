import pytest_asyncio
import pytest

from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport
from beanie import init_beanie, Document, UnionDoc
from motor.motor_asyncio import AsyncIOMotorClient

from app import MONGO_DSN_TEST
from app.main import app
from app.data.models import Teacher, Group


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
    await Group.delete_all()
    
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
    global pupil_id
    
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
        pupil_id = data["id"]
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

@pytest.mark.asyncio
async def test_create_group(client, test_teacher):
    login_response = await client.post(
            "/api/teacher/login",
            data={
                "username": test_teacher["login"],
                "password": test_teacher["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    token = login_response.json()["access_token"]
    
    group_data = "Test Group"

    response = await client.post(
        "/api/teacher/groups/new",
        json=group_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    response_data = response.json()
    print(response_data['id'])
    assert response_data["name"] == "Test Group"
    assert response_data["teacher"]["login"] == test_teacher["login"]
    assert response_data["pupils"] == []
    
@pytest.mark.asyncio
async def test_get_teacher_groups(client, test_teacher):
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]

    await client.post(
        "/api/teacher/groups/new",
        json= "Group B",
        headers={"Authorization": f"Bearer {token}"}
    )
    await client.post(
        "/api/teacher/groups/new",
        json= "Group A",
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        "/api/teacher/groups",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    groups = response.json()
    
    assert isinstance(groups, list)
    assert len(groups) == 2 

    group_names = {group["name"] for group in groups}
    assert group_names == {"Group A", "Group B"}

    unauth_response = await client.get("/api/teacher/groups")
    assert unauth_response.status_code in (401, 403)
    
    
@pytest.mark.asyncio
async def test_get_pupil_password(client, test_teacher):
    global pupil_id

    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]  

    response = await client.get(
        f"/api/teacher/pupils/{pupil_id}/password",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_get_pupils_all(client, test_teacher):
    global pupil_id
    
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]

    response = await client.get(
        "/api/teacher/pupils",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    pupils = response.json()
    assert isinstance(pupils, list)
    
@pytest.mark.asyncio
async def test_update_group_name(client, test_teacher):
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]

    original_name = "Original Group Name"
    create_res = await client.post(
        "/api/teacher/groups/new",
        json=original_name,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    group_id = create_res.json()["id"]

    new_name = "Updated Group Name"
    update_res = await client.patch(
        "/api/teacher/groups",
        json={
            "group_id": group_id,
            "new_group_name": new_name
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert update_res.status_code == 200

    get_res = await client.get(
        "/api/teacher/groups",
        headers={"Authorization": f"Bearer {token}"}
    )
    groups = get_res.json()
    assert any(g["name"] == new_name for g in groups)
    assert not any(g["name"] == original_name for g in groups)

    
#last
@pytest.mark.asyncio
async def test_delete_pupil(client, test_teacher):
    global pupil_id
    
    login_response = await client.post(
            "/api/teacher/login",
            data={
                "username": test_teacher["login"],
                "password": test_teacher["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    print(pupil_id)
    token = login_response.json()["access_token"]
    delete_response = await client.delete(
        f"/api/teacher/pupils/{pupil_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert delete_response.status_code == 200
    assert delete_response.text == '"OK"'
    get_response = await client.delete(
        f"/api/teacher/pupils/{pupil_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404