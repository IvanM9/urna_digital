import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
import os
from dotenv import load_dotenv

# Carga el archivo .env
load_dotenv()

# Obtiene el valor de la variable de entorno
clave = os.getenv('CLAVE')

def verificar_voto(cedula):
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'")
    cursor = conexion.cursor()

    cursor.execute("SELECT voto_realizado FROM estudiantes WHERE cedula=?", (cedula,))
    voto = cursor.fetchone()[0]
    print(voto)

    conexion.close()

    return voto

# Función para almacenar el voto en la base de datos
def guardar_voto(opcion, cedula):
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    cursor = conexion.cursor()
    cursor.execute(f"PRAGMA key='{clave}'")

    # Insertar el voto en la tabla de votos
    cursor.execute("INSERT INTO votos (opcion_id) VALUES (?)", (opcion,))

    # Marcar la cédula como votada
    cursor.execute("UPDATE estudiantes SET voto_realizado = 1 WHERE cedula=?", (cedula,))

    # Confirmar la transacción
    conexion.commit()

    # Cerrar la conexión
    conexion.close()
