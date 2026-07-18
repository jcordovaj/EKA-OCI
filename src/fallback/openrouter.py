import time
from openai import OpenAI
from openai import OpenAIError, RateLimitError, APIStatusError
from core.settings import settings

# Configuración inicial del cliente OpenRouter
client = OpenAI(
    base_url="operouter_base_url",  # Reemplaza con la URL de OpenRouter
    api_key="OPENROUTER_API_KEY",  # Reemplaza con tu token de OpenRouter
)

# Lista priorizada de modelos gratuitos (puedes cambiar el orden o añadir más)
# Nota: Los IDs de modelos gratuitos en OpenRouter suelen terminar en ":free"
MODELOS_GRATUITOS = [
    "google/gemini-2.5-flash:free",
    "meta-llama/llama-3-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free"
]

def enviar_prompt_con_cascada(prompt, historial_mensajes=None):
    """
    Envía un prompt a OpenRouter probando los modelos de la lista en cascada
    si el anterior falla por límites de tokens o saturación del servidor.
    """
    # Si no hay historial, creamos la estructura básica de mensajes
    mensajes = historial_mensajes or [{"role": "user", "content": prompt}]
    
    # Iteramos sobre la lista de modelos en orden de prioridad
    for i, modelo in enumerate(MODELOS_GRATUITOS):
        print(f"🤖 Intentando con el modelo [{i+1}/{len(MODELOS_GRATUITOS)}]: {modelo}...")
        
        try:
            # Realizamos la petición HTTP a OpenRouter
            response = client.chat.completions.create(
                model=modelo,
                messages=mensajes,
                # Buenas prácticas para OpenRouter: ayuda a rankear en las tablas públicas
                extra_headers={
                    "HTTP-Referer": "https://localhost:3000", 
                    "X-Title": "Script de Cascada Gratuita",
                }
            )
            
            # Si la petición fue exitosa, extraemos el texto y rompemos el bucle
            respuesta_texto = response.choices[0].message.content
            print("✅ ¡Respuesta obtenida con éxito!")
            return respuesta_texto, modelo

        except RateLimitError as e:
            # Captura el Error 429: Cuota excedida, límite de tokens o demasiadas peticiones
            print(f"⚠️ Límite excedido o sin tokens en {modelo}. Saltando al siguiente...")
            print(f"Detalle del error: {e}")
            continue
            
        except APIStatusError as e:
            # Captura Errores 5xx: El modelo está caído, saturado (peak) o inaccesible temporalmente
            print(f"⚠️ El modelo {modelo} devolvió un error de estado ({e.status_code}). Posible saturación.")
            continue
            
        except OpenAIError as e:
            # Cualquier otro error inesperado de la librería
            print(f"💥 Error inesperado de conexión con {modelo}: {e}")
            continue

    # Si el bucle termina y ningún modelo respondió
    raise RuntimeError("🚨 Todos los modelos gratuitos de la lista fallaron o agotaron sus capas gratuitas.")

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    prompt_usuario = "Explícame de forma muy breve qué es la computación cuántica."
    
    try:
        respuesta, modelo_exitoso = enviar_prompt_con_cascada(prompt_usuario)
        print("\n" + "="*40)
        print(f"Respuesta final (Generada por {modelo_exitoso}):")
        print("="*40)
        print(respuesta)
        
    except Exception as error_final:
        print(f"\n{error_final}")
