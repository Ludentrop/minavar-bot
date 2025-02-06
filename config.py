from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path


env_file = Path(__file__).parent / '.env'


class Settings(BaseSettings):
    TOKEN: SecretStr
    PUBLIC_CHAT_ID: int
    PRIVATE_CHAT_ID: int
    PUBLIC_DB: str
    PRIVATE_DB: str
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding='utf-8')


settings = Settings()
