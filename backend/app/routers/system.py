from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["Test"])

@router.get('/ping')
async def ping() -> str:
    return 'pong'