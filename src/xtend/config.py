from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DEBUG: bool = Field(True, env="DEBUG")
    HOST: str  = Field("0.0.0.0", env="HOST")
    PORT: int   = Field(4563,   env="PORT")
    SECRET_KEY: str = Field("xtendscreen", env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()