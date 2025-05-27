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