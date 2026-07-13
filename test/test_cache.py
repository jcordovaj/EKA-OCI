import time
from rag_engine import execute_smart_rag

# Simulamos el vector de la pregunta "Pregunta sobre políticas de TI"
# Para la prueba, usamos el mismo vector base para denotar alta cercanía semántica
vector_pregunta_ti = [0.035] * 1536

print("\n=== EJECUCIÓN 1: Primera vez que se hace la pregunta ===")
resultado_1 = execute_smart_rag(
    user_question="¿Cuáles son las políticas de seguridad de TI actuales?", 
    mock_embedding=vector_pregunta_ti
)
print(f"Respuesta obtenida del motor: {resultado_1['response']}")
print(f"Origen de la información: {resultado_1['source_type']}")

time.sleep(1)

print("\n=== EJECUCIÓN 2: Pregunta idéntica o muy similar (Lanzamiento de Caché) ===")
# El usuario cambia ligeramente la redacción, pero el modelo de embeddings genera un vector muy cercano
resultado_2 = execute_smart_rag(
    user_question="Dime las políticas vigentes de seguridad en TI", 
    mock_embedding=vector_pregunta_ti
)
print(f"Respuesta obtenida del motor: {resultado_2['response']}")
print(f"Origen de la información: {resultado_2['source_type']}")
print(f"Métricas de Ahorro: {resultado_2['insights']}")