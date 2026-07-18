from minio import Minio
from src.core.settings import settings

def test_minio_connection():
    print(f"\n----- VERIFICANDO MINIO -----")
    print(f"Endpoint: {settings.minio_endpoint}")
    
    try:
        # Inicializamos el cliente con los valores blindados
        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False  # Asumiendo conexión local sin TLS
        )
        
        # Intentamos listar los buckets como prueba de conectividad
        buckets = client.list_buckets()
        print(f"✅ ÉXITO: Conexión establecida. Buckets encontrados: {[b.name for b in buckets]}")
        
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar a MinIO: {e}")

if __name__ == "__main__":
    test_minio_connection()