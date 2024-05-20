import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
import os
from dotenv import load_dotenv

# Carga el archivo .env
load_dotenv()

# Obtiene el valor de la variable de entorno
clave = os.getenv('CLAVE')

# Ruta a la base de datos encriptada y clave
encrypted_db_path = 'urna_digital.db'
encryption_key = clave
decrypted_db_path = 'decrypted.db'

# Conectar a la base de datos encriptada
con = sqlcipher.connect(encrypted_db_path)
cur = con.cursor()

# Desencriptar la base de datos
cur.execute(f"PRAGMA key = '{encryption_key}';")
cur.execute("PRAGMA cipher_migrate;")  # Asegúrate de estar en la versión correcta de SQLCipher

# Adjuntar una nueva base de datos sin clave de encriptación
print(decrypted_db_path)
cur.execute(f"ATTACH DATABASE '{decrypted_db_path}' AS plaintext KEY '';")

# Exportar todas las tablas a la nueva base de datos
cur.execute("SELECT sqlcipher_export('plaintext');")

# Guardar los cambios y desacoplar la base de datos desencriptada
cur.execute("DETACH DATABASE plaintext;")

# Cerrar la conexión a la base de datos encriptada
con.close()

# Conectar a la nueva base de datos desencriptada y realizar una prueba
new_con = sqlite3.connect(decrypted_db_path)
new_cur = new_con.cursor()

# Verificar que la nueva base de datos contiene las tablas y datos esperados
new_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = new_cur.fetchall()
print("Tablas en la nueva base de datos desencriptada:", tables)

# Cerrar la conexión a la nueva base de datos desencriptada
new_con.close()