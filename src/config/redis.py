from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = Field("redis", alias="REDIS_HOST")
    port: int = Field(6379, alias="REDIS_PORT")

    @property
    def redis_url(self) -> RedisDsn:
        return (f"redis://{self.host}:{self.port}/0")

settings = Settings()
