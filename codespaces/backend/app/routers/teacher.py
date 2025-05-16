from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from app.data.models import Teacher, Pupil
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password, get_current_user

from typing import Annotated

import jwt

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.post("/create")
async def registration_teacher(request: schemas.Teacher) -> schemas.UserLogIn:
    
    await create_user(request)
    token = await authenticate_user(data={"sub": request.login})
    print(token)
    return schemas.UserLogIn(
        teacher_token=str(token)
    )
    
@router.post("/login")
async def log_in_teacher(request: Annotated[OAuth2PasswordRequestForm, Depends()]) -> schemas.Token:
    user = await Teacher.find_one(Teacher.login == request.username)
    if not user or not verify_password(request.password, user.hashed_password):
        return Error.UNAUTHORIZED_INVALID
    
    token_expires = timedelta(minutes=1440)
    token = await authenticate_user(data={"sub": request.username}, expires_delta=token_expires)

    return schemas.Token(access_token=token, token_type="bearer")
    
@router.post("/pupils/new")
# async def create_pupil(current_user: str = Depends(get_current_user)):
async def create_pupil(request: schemas.PupilCreate, _: Teacher = Depends(get_current_user)) -> schemas.Pupil:
    pupil = Pupil(
        firstname=request.firstname,
        lastname=request.lastname,
        groups=None
    )
    await pupil.create()
    
    return schemas.Pupil(
        id=str(pupil.id),
        firstname=pupil.firstname,
        lastname=pupil.lastname,
        groups=pupil.groups
    )
    
@router.delete("/pupils/{pupil_id}")
# async def create_pupil(current_user: str = Depends(get_current_user)):
async def delete_pupil(pupil_id: str) -> schemas.Pupil:
    pupil = await Pupil.find_one(Pupil.id == pupil_id)
    if not pupil:
        return Error.PUPIL_NOT_FOUND_EXCEPTION
    
    await pupil.delete()
    
    return "OK"

