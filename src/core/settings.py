from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PostgreSQL
    db_host: str = "127.0.0.1"
    db_port: int = 5433
    db_name: str = "eka_db"
    db_user: str = "admin"
    db_password: str = "password"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "admin"
    minio_secret_key: str = "password"

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    def __init__(self, **values):
        super().__init__(**values)
        # Blindaje de fuerza bruta para TODOS los servicios
        self.db_host = "127.0.0.1"
        self.db_port = 5433
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.minio_endpoint = "localhost:9000"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()