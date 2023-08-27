from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    servidor:       str
    puerto:         str
    usuario:        str
    passwd:         str
    bd:             str
    secret_key:     str
    algorithm:      str
    token_timeout:  int

    class Config:
        env_file = ".env"

settings = Settings()