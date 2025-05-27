import pytest
from httpx import AsyncClient

from app.data.models import Group

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

    
@pytest.mark.asyncio
async def test_delete_groups(client, test_teacher):
    login_res = await client.post(
        "/api/teacher/login",
        data={"username": test_teacher["login"], "password": test_teacher["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]

    name1 = "Group Name1"
    name2 = "Group Name2"
    create_res1 = await client.post(
        "/api/teacher/groups/new",
        json=name1,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    create_res2 = await client.post(
        "/api/teacher/groups/new",
        json=name2,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = await client.delete(
        "/api/teacher/groups",
        params={"groups_id": [str(create_res1.json()["id"]), str(create_res2.json()["id"])]},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.text == '"OK"'

    assert await Group.find_one(Group.id == create_res1.json()["id"]) is None
    assert await Group.find_one(Group.id == create_res2.json()["id"]) is None
    