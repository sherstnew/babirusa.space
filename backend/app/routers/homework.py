from fastapi import APIRouter, Depends

from app.data.models import Teacher
from app.data.schemas import HomeworkCheckRequest, HomeworkCheckResponse
from app.utils.homework_checker import check_homework
from app.utils.security import get_current_user

router = APIRouter(prefix="/homework", tags=["Homework"])


@router.post("/check")
async def check_homework_route(
    request: HomeworkCheckRequest,
    _: Teacher = Depends(get_current_user),
) -> HomeworkCheckResponse:
    reviews = await check_homework(
        prompt=request.prompt,
        file_pattern=request.file_pattern,
        usernames=request.usernames,
    )
    return HomeworkCheckResponse(results=reviews)
