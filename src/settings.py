from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")
    postgres_database_name: str = "search_db"
    postgres_host: str = "search-postgres"
    postgres_port: str = "5432"
    postgres_username: str = "postgres"
    postgres_password: str = "postgres"
    kafka_bootstrap_servers: str = "redpanda:29092"
    kafka_topic_ads: str = "ads"
    kafka_consumer_group: str = "search-service"
    ad_service_url: str = "http://ads-service:8000"
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+asyncpg://{self.postgres_username}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database_name}"
        )
