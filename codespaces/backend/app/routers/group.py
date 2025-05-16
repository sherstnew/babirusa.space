from fastapi import APIRouter

from app.data.models import Teacher
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password

router = APIRouter(prefix='/groups', tags=["Groups"])

@router.post("/")
async def create_group():
    pass
    
@router.post("/new")
async def create_group():
    pass
