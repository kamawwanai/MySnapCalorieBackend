from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    DB_URL: PostgresDsn | str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()