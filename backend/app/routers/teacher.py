from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from app.data.models import Teacher
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password

from typing import Annotated
from typing import List
import uuid
from app import ADMIN_PANEL_PASSWORD
from fastapi import status

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


@router.get("")
async def get_all_teachers(x_admin_password: Annotated[str, Header()] ) -> List[schemas.Teacher_]:
    if not ADMIN_PANEL_PASSWORD or x_admin_password != ADMIN_PANEL_PASSWORD:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    teachers = await Teacher.find_all(fetch_links=True).to_list()
    return [schemas.Teacher_(
        id=str(t.id),
        login=t.login,
        hashed_password=t.hashed_password,
        pupils=None if not t.pupils else [
            schemas.Pupil_(
                id=str(p.id),
                username=p.username,
                firstname=p.firstname,
                lastname=p.lastname,
                container_status=p.container_status
            ) for p in t.pupils
        ]
    ) for t in teachers]


@router.delete("/{teacher_id}")
async def delete_teacher(teacher_id: str, x_admin_password: Annotated[str, Header()]) -> str:
    if not ADMIN_PANEL_PASSWORD or x_admin_password != ADMIN_PANEL_PASSWORD:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    teacher = await Teacher.find_one(Teacher.id == uuid.UUID(teacher_id), fetch_links=True)
    if not teacher:
        raise Error.TEACHER_NOT_FOUND_EXCEPTION

    await teacher.delete()
    return "OK"