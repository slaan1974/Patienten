from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./patienten.db"
    SECRET_KEY: str = "vervang-dit-met-een-veilige-sleutel-in-productie"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOCK_TIMEOUT_MINUTES: int = 5
    LOCK_HEARTBEAT_SECONDS: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
