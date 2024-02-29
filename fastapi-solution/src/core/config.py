from logging import config as logging_config

from core.logger import LOGGING

from pydantic import Field
from pydantic_settings import BaseSettings

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = "Some project name"
    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    elastic_host: str = Field("elk", env="ELASTIC_HOST")
    elastic_port: int = Field(9200, env="ELASTIC_PORT")

    class Config:
        env_file = "../../../.env"
