from pydantic import BaseSettings, Field, PostgresDsn


class Config(BaseSettings):
    db_url: PostgresDsn = Field(env="DB_URL")


config = Config()
