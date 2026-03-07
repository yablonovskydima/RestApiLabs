from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_MONGO_URL: str
    MONGO_DB: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()