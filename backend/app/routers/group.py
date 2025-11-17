from fastapi import APIRouter, Depends, Body, Query

from app.data.models import Teacher, Pupil, Group
from app.data import schemas
from app.utils.error import Error
from app.utils.security import get_current_user


from typing import Annotated, List

import uuid

router = APIRouter(prefix='/teacher/groups', tags=["Groups"])

@router.post("/new")
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
                lastname=pupil.lastname,
                container_status=pupil.container_status
        )
            for pupil in current_teacher.pupils
        ]
            ),
        pupils=[]
    )

@router.get("")
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
                lastname=pupil.lastname,
                container_status=pupil.container_status
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname,
            container_status=pupil.container_status
        )
            for pupil in group.pupils   
        ]
    )
        for group in groups
    ]
    
@router.patch("")
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
                lastname=pupil.lastname,
                container_status=pupil.container_status
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname,
            container_status=pupil.container_status
        )
            for pupil in group.pupils   
        ]
    )
    
@router.delete("")
async def delete_teacher_groups(groups_id: Annotated[List[str], Query()],
                               _: Teacher = Depends(get_current_user)) -> str:
    
    groups = await Group.find({ "_id": { "$in": [uuid.UUID(id) for id in groups_id] }}, fetch_links=True).to_list()
    if not groups:
        raise Error.GROUP_NOT_FOUND

    for group in groups:  
        await group.delete()
    
    return "OK"
    
@router.post("/pupils")
async def add_pupil_in_group(request: schemas.AddPupil, _: Teacher = Depends(get_current_user)) -> schemas.Group:
    group = await Group.find_one(Group.id == uuid.UUID(request.group_id), fetch_links=True)
    if not group:
        raise Error.GROUP_NOT_FOUND

    pupils = await Pupil.find({ "_id": { "$in": [uuid.UUID(id) for id in request.pupil_id] } }, fetch_links=True).to_list()
    if not pupils:
        raise Error.PUPIL_NOT_FOUND
    
    for pupil in pupils:
        new_groups_pupil = await Group.find({"pupils._id": pupil.id, "_id": {"$ne": group.id}}, fetch_links=True).to_list()
        
        for old_group in new_groups_pupil:
            old_group.pupils = [p for p in old_group.pupils if p.id != pupil.id]
            await old_group.save()
    
    existing_pupil_ids = {str(pupil.id) for pupil in group.pupils} if group.pupils else set()
    new_pupils = [pupil for pupil in pupils if str(pupil.id) not in existing_pupil_ids]
    

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
                lastname=pupil.lastname,
                container_status=pupil.container_status
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname,
            container_status=pupil.container_status
        )
            for pupil in group.pupils   
        ]
    )
    

@router.delete("/pupils")
async def remove_pupils_from_group(group_id: Annotated[str, Query()], 
                                   pupil_id: Annotated[list, Query()],
                                    _: Teacher = Depends(get_current_user)) -> schemas.Group:
    group = await Group.find_one(Group.id == uuid.UUID(group_id), fetch_links=True)
    if not group:
        raise Error.GROUP_NOT_FOUND

    pupil_ids = [uuid.UUID(id) for id in pupil_id]
    pupils = await Pupil.find({"_id": {"$in": pupil_ids}}, fetch_links=True).to_list()
    
    if len(pupils) != len(pupil_ids):
        found_ids = {str(p.id) for p in pupils}
        missing_ids = [str(pid) for pid in pupil_ids if str(pid) not in found_ids]
        raise Error.PUPIL_NOT_FOUND.with_detail(f"Missing pupils: {missing_ids}")

    if group.pupils:
        group.pupils = [p for p in group.pupils if str(p.id) not in pupil_id]
    
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
                lastname=pupil.lastname,
                container_status=pupil.container_status
        )
            for pupil in group.teacher.pupils
        ]
            ),
        pupils=[schemas.Pupil_(
            id=str(pupil.id),
            username=pupil.username,
            firstname=pupil.firstname,
            lastname=pupil.lastname,
            container_status=pupil.container_status
        )
            for pupil in group.pupils   
        ]
    )

