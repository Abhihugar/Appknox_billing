import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, field_validator
from typing import Dict

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    HASHING_ALGORITHM: str = os.getenv("HASHING_ALGORITHM", "bcrypt")
    ARGON2_HASH_MEMORY: int = int(os.getenv("ARGON2_HASH_MEMORY", 65536))
    ARGON2_ITERATION_COUNT: int = int(os.getenv("ARGON2_ITERATION_COUNT", 4))
    ARGON2_PARALLELISM: int = int(os.getenv("ARGON2_PARALLELISM", 2))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    USER_PWD_RESET_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("USER_PWD_RESET_TOKEN_EXPIRE_MINUTES", 15)
    )
    USER_VERIFY_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("USER_VERIFY_TOKEN_EXPIRE_MINUTES", 15)
    )

    DEFAULT_DATABASE_HOST: str = os.getenv("DEFAULT_DATABASE_HOST", "localhost")
    DEFAULT_DATABASE_USER: str = os.getenv("DEFAULT_DATABASE_USER", "user")
    DEFAULT_DATABASE_PASSWORD: str = os.getenv("DEFAULT_DATABASE_PASSWORD", "password")
    DEFAULT_DATABASE_PORT: str = os.getenv("DEFAULT_DATABASE_PORT", "5432")
    DEFAULT_DATABASE_DB: str = os.getenv("DEFAULT_DATABASE_DB", "postgres")
    DATABASE_URI: str = ""
    DATABASE_SYNC_URI: str = ""

    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )

    @field_validator("DATABASE_SYNC_URI")
    def build_sync_db_uri(cls, v: str, values: Dict[str, str]) -> str:
        """
        Build a synchronous PostgreSQL DB URI using psycopg2 driver.
        """
        values = values.data
        return str(
            AnyUrl.build(
                scheme="postgresql+psycopg2",
                username=values["DEFAULT_DATABASE_USER"],
                password=values["DEFAULT_DATABASE_PASSWORD"],
                host=values["DEFAULT_DATABASE_HOST"],
                port=int(values["DEFAULT_DATABASE_PORT"]),
                path=values["DEFAULT_DATABASE_DB"],
            )
        )

    @field_validator("DATABASE_URI")
    def build_db_uri(cls, v: str, values: Dict[str, str]) -> str:
        """
        Build the Database URI using the class fields.
        """
        print(f"values data {values}")
        values = values.data
        db_url = AnyUrl.build(
            scheme="postgresql+asyncpg",
            username=values["DEFAULT_DATABASE_USER"],
            password=values["DEFAULT_DATABASE_PASSWORD"],
            host=values["DEFAULT_DATABASE_HOST"],
            port=int(values["DEFAULT_DATABASE_PORT"]),
            path=values["DEFAULT_DATABASE_DB"],
        )
        print(f"Database Url {db_url}")
        return str(db_url)


settings = Settings()
print(f"Database URI: {settings.DATABASE_URI}")
