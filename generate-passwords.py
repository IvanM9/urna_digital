import sqlite3
import random
from pysqlcipher3 import dbapi2 as sqlcipher
import os
from dotenv import load_dotenv

# Carga el archivo .env
load_dotenv()

# Obtiene el valor de la variable de entorno
clave = os.getenv('CLAVE')

# Conectar a la base de datos SQLite
conexion = sqlcipher.connect('urna_digital.db')
conexion.execute(f"PRAGMA key='{clave}'")
cursor = conexion.cursor()

# Obtener la lista de estudiantes
cursor.execute("SELECT cedula FROM estudiantes")
estudiantes = cursor.fetchall()

# Generar y actualizar claves únicas para cada estudiante
for estudiante in estudiantes:
    cedula = estudiante[0]
    clave_unica = ''.join(str(random.randint(1, 5)) for _ in range(5))
    cursor.execute("UPDATE estudiantes SET clave_unica = ? WHERE cedula = ?", (clave_unica, cedula))

# Confirmar la transacción
conexion.commit()

# Cerrar la conexión
conexion.close()
