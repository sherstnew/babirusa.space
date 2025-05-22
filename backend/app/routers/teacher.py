from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from app.data.models import Teacher, Pupil, Group
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password, get_current_user
from app.utils.codespaces import launch_codespace

from typing import Annotated

import uuid

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.post("/create")
async def registration_teacher(request: schemas.RequestTeacher) -> schemas.UserLogIn:
    
    await create_user(request)
    
    token_expires = timedelta(minutes=1440)
    token = await authenticate_user(data={"sub": request.login}, expires_delta=token_expires)
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
async def create_pupil(request: schemas.PupilCreate, 
                       _: Teacher = Depends(get_current_user)) -> schemas.Pupil:
    pupil = Pupil(
        username=request.username,
        firstname=request.firstname,
        lastname=request.lastname,
        groups=None
    )
    await pupil.create()
    
    await launch_codespace(pupil.username, request.password)
    
    return schemas.Pupil(
        id=str(pupil.id),
        username=pupil.username,
        firstname=pupil.firstname,
        lastname=pupil.lastname,
        groups=pupil.groups
    )
    
@router.delete("/pupils/{pupil_id}")
async def delete_pupil(pupil_id: str,
                       _: Teacher = Depends(get_current_user)) -> str:
    pupil = await Pupil.find_one(Pupil.id == uuid.UUID(pupil_id), fetch_links=True)
    if not pupil:
        raise Error.PUPIL_NOT_FOUND_EXCEPTION
    
    await pupil.delete()
    
    return "OK"

@router.post("/groups/new")
async def create_group(group_name: Annotated[str, Header()],
                       current_teacher: Teacher = Depends(get_current_user)) -> schemas.Group:
    existing_group = await Group.find_one(Group.name == group_name)
    if existing_group:
        return Error.GROUP_EXISTS
    
    group = Group(
        name=group_name,
        teacher=current_teacher.dict(),
        pupils=None
    )
    await group.insert()
    
    return schemas.Group(
        id=str(group.id),
        name=group.name,
        pupils=group.pupils
    )

@router.get("/groups")
async def get_teacher_groups(current_teacher: Teacher = Depends(get_current_user)):
    groups = await Group.find(Group.teacher.id == current_teacher.id, fetch_links=True).to_list()
    
    return [schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=group.teacher,
        pupils=group.pupils
    )
        for group in groups
    ]
    

