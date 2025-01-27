import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    OPENAI_KEY: str = os.getenv("OPENAI_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")


settings = Settings()
