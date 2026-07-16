import os
from pathlib import Path
from processing.delta_manager import DeltaManager

def test_delta_manager():
    # Setup: Archivo dummy
    test_file = Path("test_dummy.txt")
    test_file.write_text("Contenido inicial")
    
    # Instanciamos
    dm = DeltaManager(registry_path="data/test_registry.json")
    
    # 1. Validación: El archivo es nuevo, debe necesitar procesamiento
    assert dm.needs_processing(test_file) == True
    
    # 2. Validación: Actualizamos el registro
    dm.update_registry(test_file)
    assert dm.needs_processing(test_file) == False
    
    # 3. Validación: Cambiamos el contenido, debe detectar el cambio
    test_file.write_text("Contenido modificado")
    assert dm.needs_processing(test_file) == True
    
    # Limpieza
    test_file.unlink()
    if os.path.exists("data/test_registry.json"):
        os.remove("data/test_registry.json")
        
    print("PROCESSING TEST PASSED")

if __name__ == "__main__":
    test_delta_manager()