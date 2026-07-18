from redis import Redis
from core.settings import settings

def test_redis_connection():
    print(f"\n----- VERIFICANDO REDIS -----")
    print(f"Host: {settings.redis_host}")
    print(f"Port: {settings.redis_port}")
    
    try:
        client = Redis(
            host=settings.redis_host, 
            port=settings.redis_port, 
            decode_responses=True
        )
        # Intentamos un ping simple
        if client.ping():
            print("✅ ÉXITO: Conexión establecida con Redis.")
        else:
            print("❌ ERROR: Redis no respondió al ping.")
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar a Redis: {e}")

if __name__ == "__main__":
    test_redis_connection()