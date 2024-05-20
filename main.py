import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os
from admin import contar_votos, generar_resultados, obtener_resultados, contar_votantes, init_db, obtener_candidatos, obtener_votos, votos_por_hora, obtener_estudiantes, verificar_presidente
from pysqlcipher3 import dbapi2 as sqlcipher
import os
from dotenv import load_dotenv
from student import verificar_voto, guardar_voto

# Carga el archivo .env
load_dotenv()

# Obtiene el valor de la variable de entorno
clave = os.getenv('CLAVE')
user_admin = os.getenv('USER_ADMIN')
password_admin = os.getenv('PASSWORD_ADMIN')

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

app.secret_key = os.urandom(24)

# Lista en memoria de cédulas que ya han votado
cedulas_votadas = []

# Función para verificar la cédula y la clave única en la base de datos
def verificar_estudiante(cedula, clave_unica):
    # Conectar a la base de datos SQLite encriptada
    conexion = sqlcipher.connect('urna_digital.db')
    cursor = conexion.cursor()
    cursor.execute(f"PRAGMA key='{clave}'")  # Establecer la clave de encriptación

    # Verificar si la cédula y la clave única están en la base de datos
    cursor.execute("SELECT * FROM estudiantes WHERE cedula=? AND clave_unica=?", (cedula, clave_unica))
    estudiante = cursor.fetchone()

    # Cerrar la conexión
    conexion.close()

    return estudiante


# Página de inicio de sesión para el usuario principal
@app.route('/', methods=['GET', 'POST'])
def login_usuario_principal():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        # Lógica de validación para el usuario principal (ajusta según tus necesidades)
        
        if verificar_presidente(usuario, contrasena):
            # Almacenar indicador de autenticación en la sesión
            session['autenticado_usuario_principal'] = True
            return redirect(url_for('login_estudiantes'))

        if usuario == 'MARVINCADENA' and contrasena == 'UTEQ1234':
            # Almacenar indicador de autenticación en la sesión
            session['autenticado_usuario_principal'] = True
            return redirect(url_for('login_estudiantes'))
        else:
            mensaje_error = 'Credenciales incorrectas. Inténtelo de nuevo.'
            return render_template('login_usuario_principal.html', mensaje_error=mensaje_error)

    return render_template('login_usuario_principal.html')


# Página de inicio de sesión para estudiantes
@app.route('/login_estudiantes', methods=['GET', 'POST'])
def login_estudiantes():
    # Verificar si el usuario principal está autenticado
    if not session.get('autenticado_usuario_principal', False):
        return redirect(url_for('login_usuario_principal'))

    if request.method == 'POST':
        cedula = request.form['cedula']
        clave_unica = request.form['clave_unica']

        # Lógica de validación con la base de datos
        estudiante = verificar_estudiante(cedula, clave_unica)

        # Verificar si la cédula ya ha votado
        if verificar_voto(cedula) == True:
            mensaje_error = 'Usted ya ha ejercido su voto.'
            return render_template('login_estudiantes.html', mensaje_error=mensaje_error)

        if estudiante:
            # Almacenar indicador de autenticación en la sesión
            session['autenticado'] = True
            session['cedula'] = cedula  # Agregar la cédula a la sesión
            print(f"Cédula: {cedula}, Autenticado: {session['autenticado']}")
            return redirect(url_for('votacion'))
        else:
            mensaje_error = 'Credenciales incorrectas. Inténtelo de nuevo.'
            return render_template('login_estudiantes.html', mensaje_error=mensaje_error)

    return render_template('login_estudiantes.html')
    

# Página de votación
@app.route('/votacion', methods=['GET', 'POST'])
def votacion():
    # Verificar si el usuario está autenticado y no ha votado
    if 'autenticado' not in session or session['autenticado'] is False or verificar_voto(session['cedula']) == True:
        return redirect(url_for('login_estudiantes'))

    if request.method == 'POST':
        # Lógica de votación aquí

        # Obtener la opción seleccionada del formulario
        opcion_seleccionada = request.form.get('opcion')

        # Verificar si se seleccionó una opción
        if not opcion_seleccionada:
            mensaje_error = 'Seleccione una opción antes de votar.'
            return render_template('votacion.html', mensaje_error=mensaje_error)

        guardar_voto(opcion_seleccionada, session['cedula'])  # Guardar el voto en la base de datos

        # Después de la lógica de votación, asegúrate de actualizar el estado de autenticación a False
        session['autenticado'] = False

        # Consultar la cantidad de votos por opción
        resultados = obtener_resultados()

        # Encontrar la opción con más votos
        ganador = max(resultados, key=lambda x: x[1])[0]

        # Mostrar la página de agradecimiento después de cada voto
        return render_template('agradecimiento.html', mensaje='Gracias por tu voto.', resultados=resultados, ganador=ganador)

    return render_template('votacion.html',opciones=obtener_candidatos())


