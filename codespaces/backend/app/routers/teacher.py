from fastapi import APIRouter, Depends

from app.data.models import Teacher, Pupil
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password, get_current_user

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
async def log_in_teacher(request: schemas.RequestLogInUser) -> schemas.UserLogIn:
    user = await Teacher.find_one(Teacher.login == request.login)
    if not user or not verify_password(request.password, user.hashed_password):
        return Error.UNAUTHORIZED_INVALID
    
    token = await authenticate_user(data={"sub": request.login})
    
    return schemas.UserLogIn(
        teacher_token=str(token)
    )
    
@router.post("/pupils/new")
# async def create_pupil(current_user: str = Depends(get_current_user)):
async def create_pupil(request: schemas.PupilCreate) -> schemas.Pupil:
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

