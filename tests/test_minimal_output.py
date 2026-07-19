# test_minimal.py
import sys
import os

print("Hola mundo, el intérprete funciona.")

try:
    from persistence.unit_of_work import UnitOfWork
    print("UnitOfWork importado correctamente.")
except Exception as e:
    print(f"Error al importar UoW: {e}")

try:
    from persistence.orm.document import ProcessingJob
    print("ProcessingJob importado correctamente.")
except Exception as e:
    print(f"Error al importar ORM: {e}")