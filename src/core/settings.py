from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración de entornos
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5433
    DB_NAME: str = "eka_db"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "password"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Storage (MinIO/S3) ---
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "admin"
    STORAGE_SECRET_KEY: str = "password"
    BUCKET_NAME: str = "ekadocs"

    # --- Redis ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # --- Políticas de Triage (Stage 1) ---
    MAX_PDF_PAGES: int = 200
    MAX_LOCAL_WORKERS: int = 2
    MAX_BATCH_UPLOAD: int = 5
    
    # --- Rutas de Procesamiento ---
    INBOX_PATH: str = "inbox/"
    REJECTS_PATH: str = "failed/"
    PROCESSED_PATH: str = "processed/"

# Instancia global única
settings = Settings()