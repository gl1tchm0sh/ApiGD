from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVIDOR:       str
    PUERTO:         str
    USUARIO:        str
    PASSWD:         str
    BD:             str
    SECRET_KEY:     str
    ALGORITHM:      str
    TOKEN_TIMEOUT:  str

    class Config:
        env_file = ".env"

settings = Settings()