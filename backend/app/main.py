from contextlib import asynccontextmanager
from typing import AsyncIterator

from beanie import Document, UnionDoc, init_beanie
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app import ENVIRONMENT, MONGO_DSN, projectConfig
from app.routers import group, homework, pupil, system, teacher


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_DSN, uuidRepresentation="standard")
    await init_beanie(
        database=client.get_default_database(),
        document_models=Document.__subclasses__() + UnionDoc.__subclasses__(),
    )
    yield


if ENVIRONMENT == "prod":
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__,
        lifespan=lifespan,
        docs_url=None,
    )

else:
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__,
        lifespan=lifespan,
    )

api_router = APIRouter(prefix="/api")

api_router.include_router(system.router)
api_router.include_router(teacher.router)
api_router.include_router(group.router)
api_router.include_router(pupil.router)
api_router.include_router(homework.router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event('startup')
# async def startup_event():
#     # AsyncIOMotorClient.uuid_representation = 'standard'
#     client = AsyncIOMotorClient(MONGO_DSN, uuidRepresentation='standard')

#     await init_beanie(
#         database=client.get_default_database(),
#         document_models=Document.__subclasses__() + UnionDoc.__subclasses__()
#     )
