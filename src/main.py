from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from ai_helper.router import router as ai_helper_router
from config import settings
from db import sessionmanager
from relatories.router import router as relatories_router

DATABASE_URL: str = settings.DATABASE_URL


# Creating engine to be use through the whole app
async def check_db_connection():
    async with sessionmanager.session() as session:
        print("Starting database connection...")
        await session.execute(select(1))
        print("Database connection successful")


sessionmanager.init(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


# FastAPI instance
app = FastAPI(title="Relatory generation for all clients", lifespan=lifespan)


app.include_router(relatories_router)
app.include_router(ai_helper_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", reload=True)
