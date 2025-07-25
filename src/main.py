from fastapi import FastAPI
from src.tasks.controller import router as task_route
from src.database.core import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

def registered_routes(app: FastAPI):
    app.include_router(task_route)

registered_routes(app)