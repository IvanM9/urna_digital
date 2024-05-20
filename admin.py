import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
import os
from dotenv import load_dotenv
import json
import random
from faker import Faker
from datetime import datetime
import pytz

# Carga el archivo .env
load_dotenv()

# Obtiene el valor de la variable de entorno
clave = os.getenv('CLAVE')

def init_db():
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'")
    cursor = conexion.cursor()

    with open('create-db.sql', 'r') as file:
        script = file.read()
        cursor.executescript(script)

    # Verificar si no hay datos en la tabla estudiantes
    cursor.execute('SELECT COUNT(*) FROM estudiantes')
    num_estudiantes = cursor.fetchone()[0]
    if num_estudiantes == 0:
        # Ejecutar el archivo register-students.sql
        with open('register-data.sql', 'r') as file:
            script = file.read()
            cursor.executescript(script)
        
        generar_estudiantes()

        # Ejecutar el archivo agregardatos.py
        # os.system('python3 generate-passwords.py')

    conexion.commit()
    conexion.close()

def contar_votos():
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    cursor.execute('SELECT COUNT(*) FROM votos')
    resultado = cursor.fetchone()[0]

    conexion.close()

    return resultado

def contar_votantes():
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'")  # Establecer la clave de encriptación
    cursor = conexion.cursor()

    cursor.execute('SELECT COUNT(*) FROM estudiantes')
    resultado = cursor.fetchone()[0]

    conexion.close()

    return resultado

# Función para obtener los resultados de los votos
def obtener_resultados():
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    # Obtener la cantidad de votos por opción
    cursor.execute("SELECT opcion_id, COUNT(*) as total FROM votos GROUP BY opcion_id")

    # Obtener los resultados
    resultados = cursor.fetchall()

    # Cerrar la conexión
    conexion.close()

    return resultados

def generar_resultados():
    # Consultar la cantidad de votos por opción
    resultados = obtener_resultados()

    mensaje = "Aún no se ha registrado ningún voto."
    if resultados:
        mensaje = None

    # Encontrar la opción con más votos
    ganador = None
    if resultados:
        ganador = max(resultados, key=lambda x: x[1])[0]

    return resultados, ganador, mensaje

def obtener_candidatos():
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    # Obtener la lista de candidatos
    cursor.execute("SELECT id, opcion, imagen_url FROM opciones")

    # Obtener los resultados
    candidatos = cursor.fetchall()

    #Convertir los resultados en una lista de diccionarios
    candidatos_dict = [{"id": id, "opcion": opcion, "imagen": imagen_url} for id, opcion, imagen_url in candidatos]

    # Cerrar la conexión
    conexion.close()

    return candidatos_dict

def obtener_votos():
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    # Obtener la lista de votos
    cursor.execute("SELECT v.opcion_id, o.opcion, COUNT(*) as total FROM votos v JOIN opciones o ON v.opcion_id = o.id GROUP BY v.opcion_id, o.opcion")

    # Obtener los resultados
    votos = cursor.fetchall()

    # Separar la cantidad de votos y las opciones en arrays distintos
    cantidad_votos = [voto[2] for voto in votos]

    opciones = [voto[1] for voto in votos]
    print(opciones)

    # Cerrar la conexión
    conexion.close()

    return cantidad_votos, opciones

def votos_por_hora():
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    # Consultar la cantidad de votos por hora
    cursor.execute("""
        SELECT COUNT(*) as votos, strftime('%Y-%m-%dT%H:00:00.000Z', fecha) as fecha
        FROM votos
        GROUP BY strftime('%Y-%m-%dT%H:00:00.000Z', fecha)
        ORDER BY fecha ASC
    """)

    # Obtener los resultados
    votos_por_hora = cursor.fetchall()

    # Convertir los resultados a la estructura deseada
    votos_x_hora = [row[0] for row in votos_por_hora]
    hora = [row[1] for row in votos_por_hora]

    # Convertir las fechas a la zona horaria -05:00
    hora = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Etc/GMT+5')).strftime('%Y-%m-%dT%H:%M:%S.%fZ') for date in hora]

    # Cerrar la conexión
    conexion.close()

    return votos_x_hora, hora

def obtener_estudiantes():
    # Conectar a la base de datos SQLite
    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    # Obtener la lista de estudiantes
    cursor.execute("SELECT id, nombres, apellidos, carrera, curso, cedula FROM estudiantes ORDER BY apellidos, nombres")

    # Obtener los resultados
    estudiantes = cursor.fetchall()
    print(estudiantes)
    #Convertir los resultados en una lista de diccionarios
    estudiantes_dict = [{"nombres": nombres, "apellidos": apellidos, "carrera": carrera, "curso": curso, "cedula": cedula, "id": id} for id, nombres, apellidos, carrera, curso, cedula in estudiantes]

    # Cerrar la conexión
    conexion.close()

    return estudiantes_dict

def generar_estudiantes():
    fake = Faker()
    estudiantes = []
    carreras = ['Telematica', 'Software', 'Arquitectura', 'Mercadotecnia', 'Enfermería']
    cursos = ['1ro', '2do', '3ro', '4to', '5to', '6to', '7mo', '8vo', '9no', '10mo']

    conexion = sqlcipher.connect('urna_digital.db')
    conexion.execute(f"PRAGMA key='{clave}'") 
    cursor = conexion.cursor()

    for _ in range(372):
        nombres = fake.first_name()
        apellidos = fake.last_name()
        carrera = random.choice(carreras)
        curso = random.choice(cursos)
        cedula = fake.unique.random_number(digits=10)

        estudiante = (nombres, apellidos, carrera, curso, cedula, cedula)
        cursor.execute("INSERT INTO estudiantes (nombres, apellidos, carrera, curso, cedula, clave_unica) VALUES (?, ?, ?, ?, ?, ?)", estudiante)

    # Confirmar la transacción
    conexion.commit()

    # Cerrar la conexión
    conexion.close()


def verificar_presidente(cedula, clave_unica):
    # Conectar a la base de datos SQLite encriptada
    conexion = sqlcipher.connect('urna_digital.db')
    cursor = conexion.cursor()
    cursor.execute(f"PRAGMA key='{clave}'")  # Establecer la clave de encriptación

    # Verificar si la cédula y la clave única están en la base de datos
    cursor.execute("SELECT * FROM estudiantes WHERE cedula=? AND clave_unica=? AND presidente=1", (cedula, clave_unica))
    estudiante = cursor.fetchone()

    # Cerrar la conexión
    conexion.close()
    print(estudiante)

    return estudiante