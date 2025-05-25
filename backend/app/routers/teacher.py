from fastapi import APIRouter, Depends, Body, Path
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from app.data.models import Teacher, Pupil, Group
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user, create_pupil
from app.utils.security import verify_password, get_current_user
from app.utils.codespaces import launch_codespace

from typing import Annotated, List

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
        raise Error.UNAUTHORIZED_INVALID
    
    token_expires = timedelta(minutes=1440)
    token = await authenticate_user(data={"sub": request.username}, expires_delta=token_expires)

    return schemas.Token(access_token=token, token_type="bearer")
    
@router.post("/pupils/new")
async def teacher_create_pupil(request: schemas.PupilCreate, 
                       current_teacher: Teacher = Depends(get_current_user)) -> schemas.Pupil_:
    
    pupil = await create_pupil(request)

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
        # groups=pupil.groups
    )
    
@router.delete("/pupils/{pupil_id}")
async def delete_pupil(pupil_id: Annotated[str, Path()],
                       _: Teacher = Depends(get_current_user)) -> str:
    pupil = await Pupil.find_one(Pupil.id == uuid.UUID(pupil_id), fetch_links=True)
    if not pupil:
        raise Error.PUPIL_NOT_FOUND_EXCEPTION
    
    await pupil.delete()
    
    return "OK"

@router.post("/groups/new")
async def create_group(group_name: Annotated[str, Body()],
                       current_teacher: Teacher = Depends(get_current_user)) -> schemas.Group:
    existing_group = await Group.find_one(Group.name == group_name)
    if existing_group:
        raise Error.GROUP_EXISTS
    
    group = Group(
        name=group_name,
        teacher=current_teacher,
        pupils=None
    )
    await group.insert()
    
    return schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=schemas.Teacher_(
            id=str(group.teacher.id),
            login=group.teacher.login,
            hashed_password=group.teacher.hashed_password,
            pupils=[schemas.Pupil_(
                id=str(pupil.id),
                username=pupil.username,
                firstname=pupil.firstname,
                lastname=pupil.lastname
        )
            for pupil in current_teacher.pupils
        ]
            ),
        pupils=[]
    )

@router.get("/groups")
async def get_teacher_groups(current_teacher: Teacher = Depends(get_current_user)) -> List[schemas.Group]:
    groups = await Group.find(Group.teacher.id == current_teacher.id, fetch_links=True).to_list()
    
    return [schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=schemas.Teacher_(
            id=str(group.teacher.id),
            login=group.teacher.login,
            hashed_password=group.teacher.hashed_password,
            pupils=[schemas.Pupil_(
                id=str(pupil.id),
                username=pupil.username,
                firstname=pupil.firstname,
                lastname=pupil.lastname
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname
        )
            for pupil in group.pupils   
        ]
    )
        for group in groups
    ]
    
@router.patch("/groups")
async def update_teacher_group(request: schemas.UpdateGroup,
                               _: Teacher = Depends(get_current_user)) -> schemas.Group:
    group = await Group.find_one(Group.id == uuid.UUID(request.group_id), fetch_links=True)
    if not group:
        raise Error.GROUP_NOT_FOUND
    
    group.name = request.new_group_name
    
    await group.save()
    
    return schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=schemas.Teacher_(
            id=str(group.teacher.id),
            login=group.teacher.login,
            hashed_password=group.teacher.hashed_password,
            pupils=[schemas.Pupil_(
                id=str(pupil.id),
                username=pupil.username,
                firstname=pupil.firstname,
                lastname=pupil.lastname
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname
        )
            for pupil in group.pupils   
        ]
    )
    
@router.delete("/groups")
async def delete_teacher_groups(groups_id: Annotated[List[str], Body()],
                               _: Teacher = Depends(get_current_user)) -> str:
    
    groups = await Group.find({ "_id": { "$in": [uuid.UUID(id) for id in groups_id] }}, fetch_links=True).to_list()
    if not groups:
        raise Error.GROUP_NOT_FOUND

    for group in groups:  
        await group.delete()
    
    return "OK"
    
@router.post("/groups/pupils")
async def add_pupil_in_group(request: schemas.AddPupil, _: Teacher = Depends(get_current_user)) -> schemas.Group:
    group = await Group.find_one(Group.id == uuid.UUID(request.group_id), fetch_links=True)
    if not group:
        raise Error.GROUP_NOT_FOUND

    pupils = await Pupil.find({ "_id": { "$in": [uuid.UUID(id) for id in request.pupil_id] } }, fetch_links=True).to_list()
    if not pupils:
        raise Error.PUPIL_NOT_FOUND
    
    existing_pupil_ids = {str(pupil.id) for pupil in group.pupils} if group.pupils else set()
    new_pupils = [pupil for pupil in pupils if str(pupil.id) not in existing_pupil_ids]
    
    if not new_pupils:
        raise Error.PUPIL_ALREADY_IN_GROUP 

    if not group.pupils:
        group.pupils = pupils
    else:
        group.pupils.extend(new_pupils)
        
    await group.save()
    
    return schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=schemas.Teacher_(
            id=str(group.teacher.id),
            login=group.teacher.login,
            hashed_password=group.teacher.hashed_password,
            pupils=[schemas.Pupil_(
                id=str(pupil.id),
                username=pupil.username,
                firstname=pupil.firstname,
                lastname=pupil.lastname
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname
        )
            for pupil in group.pupils   
        ]
    )
    

@router.delete("/groups/pupils")
async def remove_pupils_from_group(request: schemas.RemovePupilsRequest,
                                    _: Teacher = Depends(get_current_user)) -> schemas.Group:
    group = await Group.find_one(Group.id == uuid.UUID(request.group_id), fetch_links=True)
    if not group:
        raise Error.GROUP_NOT_FOUND

    pupil_ids = [uuid.UUID(id) for id in request.pupil_id]
    pupils = await Pupil.find({"_id": {"$in": pupil_ids}}, fetch_links=True).to_list()
    
    if len(pupils) != len(pupil_ids):
        found_ids = {str(p.id) for p in pupils}
        missing_ids = [str(pid) for pid in pupil_ids if str(pid) not in found_ids]
        raise Error.PUPIL_NOT_FOUND.with_detail(f"Missing pupils: {missing_ids}")

    if group.pupils:
        group.pupils = [p for p in group.pupils if str(p.id) not in request.pupil_id]
    
    await group.save()
    
    return schemas.Group(
        id=str(group.id),
        name=group.name,
        teacher=schemas.Teacher_(
            id=str(group.teacher.id),
            login=group.teacher.login,
            hashed_password=group.teacher.hashed_password,
            pupils=[schemas.Pupil_(
                id=str(pupil.id),
                username=pupil.username,
                firstname=pupil.firstname,
                lastname=pupil.lastname
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname
        )
            for pupil in group.pupils   
        ]
    )
