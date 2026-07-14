from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_user: str = Field(default="admin", env="DB_USER")
    db_password: str = Field(default="1234", env="DB_PASSWORD")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="eka_db", env="DB_NAME")

    @property
    def database_url(self) -> str:
        return (
                f"postgresql+psycopg2://"
                f"{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}"
                f"/{self.db_name}"
            )

    class Config:
        env_file = ".env"

settings = Settings()