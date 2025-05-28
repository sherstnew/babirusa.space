from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from app.data.models import Teacher
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password

from typing import Annotated

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.post("/create")
async def registration_teacher(request: schemas.RequestTeacher) -> schemas.UserLogIn:
    
    await create_user(request)
    
    token_expires = timedelta(minutes=1440)
    token = await authenticate_user(data={"sub": request.login}, expires_delta=token_expires)
    return schemas.UserLogIn(
        teacher_token=str(token)
    )
    
@router.post("/login")
async def log_in_teacher(request: Annotated[OAuth2PasswordRequestForm, Depends()]) -> schemas.Token:
    user = await Teacher.find_one(Teacher.login == request.username)
    if not user or not verify_password(request.password, user.hashed_password):
        raise Error.UNAUTHORIZED_INVALID
    
    token_expires = timedelta(minutes=1440)
    token = await authenticate_user(data={"sub": request.username}, expires_delta=token_expires)

    return schemas.Token(access_token=token, token_type="bearer")