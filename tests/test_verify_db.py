from alembic import config
import psycopg2
import os
print(f"Directorio de trabajo actual: {os.getcwd()}")
print(f"¿Existe el archivo .env?: {os.path.exists('.env')}")
# Limpiamos explícitamente el entorno para evitar caracteres extraños
os.environ.pop("LANG", None)
os.environ.pop("LC_ALL", None)

from core.settings import settings

print("----- SETTINGS -----")
print(f"DB_HOST     = {settings.db_host}")
print(f"DB_PORT     = {settings.db_port}")
print(f"DB_NAME     = {settings.db_name}")
print(f"DB_USER     = {settings.db_user}")
print(f"DB_PASSWORD = {settings.db_password}")
print("--------------------")

try:
    # Conexión directa, sin configurar nada extraño
    conn = psycopg2.connect(
        dbname="eka_db",
        user="admin",
        password="password",
        host="localhost",
        port=5433,
        connect_timeout=5
    )
    print("✅ ÉXITO: Conexión establecida con psycopg2.")
    conn.close()
except Exception as e:
    print(f"❌ FALLO CRÍTICO: {e}")
    