# Página de agradecimiento después de votar
@app.route('/agradecimiento')
def agradecimiento():
    return render_template('agradecimiento.html')

# Página de resultados
@app.route('/resultados')
def mostrar_resultados():
    resultados, ganador, mensaje = generar_resultados()

    return render_template('resultados.html', resultados=resultados, ganador=ganador, mensaje=mensaje)

@app.route('/logout', methods=['POST'])
def logout():
    # Cerrar la sesión
    session.clear()
    return redirect(url_for('login_usuario_principal'))

@app.route('/admin')
def admin():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    cantidad_votos, opciones = obtener_votos()
    votos_x_hora, horas = votos_por_hora()
    return render_template('admin-index.html',
    votos=contar_votos(), 
    votantes=contar_votantes(), 
    cantidad_votos=cantidad_votos, 
    opciones=opciones,
    votos_por_hora=votos_x_hora,
    horas=horas
    )

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        # Lógica de validación para el usuario principal (ajusta según tus necesidades)
        if usuario == user_admin and contrasena == password_admin:
            # Almacenar indicador de autenticación en la sesión
            session['autenticado_admin'] = True
            return redirect(url_for('admin'))
        else:
            mensaje_error = 'Credenciales incorrectas. Inténtelo de nuevo.'
            return render_template('login_admin.html', mensaje_error=mensaje_error)

    return render_template('login_admin.html')

@app.route('/admin/candidatos', methods=['Get', 'POST'])
def candidatos():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    if request.method == 'POST':
        opcion = request.form['opcion']
        imagen_url = request.form['imagen_url']

        conexion = sqlcipher.connect('urna_digital.db')
        cursor = conexion.cursor()
        cursor.execute(f"PRAGMA key='{clave}'")

        cursor.execute("INSERT INTO opciones (opcion, imagen_url) VALUES (?, ?)", (opcion, imagen_url))

        conexion.commit()
        conexion.close()

        return redirect(url_for('candidatos'))

    return render_template('admin-candidatos.html', opciones=obtener_candidatos())

@app.route('/admin/candidatos/nuevo', methods=['Get'])
def candidatoNuevo():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    return render_template('candidato-nuevo.html')

@app.route('/admin/candidato/eliminar/<int:id>', methods=['DELETE'])
def eliminar_candidato(id):
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    conexion = sqlcipher.connect('urna_digital.db')
    cursor = conexion.cursor()
    cursor.execute(f"PRAGMA key='{clave}'")

    cursor.execute("DELETE FROM opciones WHERE id=?", (id,))

    conexion.commit()
    conexion.close()

    return redirect(url_for('candidatos'))

@app.route('/admin/estudiantes', methods=['Get', 'post'])
def estudiantes():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    if request.method == 'POST':
        cedula = request.form['cedula']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        carrera = request.form['carrera']
        curso = request.form['curso']


        conexion = sqlcipher.connect('urna_digital.db')
        cursor = conexion.cursor()
        cursor.execute(f"PRAGMA key='{clave}'")

        print(cedula, nombres, apellidos, carrera, curso)

        cursor.execute("INSERT INTO estudiantes (cedula, nombres, apellidos, carrera, curso, clave_unica) VALUES (?, ?, ?, ?, ?, ?)", (cedula, nombres, apellidos, carrera, curso, cedula))

        conexion.commit()
        conexion.close()

        return redirect(url_for('estudiantes'))

    return render_template('estudiantes.html', estudiantes=obtener_estudiantes())

@app.route('/admin/estudiante/nuevo', methods=['Get'])
def estudianteNuevo():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    return render_template('estudiante-nuevo.html')

@app.route('/admin/estudiante/presidente', methods=['Post'])
def presidente():
    if 'autenticado_admin' not in session or session['autenticado_admin'] is False:
        return redirect(url_for('login_admin'))

    data = request.get_json()
    estudiante_id = data['id']

    conexion = sqlcipher.connect('urna_digital.db')
    cursor = conexion.cursor()
    cursor.execute(f"PRAGMA key='{clave}'")

    cursor.execute("UPDATE estudiantes SET presidente = 1 WHERE id=?", (estudiante_id,))

    conexion.commit()
    conexion.close()

    return redirect(url_for('estudiantes'))

# Iniciar la aplicación
if __name__ == '__main__':
    # Inicializar la base de datos de votos al iniciar la aplicación
    init_db()
    app.run(debug=True)
