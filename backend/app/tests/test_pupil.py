import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.data.models import Teacher, UserIp

import uuid

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
    
    with patch("app.routers.pupil.launch_codespace", new_callable=AsyncMock) as mock_launch:
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
        
        userip = UserIp(
            username=pupil_data["username"],
            ip="123",
            container_id="123"
        )
        await userip.create()

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
async def test_add_pupil_to_group(client, test_teacher):
    global pupil_id
    
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]
    
    
    create_res = await client.post(
        "/api/teacher/groups/new",
        json="Group Test",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    group_id = create_res.json()["id"]

    request_data = {
        "group_id": str(group_id),
        "pupil_id": [str(pupil_id)]
    }
    
    response = await client.post(
        "/api/teacher/groups/pupils",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["id"] == str(group_id)
    assert len(response_data["pupils"]) == 1
    assert {p["id"] for p in response_data["pupils"]} == {str(pupil_id)}
    
@pytest.mark.asyncio
async def test_remove_pupils_from_group(client, test_teacher):
    global pupil_id
    
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]
    
    create_res = await client.post(
        "/api/teacher/groups/new",
        json="Group Test",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    group_id = create_res.json()["id"]

    request_data = {
        "group_id": str(group_id),
        "pupil_id": [str(pupil_id)]
    }
    
    add_res = await client.post(
        "/api/teacher/groups/pupils",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert add_res.status_code == 200
    
    response = await client.delete(
        "/api/teacher/groups/pupils",
        params={ 
            "group_id": str(group_id),
            "pupil_id": [str(pupil_id)]
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["id"] == str(group_id)
    assert len(response_data["pupils"]) == 0
    
@pytest.mark.asyncio
async def test_delete_pupil(client, test_teacher, mocker):
    global pupil_id
    
    login_response = await client.post(
            "/api/teacher/login",
            data={
                "username": test_teacher["login"],
                "password": test_teacher["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    token = login_response.json()["access_token"]
    
    mock_docker = mocker.patch('docker.from_env')
    mock_container = mocker.MagicMock()
    mock_docker.return_value.containers.get.return_value = mock_container
    
    mock_os = mocker.patch('os.listdir')
    mock_os.return_value = []

    delete_response = await client.delete(
        f"/api/teacher/pupils/{pupil_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert delete_response.status_code == 200
    assert delete_response.text == '"OK"'
    
    mock_docker.return_value.containers.get.assert_called_once()
    mock_container.remove.assert_called_once_with(force=True, v=True)
    await UserIp.delete_all()
    
    get_response = await client.delete(
        f"/api/teacher/pupils/{pupil_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404