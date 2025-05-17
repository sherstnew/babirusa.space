from beanie import init_beanie, Document, UnionDoc
from fastapi import FastAPI, APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

from app import MONGO_DSN, ENVIRONMENT, projectConfig
from app.routers import system, teacher

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

app.include_router(api_router)


@app.on_event('startup')
async def startup_event():
    # AsyncIOMotorClient.uuid_representation = 'standard'
    client = AsyncIOMotorClient(MONGO_DSN, uuidRepresentation='standard')

    await init_beanie(
        database=client.get_default_database(),
        document_models=Document.__subclasses__() + UnionDoc.__subclasses__()
    )