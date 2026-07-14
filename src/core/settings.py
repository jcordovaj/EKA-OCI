from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración global para EKA-OCI. 
    Todas las credenciales sensibles deben ser proporcionadas por el entorno operativo.
    Se usa Pydantic's base settings que lee de variables de entorno (OS Environment).
    """
    # PostgreSQL
    db_host    : str = Field(default="localhost", alias="DB_HOST")
    db_port    : int = Field(default=5432, alias="DB_PORT")
    db_name    : str = Field(default="eka_db", alias="DB_NAME")
    db_user    : str = Field(default="admin", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")

    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    # MinIO
    minio_endpoint  : str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="admin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="password", alias="MINIO_SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )


settings = Settings()