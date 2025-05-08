from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from app.data.models import UserPort

router = APIRouter(prefix="/resolve")

@router.get('/{subdomain}')
async def resolve_subdomain(subdomain: str):
  port = await UserPort.find_one(UserPort.username == subdomain)
  
  if port:
    return {"port": port.port}
  else:
    return HTTPException(404)