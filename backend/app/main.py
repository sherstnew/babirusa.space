from contextlib import asynccontextmanager
from beanie import init_beanie, Document, UnionDoc
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncIterator

from app import MONGO_DSN, ENVIRONMENT, projectConfig
from app.routers import system, teacher, group, pupil

@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    client = AsyncIOMotorClient(MONGO_DSN, uuidRepresentation='standard')
    await init_beanie(
        database=client.get_default_database(),
        document_models=Document.__subclasses__() + UnionDoc.__subclasses__()
    )
    yield

if ENVIRONMENT == "prod":
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__,
        docs_url=None
    )

else:
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__
    )
    
api_router = APIRouter(prefix="/api")

api_router.include_router(system.router)
api_router.include_router(teacher.router)
api_router.include_router(group.router)
api_router.include_router(pupil.router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
