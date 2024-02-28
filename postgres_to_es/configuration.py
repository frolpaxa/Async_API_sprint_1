from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    es_url: str

    pg_dsn: str
    pack_size: int = 100

    start_date: str = "1970-01-01 00:00:00"
    file_storage: str = "state.json"
    sleep_time: int = 10

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_file=".env",
        extra="ignore",
        model_fields={
            "pg_dsn": {
                "env": "PG_DSN",
            },
            "es_url": {
                "env": "ES_URL",
            },
        },
    )
