import psycopg2
import sys

def test_hardcoded_connection():
    # Valores "en duro" para validar la infraestructura
    DB_PARAMS = {
        "dbname": "eka_db",
        "user": "admin",
        "password": "password",
        "host": "127.0.0.1", # Forzamos IP literal para evitar resolución DNS/IPv6
        "port": 5433
    }
    
    print(f"--- Intentando conexión mínima a {DB_PARAMS['host']}:{DB_PARAMS['port']} ---")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("✅ ÉXITO: Conexión establecida con las credenciales dadas.")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Versión de Postgres detectada: {version[0]}")
        
        cur.close()
        conn.close()
        sys.exit(0)
    except Exception as e:
        print(f"❌ FALLO CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_hardcoded_connection()