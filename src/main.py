from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from ai_helper.router import router as ai_helper_router
from config import settings
from db import sessionmanager
from relatories.router import router as relatories_router

DATABASE_URL: str = settings.DATABASE_URL
API_KEY: str = settings.API_KEY


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


async def api_key_auth(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


# FastAPI instance
app = FastAPI(
    title="Relatory generation for all clients",
    lifespan=lifespan,
    dependencies=[Depends(api_key_auth)],
)


app.include_router(relatories_router)
app.include_router(ai_helper_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="localhost", reload=True)
