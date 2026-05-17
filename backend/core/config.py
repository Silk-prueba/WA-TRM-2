from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    waha_session_name: str = "default"
    waha_api_url: str = "http://localhost:3000"
    backend_port: int = 8000
    test_chat_id: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
