from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "User Service"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
    