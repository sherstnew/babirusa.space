from fastapi import APIRouter, Depends, Path
from cryptography.fernet import Fernet

from app import SECRET_KEY_USER
from app.data.models import Teacher, Pupil, UserIp
from app.data import schemas
from app.utils.error import Error
from app.utils.security import get_current_user
from app.utils.codespaces import launch_codespace, check_container_status

from typing import Annotated, List

import uuid
import docker
import os

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



router = APIRouter(prefix="/teacher/pupils", tags=["Pupils"])

cipher = Fernet(SECRET_KEY_USER)

@router.post("/new")
async def teacher_create_pupil(request: schemas.PupilCreate, 
                       current_teacher: Teacher = Depends(get_current_user)) -> schemas.Pupil_:
    pupil_exists = await Pupil.find_one(Pupil.username == request.username)
    if pupil_exists:
        raise Error.LOGIN_EXISTS
    
    hashed_password = cipher.encrypt(request.password.encode('utf-8')).decode('utf-8')
    pupil = Pupil(
        username=request.username,
        firstname=request.firstname,
        lastname=request.lastname,
        hashed_password=hashed_password,
        container_status="running" 
    )
    
    await pupil.create()

    if current_teacher.pupils is None:
        current_teacher.pupils = []
    current_teacher.pupils.append(pupil)
    await current_teacher.save()
    
    await launch_codespace(pupil.username, request.password)
    
    return schemas.Pupil_(
        id=str(pupil.id),
        username=pupil.username,
        firstname=pupil.firstname,
        lastname=pupil.lastname,
        container_status=pupil.container_status
    )
    
    
@router.post('/{username}/codespace')
async def conteiner(username: str, start: bool) -> str:
    userip = await UserIp.find_one(UserIp.username == username)
    if not userip:
        raise Error.PUPIL_NOT_FOUND
    
    client = docker.from_env()
    container = client.containers.get(userip.container_id)
    if start:
        container.start()
    else:
        conteiner.stop()
    
    return "OK"
    
    
@router.get("/{pupil_id}/password")
async def teacher_get_pupil_passwor(pupil_id: Annotated[str, Path()], 
                       _: Teacher = Depends(get_current_user)) -> schemas.PupilPassword:
    pupil = await Pupil.find_one(Pupil.id == uuid.UUID(pupil_id))
    if not pupil:
        raise Error.PUPIL_NOT_FOUND
    
    decrypted_password = cipher.decrypt(pupil.hashed_password.encode('utf-8')).decode('utf-8')
    
    return schemas.PupilPassword(
        password=decrypted_password
    )
    
@router.get("")
async def teacher_get_pupil_all(current_teacher: Teacher = Depends(get_current_user)) -> List[schemas.Pupil_]:
    print(current_teacher.pupils, flush=True)
    logger.info(current_teacher.pupils, "pupils")
    await check_container_status(current_teacher.pupils)
    
    return [schemas.Pupil_(
        id=str(pupil.id),
        username=pupil.username,
        firstname=pupil.firstname,
        lastname=pupil.lastname,
        container_status=pupil.container_status
    )
        for pupil in current_teacher.pupils   
    ]
    
@router.delete("/{pupil_id}")
async def delete_pupil(pupil_id: Annotated[str, Path()],
                       _: Teacher = Depends(get_current_user)) -> str:
    pupil = await Pupil.find_one(Pupil.id == uuid.UUID(pupil_id), fetch_links=True)
    if not pupil:
        raise Error.PUPIL_NOT_FOUND
    await pupil.delete()
    
    userip = await UserIp.find_one(UserIp.username == pupil.username)
    if not userip:
        raise Error.USER_IP_NOT_FOUND
    
    client = docker.from_env()
    container = client.containers.get(userip.container_id)
    container.remove(force=True, v=True)
    
    # for file in os.listdir("/babirusa"):
    #     if file == f"user-{pupil.username}-prj":
    #         os.remove(f"/babirusa/user-{pupil.username}-prj")
    #     if file == f"user-{pupil.username}-config":
    #         os.remove(f"/babirusa/user-{pupil.username}-config")
        
    return "OK"