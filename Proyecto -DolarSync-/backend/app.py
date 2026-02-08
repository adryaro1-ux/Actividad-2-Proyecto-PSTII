import os
import requests
import urllib3
import pytz
import time
from functools import wraps
from flask import (
    Flask, jsonify, send_from_directory, send_file, abort,
    render_template, request, redirect, url_for, flash, session, make_response
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

import pandas as pd
from io import BytesIO
from fpdf import FPDF


# Configura tu zona horaria local
local_tz = pytz.timezone('America/Caracas') 

# Cuando guardes un log en la base de datos, usa esto:
fecha_actual = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

# Importaciones de DB
from sql.db import (
    crear_tabla_si_no_existe, 
    insertar_valor, 
    crear_conexion, 
    insertar_reporte,
    obtener_reportes_por_usuario,
    obtener_usuario_por_username,
    obtener_usuario_por_id, 
    obtener_todos_los_usuarios,
    crear_nuevo_usuario_db,
    actualizar_usuario_db,
    obtener_ultimo_registro_completo,
    obtener_reporte_por_id,
    actualizar_reporte,
    obtener_ultimo_historico,
    actualizar_reporte_administrativo,
    registrar_evento
)

# --- DEFINICIONES DE ROLES ---
ROLES_VALIDOS = ['Administrador', 'Gerente', 'Coordinador', 'Operador']


app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public')),
    static_url_path=''
)

# 1. Configuraciones de sesión
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.before_request
def configurar_sesion():
    session.permanent = False

# 2. Evitar que el navegador guarde la página en su memoria interna (Caché)
@app.after_request
def limpiar_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.after_request
def add_header(response):
    """
    Indica al navegador que no guarde caché para que no se pueda 
    acceder a páginas protegidas usando el botón 'atrás'.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/data_sync_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Log(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    accion = db.Column(db.String(100))
    detalles = db.Column(db.String(200))
    fecha_hora = db.Column(db.String(50))

last_heartbeat = {}

def check_for_disconnections():
    now = datetime.now()
    threshold = now - timedelta(seconds=60)
    
    for user_id, last_time in list(last_heartbeat.items()):
        if last_time < threshold:
            # --- CAMBIO AQUÍ: Buscar usuario manualmente ---
            # Como no usas User.query, usamos el current_user si coincide 
            # o una consulta simple a tu base de datos.
            
            # Si solo tienes un usuario activo a la vez, podemos usar:
            username_afectado = "Usuario Desconocido"
            
            # Intentamos obtener el nombre desde la DB con tu conexión manual
            conn = crear_conexion()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT username FROM usuarios WHERE id = %s", (user_id,))
                    res = cursor.fetchone()
                    if res:
                        username_afectado = res['username']
            finally:
                conn.close()

            # Guardamos el log usando el modelo Log (que SÍ es SQLAlchemy)
            nuevo_log = Log(
                username=username_afectado,
                accion="FALLA DE CONEXIÓN",
                detalles="Desconexión repentina detectada (posible falla de internet o luz).",
                fecha_hora=now.strftime('%d/%m/%Y %I:%M %p')
            )
            db.session.add(nuevo_log)
            db.session.commit()
            
            del last_heartbeat[user_id]

@app.route('/heartbeat', methods=['POST'])
@login_required
def heartbeat():
    # Esta línea guarda el momento exacto del último pulso del usuario
    # Asegúrate de tener definido 'last_heartbeat = {}' al inicio de tu app.py
    last_heartbeat[current_user.id] = datetime.now()
    return '', 204

@app.route('/api/audit')
@login_required
def obtener_bitacora():
    if current_user.rol != 'Administrador':
        return {"error": "No autorizado"}, 403
        
    conn = crear_conexion()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM audit_logs ORDER BY fecha_hora DESC LIMIT 100")
        logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

# Carga la clave secreta desde el entorno o usa un valor por defecto (IMPORTANTE)
app.secret_key = os.getenv("SECRET_KEY", "clave_de_desarrollo_insegura_por_favor_cambiar") 
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['JSON_AS_ASCII'] = False 

# --- CLASE USER ---
class User(UserMixin):
    def __init__(self, id, username, rol):
        self.id = str(id)
        self.username = username
        self.rol = rol 
        
# --- USER LOADER ---
@login_manager.user_loader
def load_user(user_id):
    usuario = obtener_usuario_por_id(user_id) 
    if usuario:
        return User(id=usuario['id'], username=usuario['username'], rol=usuario['rol']) 
    return None

@app.route('/logo')
def logo():
    ruta_logo = r'C:\xampp\htdocs\dolar-bcv-monitor\frontend\src\css\logo_sync.png'
    if os.path.exists(ruta_logo):
        return send_file(ruta_logo)
    return '', 404

# --- DECORADOR DE AUTORIZACIÓN PARA ADMINISTRADOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'Administrador':
            if request.path.startswith('/api/'):
                return jsonify({"mensaje": "Acceso denegado. Se requiere rol de Administrador."}), 403
            
            flash('Acceso denegado: Se requiere rol de Administrador.', 'danger')
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function

# --- RUTA DE LOGIN REVERTIDA A COMPARACIÓN SIMPLE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = obtener_usuario_por_username(username) 

        if user and user['password'] == password:
            if not user.get('activo'):
                # Registramos el intento fallido por estar suspendido
                registrar_evento(user['id'], username, "Intento Fallido", "Cuenta suspendida")
                return render_template('login.html', error="🚫 Cuenta suspendida.")

            # --- REGISTRO EXITOSO ---
            registrar_evento(user['id'], username, "Inicio de Sesión", "Acceso exitoso")
            
            usuario_obj = User(user['id'], user['username'], user['rol'])
            login_user(usuario_obj, remember=False)
            return redirect(url_for('index'))

        return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    ultimos_logs = []
    
    if current_user.rol == 'Administrador':
        conn = crear_conexion()
        try:
            with conn.cursor() as cursor:
                # Consultamos los últimos 3 movimientos
                cursor.execute("""
                    SELECT username, accion, detalles, fecha_hora 
                    FROM audit_logs 
                    ORDER BY id DESC 
                    LIMIT 3
                """)
                ultimos_logs = cursor.fetchall()
                
                # CORRECCIÓN: Quitamos el strftime porque ya es un string
                for log in ultimos_logs:
                    if log['fecha_hora']:
                        # Convertimos a string por seguridad, sin formatear
                        log['fecha_hora'] = str(log['fecha_hora'])
        finally:
            conn.close()

    # Enviamos la variable 'logs' al template
    return render_template('index.html', logs=ultimos_logs)

@app.route('/reports')
@login_required
def reports():
    # Bloqueo explícito para administradores
    if current_user.rol == 'Administrador':
        flash('El Administrador no tiene permisos para crear reportes.', 'danger')
        return redirect(url_for('index'))
    return render_template('reports.html')

# ----------------------------------------------------------------------------------
# 🔑 RUTA ÚNICA DEL PANEL DE ADMINISTRACIÓN (SOLUCIONA EL ERROR DE DUPLICIDAD)
# ----------------------------------------------------------------------------------
@app.route("/admin-dashboard")
@login_required
@admin_required 
def admin_dashboard():
    """Muestra la interfaz de gestión de usuarios (CRUD) para administradores."""
    try:
        return render_template('admin_dashboard.html')
    except Exception as e:
        # En caso de que persista el error de TemplateNotFound
        flash(f'Error al cargar plantilla: {e}', 'danger')
        return redirect(url_for('index')) # Redirige al inicio si hay un error

# --- RUTAS DE GESTIÓN DE USUARIOS (CRUD API) ---

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
@admin_required 
def gestionar_usuarios_api():
    
    if request.method == 'GET':
        try:
            # Elimina el password antes de enviar los datos al frontend
            usuarios = [u for u in obtener_todos_los_usuarios() if u.pop('password', None) or True]
            return jsonify(usuarios), 200
        except Exception as e:
            return jsonify({"mensaje": f"Error al listar usuarios: {e}"}), 500

    elif request.method == 'POST':
        # CREAR NUEVO USUARIO
        data = request.get_json()
        username = data.get('username')
        password = data.get('password') 
        rol = data.get('rol')
        activo = data.get('activo', True)
        
        if not username or not password or rol not in ROLES_VALIDOS:
            return jsonify({"mensaje": "Datos inválidos o rol no reconocido."}, 400)

        try:
            if crear_nuevo_usuario_db(username, password, rol, activo):
                registrar_evento(current_user.id, current_user.username, "CREACIÓN", f"Usuario '{username}' creado exitosamente.")
                return jsonify({"mensaje": f"Usuario '{username}' creado exitosamente."}), 201
            else:
                return jsonify({"mensaje": "El nombre de usuario ya existe o error de DB."}, 409)
        except Exception as e:
            return jsonify({"mensaje": f"Error interno al crear usuario: {e}"}), 500

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required 
def modificar_usuario_api(user_id):
    if request.method == 'GET':
        usuario = obtener_usuario_por_id(user_id)
        if usuario:
            usuario.pop('password', None) 
            return jsonify(usuario), 200
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    elif request.method == 'PUT':
        data = request.get_json()
        
        # 1. OBTENER DATOS ACTUALES (Antes de cambiar nada)
        usuario_previo = obtener_usuario_por_id(user_id)
        if not usuario_previo:
            return jsonify({"mensaje": "Usuario no encontrado."}), 404

        # 2. INTENTAR ACTUALIZACIÓN
        if actualizar_usuario_db(user_id, data):
            target_username = usuario_previo['username']
            
            # --- LÓGICA DE AUDITORÍA SELECTIVA ---

            # Caso A: ¿Cambió el Rol? Solo registra si el rol nuevo es distinto al que ya tenía
            nuevo_rol = data.get('rol')
            if nuevo_rol and nuevo_rol != usuario_previo.get('rol'):
                registrar_evento(
                    current_user.id, 
                    current_user.username, 
                    "NIVEL DE ACCESO", 
                    f"Cambió Rol de '{target_username}' a {nuevo_rol}"
                )

            # Caso B: ¿Cambió el Estado? Solo registra si el switch de activo cambió
            # Convertimos a bool para asegurar que la comparación sea exacta
            nuevo_estado_bool = data.get('activo')
            if nuevo_estado_bool is not None and nuevo_estado_bool != bool(usuario_previo.get('activo')):
                estado_texto = "HABILITADO" if nuevo_estado_bool else "SUSPENDIDO"
                registrar_evento(
                    current_user.id, 
                    current_user.username, 
                    "CONTROL DE ACCESO", 
                    f"El Usuario '{target_username}' ha sido {estado_texto}"
                )

            return jsonify({"mensaje": "Usuario actualizado exitosamente."}), 200
        
        return jsonify({"mensaje": "No se realizaron cambios."}), 500

    # --- MÉTODO PUT: Actualizar reporte (Gerentes/Coordinadores) ---
    elif request.method == 'PUT':
        if current_user.rol == 'Operador':
            return jsonify({"mensaje": "Acceso denegado: Operadores no pueden editar"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"mensaje": "Datos inválidos"}), 400

        # Mapeamos los campos que vienen del Frontend (JavaScript)
        data_db = {
            'numero_poliza': data.get('numero_poliza'),
            'nombre_apellido': data.get('nombre_apellido') or data.get('nombreApellido'),
            'cedula': data.get('cedula'),
            'contratante': data.get('contratante'),
            'num_control': data.get('num_control') or data.get('numControl'),
            'proveedor': data.get('proveedor'),
            'estado': data.get('estado'),
            'patologia': data.get('patologia'),
            'monto': float(data.get('monto') or 0), 
            'tratamiento': data.get('tratamiento'),
            'observaciones': data.get('observaciones')
        }

        # Llamamos a la función administrativa que agregamos a db.py e importamos
        if actualizar_reporte_administrativo(user_id, data_db):
            return jsonify({"mensaje": "Reporte actualizado con éxito."}), 200
        else:
            return jsonify({"mensaje": "No se encontró el reporte o no hubo cambios."}), 404
        

@app.route('/gestion-accesos')
@login_required
def view_audit():
    # 1. Seguridad: Solo administradores
    if current_user.rol != 'Administrador':
        return redirect(url_for('index'))
    
    # 2. Consultar TODOS los registros de la tabla Log
    # .order_by(Log.id.desc()) hace que lo más nuevo salga arriba
    logs_registrados = Log.query.order_by(Log.id.desc()).all()
    
    # 3. Pasar los logs a la plantilla audit.html
    return render_template('audit.html', logs=logs_registrados)

@app.route('/api/audit-logs')
@login_required
def get_audit_logs():
    # 1. Verificación de seguridad
    if current_user.rol != 'Administrador':
        return jsonify([]), 403
    
    try:
        # 2. Consulta usando SQLAlchemy (más rápido y limpio)
        # Esto consulta la tabla 'audit_logs' gracias al __tablename__ que pusimos antes
        logs = Log.query.order_by(Log.id.desc()).limit(200).all()
        
        # 3. Formateamos la respuesta
        logs_list = []
        for l in logs:
            logs_list.append({
                "username": l.username,
                "accion": l.accion,
                "detalles": l.detalles,
                "fecha_hora": str(l.fecha_hora) # Convertimos a string para evitar errores de fecha
            })
            
        return jsonify(logs_list)
        
    except Exception as e:
        print(f"Error cargando logs: {e}")
        return jsonify({"error": "No se pudieron cargar los registros"}), 500

# --- Rutas de Reportes (Se mantienen) ---

@app.route('/api/reports', methods=['POST'])
@login_required
def crear_reporte():
    # 1. Validación de Seguridad (Solo Operadores crean)
    if current_user.rol != 'Operador':
        return jsonify({"mensaje": "Acceso denegado: Su rol no permite crear nuevos reportes."}), 403

    # 2. Obtener datos
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se recibieron datos"}), 400

    try:
        # 3. Preparación de datos (Aseguramos que no falten llaves para evitar errores en db.py)
        # Importante: el HTML usa 'estado_paciente' o 'estado', lo normalizamos aquí:
        data_normalizada = {
            'numero_poliza': data.get('numero_poliza'),
            'nombre_apellido': data.get('nombre_apellido'),
            'cedula': data.get('cedula'),
            'contratante': data.get('contratante'),
            'num_control': data.get('num_control'),
            'proveedor': data.get('proveedor'),
            'estado': data.get('estado') or data.get('estado_paciente'),
            'patologia': data.get('patologia'),
            'monto_dolar': float(data.get('monto_dolar') or 0),
            'monto_bs': float(data.get('monto_bs') or 0),
            'tratamiento': data.get('tratamiento') or "", # Evitamos que sea None
            'observaciones': data.get('observaciones') or ""
        }

        # 4. LLAMADA CORRECTA (Pasamos el ID y luego el Diccionario)
        # Esta es la parte que faltaba: pasar current_user.id como primer argumento
        if insertar_reporte(current_user.id, data_normalizada):
            registrar_evento(current_user.id, current_user.username, "CREACIÓN", f"Reporte creado para paciente: {data_normalizada['nombre_apellido']}")
            return jsonify({"mensaje": "Reporte guardado exitosamente"}), 201
        
        return jsonify({"mensaje": "Error interno al procesar en la base de datos"}), 500

    except Exception as e:
        print(f"ERROR CRÍTICO: {str(e)}")
        return jsonify({"mensaje": f"Error de formato: {str(e)}"}), 400
    
@app.route('/api/reporte/<int:id>', methods=['PUT'])
@login_required
def editar_reporte(id):
    # 1. Verificación de permisos
    if current_user.rol not in ['Gerente', 'Coordinador']:
        return jsonify({"error": "No tiene permisos"}), 403

    try:
        data = request.json
        # 2. Mapeamos los campos EXACTOS de tu base de datos
        data_db = {
            'numero_poliza': data.get('numero_poliza'),
            'nombre_apellido': data.get('nombre_apellido'),
            'cedula': data.get('cedula'),
            'contratante': data.get('contratante'),
            'proveedor': data.get('proveedor'),
            'estado': data.get('estado'),
            'patologia': data.get('patologia'),
            'monto_dolar': float(data.get('monto_dolar') or 0),
            'monto_bs': float(data.get('monto_bs') or 0),
            'observaciones': data.get('observaciones'),
            'num_control': data.get('num_control'),
            'tratamiento': data.get('tratamiento') or "N/A"
        }

        # 3. Llamada a la función de la base de datos
        if actualizar_reporte_administrativo(id, data_db):
            registrar_evento(current_user.id, current_user.username, "EDICIÓN", f"Editó reporte ID: {id} (Paciente: {data_db['nombre_apellido']})")
            return jsonify({"status": "success", "message": "Reporte actualizado"}), 200
        else:
            return jsonify({"error": "No se pudo actualizar"}), 404

    except Exception as e:
        print(f"Error al editar: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports', methods=['POST'])
@login_required
def guardar_reporte():
    # Bloqueo para Administrador
    if current_user.rol == 'Administrador':
        return jsonify({'mensaje': 'El admin no crea reportes', 'status': 'error'}), 403

    # Intentar obtener datos de JSON o de Formulario
    if request.is_json:
        data_input = request.get_json()
    else:
        data_input = request.form

    try:
        data_db = {
            'numero_poliza': data_input.get('numero_poliza'),
            'nombre_apellido': data_input.get('nombre_apellido') or data_input.get('nombreApellido'),
            'cedula': data_input.get('cedula'),
            'contratante': data_input.get('contratante'),
            'num_control': data_input.get('num_control') or data_input.get('numControl'),
            'proveedor': data_input.get('proveedor'),
            'estado': data_input.get('estado'),
            'patologia': data_input.get('patologia'),
            'monto_dolar': float(data_input.get('monto_dolar') or 0),
            'monto_bs': float(data_input.get('monto_bs') or 0),
            'tratamiento': data_input.get('tratamiento') or "N/A",
            'observaciones': data_input.get('observaciones'),
            'usuario_id': current_user.id
        }

        if crear_reporte(data_db):
            return jsonify({'status': 'success', 'mensaje': 'Reporte guardado correctamente'}), 201
        else:
            return jsonify({'status': 'error', 'mensaje': 'Error en base de datos'}), 500

    except Exception as e:
        print(f"Error al guardar reporte: {e}")
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

        # VALIDACIÓN CRÍTICA: Si el nombre sigue siendo None, lanzamos error antes de ir a la DB
        if not data_db['nombre_apellido']:
            return jsonify({'mensaje': 'El nombre del paciente es obligatorio', 'status': 'error'}), 400

        usuario_id = int(current_user.id)
        exito = insertar_reporte(usuario_id, data_db)

        if exito:
            return jsonify({'mensaje': 'Reporte guardado con éxito', 'status': 'success'}), 201
        else:
            return jsonify({'mensaje': 'Error al insertar en la base de datos', 'status': 'error'}), 500

    except Exception as e:
        print(f"❌ Error procesando el reporte: {e}")
        return jsonify({'mensaje': f'Error interno: {str(e)}', 'status': 'error'}), 500


@app.route('/api/reportes_usuario', methods=['GET'])
@login_required
def reportes_usuario():
    try:
        # 1. Definimos quién es el usuario y su rol
        usuario_id = int(current_user.id)
        rol_usuario = current_user.rol

        # 2. Lógica de filtrado por Rol
        if rol_usuario in ['Gerente', 'Coordinador']:
            # Estos roles ven TODO
            from sql.db import obtener_todos_los_reportes
            reportes = obtener_todos_los_reportes()
        elif rol_usuario == 'Operador':
            # El operador solo ve lo suyo
            reportes = obtener_reportes_por_usuario(usuario_id)
        else:
            # El Administrador (u otros) no ven nada
            return jsonify([]), 200

        # 3. Formateo de datos (Fecha y Monto)
        reportes_formateados = []
        for r in reportes:
            if 'fecha_creado' in r and r['fecha_creado']:
                r['fecha_creado'] = r['fecha_creado'].strftime('%Y-%m-%d %H:%M:%S')
            
            if 'monto' in r:
                r['monto'] = float(r['monto']) 
                
            reportes_formateados.append(r)

        return jsonify(reportes_formateados)

    except Exception as e:
        print(f"Error al obtener reportes: {e}")
        return jsonify({'error': 'Error interno al consultar reportes'}), 500

@app.route('/api/reporte/<int:reporte_id>', methods=['GET', 'PUT'])
@login_required
def gestionar_reporte(reporte_id):
    rol_actual = current_user.rol

    # --- MÉTODO GET: Ver detalle ---
    # Permite a los Gerentes/Coordinadores obtener los datos para llenar el formulario de edición
    if request.method == 'GET':
        reporte = obtener_reporte_por_id(reporte_id)
        if reporte:
            if 'fecha_creado' in reporte and reporte['fecha_creado']:
                reporte['fecha_creado'] = reporte['fecha_creado'].strftime('%Y-%m-%d %H:%M:%S')
            if 'monto' in reporte:
                reporte['monto'] = float(reporte['monto'])
            return jsonify(reporte), 200
        return jsonify({"mensaje": "No encontrado"}), 404

    # --- MÉTODO PUT: Actualizar ---
    # Solo Gerentes y Coordinadores pueden entrar aquí
    elif request.method == 'PUT':
        if rol_actual not in ['Gerente', 'Coordinador']:
            return jsonify({"mensaje": "Acceso denegado. Solo personal administrativo puede editar."}), 403
        
        data = request.get_json()
        data_db = {
            'numero_poliza': data.get('numero_poliza'),
            'nombre_apellido': data.get('nombre_apellido') or data.get('nombreApellido'),
            'cedula': data.get('cedula'),
            'contratante': data.get('contratante'),
            'num_control': data.get('num_control') or data.get('numControl'),
            'proveedor': data.get('proveedor'),
            'estado': data.get('estado'),
            'patologia': data.get('patologia'),
            'monto': float(data.get('monto', 0)), 
            'tratamiento': data.get('tratamiento'),
            'observaciones': data.get('observaciones')
        }

        # Actualización administrativa (sin restricción de usuario_id del creador)
        if actualizar_reporte_administrativo(reporte_id, data_db):
            return jsonify({"mensaje": "Reporte actualizado con éxito."}), 200
        return jsonify({"mensaje": "No se pudo actualizar el registro."}), 404

@app.route('/api/descargar_registro/<int:reporte_id>')
@login_required
def descargar_registro(reporte_id):
    if current_user.rol != 'Gerente':
        return jsonify({"mensaje": "Acceso denegado. Solo el Gerente puede descargar reportes"}), 403

    try:
        r = obtener_reporte_por_id(reporte_id)
        if not r:
            return "Reporte no encontrado", 404

        # Auditoría posicional (sin nombres de argumentos para evitar el error)
        registrar_evento(current_user.id, current_user.username, "Descarga de Reporte", f"PDF: {r.get('cedula')}")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 112, 209)
        pdf.cell(0, 10, "DOLARSYNC - COMPROBANTE OFICIAL", 0, 1, 'C')
        pdf.ln(10)

        # Cuerpo del PDF
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        
        campos = [
            ('Numero de Poliza', r.get('numero_poliza')),
            ("Paciente", r.get('nombre_apellido')),
            ("Cédula", r.get('cedula')),
            ("Monto en Bs", f"Bs. {float(r.get('monto_bs', 0)):,.2f}"),
            ("Monto en $", f"$ {float(r.get('monto_dolar', 0)):,.2f}"),
            ("Tratamiento", r.get('tratamiento')),
            ("Observaciones", r.get('observaciones')),
            ("Fecha Reg.", str(r.get('fecha_creado')))
        ]

        for label, valor in campos:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(50, 10, f"{label}:", 1)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f" {valor}", 1, 1)

        output = BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        output.write(pdf_bytes)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Reporte_{r.get('cedula')}.pdf"
        )

    except Exception as e:
        print(f"Error crítico: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/descargar_reportes')
@login_required
def descargar_reportes():
    if current_user.rol != 'Gerente':
        return jsonify({"mensaje": "Acceso denegado"}), 403

    fecha_filtro = request.args.get('fecha')

    try:
        from sql.db import obtener_reportes_por_fecha
        registrar_evento(current_user.id, current_user.username, "Exportación Excel", f"Descargó reporte de fecha: {fecha_filtro}")

        datos = obtener_reportes_por_fecha(fecha_filtro)

        if not datos:
            return jsonify({"mensaje": "No hay reportes para esta fecha"}), 404

        df = pd.DataFrame(datos)

        # 1. Quitar la columna del ID de usuario (X roja)
        # Probamos con varios nombres comunes por si acaso
        for col in ['user_id', 'id_usuario', 'usuario_id']:
            if col in df.columns:
                df = df.drop(columns=[col])
            
        # 2. Renombrar columnas (Verde y demás)
        df = df.rename(columns={
            'id': 'N° Registro',
            'numero_poliza': 'Numero de Poliza',
            'nombre_apellido': 'Paciente',
            'cedula': 'Cédula',
            'contratante': 'Contratante',
            'num_control': 'N° Control',
            'proveedor': 'Proveedor',
            'estado': 'Estado del Paciente',
            'patologia': 'Patología',
            'monto_dolar': 'Monto ($)',
            'monto_bs': 'Monto (Bs.)',
            'tratamiento': 'Tratamiento',
            'observaciones':'Observaciones',
            'fecha_creado': 'Fecha'
        })

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Reportes')
            worksheet = writer.sheets['Reportes']
            
            # 1. Definimos un ancho MÍNIMO para cada columna (Bien estiradas)
            # Esto asegura que de entrada se vean grandes
            column_widths = {
                'A': 20,  # N° Registro
                'B': 25,  # Numero de Poliza
                'C': 40,  # Paciente (Nombre completo)
                'D': 20,  # Cédula
                'E': 30,  # Contratante
                'F': 20,  # N° Control
                'G': 30,  # Proveedor
                'H': 30,  # Estado del Paciente
                'I': 30,  # Patología
                'J': 20,  # Monto (Bs.)
                'K': 20,  # Monto ($)
                'L': 80,  # TRATAMIENTO (Súper estirado a los lados)
                'M': 80,  # OBSERVACIONES (Súper estirado a los lados)
                'N': 25   # Fecha
            }
            
            for column_letra, width in column_widths.items():
                if column_letra in worksheet.column_dimensions:
                    worksheet.column_dimensions[column_letra].width = width

            # 2. TRUCO DE AUTO-ESTIRADO DINÁMICO
            # Esto recorre cada columna y, si hay un texto más largo que el ancho fijo,
            # estira la celda un poco más.
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter # Obtiene la letra A, B, C...
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Si el contenido es más largo que nuestro valor fijo, estiramos más
                adjusted_width = (max_length + 2)
                if adjusted_width > worksheet.column_dimensions[column].width:
                    # Ponemos un tope de 100 para que no sea infinito
                    worksheet.column_dimensions[column].width = min(adjusted_width, 100)

        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'Reporte_{fecha_filtro}.xlsx'
        )

    except Exception as e:
        print(f"❌ Error al generar Excel: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/log_closure', methods=['POST'])
@login_required
def log_closure():
    usuario_id = current_user.id
    username = current_user.username
    
    # Esperamos 5 segundos antes de registrar
    # Si el usuario solo refrescó, el 'heartbeat' ya habrá actualizado su estado
    time.sleep(5) 
    
    ahora = datetime.now()
    ultimo_pulso = last_heartbeat.get(usuario_id)

    # Si el último pulso fue hace más de 10 segundos, es que REALMENTE cerró
    if ultimo_pulso is None or (ahora - ultimo_pulso).total_seconds() > 10:
        try:
            nuevo_log = Log(
                username=username,
                accion="CIERRE DE SESIÓN",
                detalles="Sesión terminada (Cierre de pestaña/navegador)",
                fecha_hora=ahora.strftime('%Y-%m-%d %H:%M:%S')
            )
            db.session.add(nuevo_log)
            db.session.commit()
        except Exception as e:
            print(f"Error: {e}")
            
    return '', 204
    
    
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # 1. REGISTRO EN BITÁCORA (Debe ir antes de logout_user)
    try:
        registrar_evento(
            current_user.id, 
            current_user.username, 
            "Cierre de Sesión", 
            "Sesión finalizada por el usuario"
        )
    except Exception as e:
        print(f"⚠️ Error al registrar evento de logout: {e}")

    # 2. Flask-Login cierra la sesión del usuario
    logout_user()
    
    # 3. Limpiamos el diccionario de sesión de Flask
    session.clear()
    
    # 4. Preparamos la respuesta para redirigir
    response = make_response(redirect(url_for('login')))
    
    # 5. Forzamos la limpieza de la cookie de sesión en el navegador
    response.set_cookie('session', '', expires=0)
    
    # 6. Cabeceras de seguridad para evitar caché (Back Button protection)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    flash("Has cerrado sesión exitosamente.", "success")
    return response

# --- Rutas de Utilidad (Se mantienen) ---

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.static_folder),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BCV_URL = 'https://www.bcv.org.ve/'

def obtener_valor_dolar_bcv():
    # ... (Se mantiene el código de scraping BCV) ...
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(BCV_URL, headers=headers, verify=False, timeout=20)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Timeout excedido al conectar con BCV.")
        return None
    except requests.RequestException as e:
        print(f"Error al acceder al BCV: {e}")
        return None

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    dolar_div = soup.find('div', id='dolar')
    if dolar_div:
        strong_tag = dolar_div.find('strong')
        if strong_tag and strong_tag.text:
            match = re.search(r'(\d+,\d+)', strong_tag.text)
            if match:
                valor = match.group(1).replace(',', '.')
                try:
                    return round(float(valor), 2)
                except Exception as e:
                    print(f"Error al convertir valor extraído: {e}")

    match = re.search(r'USD.*?(\d+,\d+)', html)
    if match:
        valor = match.group(1).replace(',', '.')
        try:
            return round(float(valor), 4)
        except Exception as e:
            print(f"Error al convertir valor con regex USD: {e}")

    print("No se encontró la tasa del dólar en el HTML del BCV.")
    return None

def insertar_si_no_actualizado_en_24h(valor_nuevo):
    conexion = crear_conexion()
    if not conexion: return

    insertar = False
    try:
        with conexion.cursor() as cursor:
            # 1. Consultamos el último registro
            cursor.execute("SELECT valor, fecha_hora FROM tipo_cambio ORDER BY fecha_hora DESC LIMIT 1")
            ultimo = cursor.fetchone()
            
            ahora = datetime.now()

            if ultimo is None:
                # Si la tabla está vacía, hay que insertar el primero
                insertar = True
            else:
                # ACCESO SEGURO: Usamos índices [0] y [1] para evitar el KeyError
                # Si tu cursor es de diccionario, usamos .get() o las llaves
                val_db = float(ultimo[0]) if not isinstance(ultimo, dict) else float(ultimo['valor'])
                fecha_db = ultimo[1] if not isinstance(ultimo, dict) else ultimo['fecha_hora']
                
                # 2. LA RESTRICCIÓN: 
                # Solo inserta si el valor cambió Y han pasado más de 24 horas
                diferencia_tiempo = ahora - fecha_db
                
                if valor_nuevo != val_db and diferencia_tiempo > timedelta(hours=24):
                    insertar = True
                    print(f"✅ Han pasado {diferencia_tiempo}. Procediendo a insertar nuevo valor.")
                else:
                    print(f"⏳ No se inserta: El valor es igual o no han pasado 24h (Faltan: {timedelta(hours=24) - diferencia_tiempo})")

        # 3. Ejecución de la inserción
        if insertar:
            # Usamos la función que ya definimos antes que recibe (valor, fecha)
            fecha_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
            insertar_valor(valor_nuevo, fecha_str)
            
    except Exception as e:
        print(f"❌ Error en lógica de 24h: {e}")
    finally:
        conexion.close()

#API DOLAR#

# --- COLOCA ESTO FUERA DE LA FUNCIÓN (ARRIBA DEL TODO) ---
YA_GUARDADO_HOY = False 

@app.route('/api/dolar')
@login_required
def get_dolar_api():
    try:
        # 1. Intentamos extraer el valor actual del BCV
        valor_bcv = obtener_valor_dolar_bcv()
        
        if valor_bcv:
            # --- CASO CON INTERNET: Procesamos y guardamos si cambió ---
            valor_limpio = round(float(str(valor_bcv).replace(',', '.')), 2)
            fecha_actual_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ultimo_registro = obtener_ultimo_registro_completo()
            
            if ultimo_registro is None:
                insertar_valor(valor_limpio, fecha_actual_str)
                print(f"🚀 Base de datos vacía. Iniciada con: {valor_limpio}")
            else:
                ultimo_valor_db = float(ultimo_registro['valor'])
                if valor_limpio != ultimo_valor_db:
                    insertar_valor(valor_limpio, fecha_actual_str)
                    print(f"📈 ¡CAMBIO DETECTADO! Nuevo valor: {valor_limpio}")
                else:
                    print(f"😴 Sin cambios. El valor sigue siendo {valor_limpio}")

            return jsonify({'price': "{:.2f}".format(valor_limpio), 'source': 'bcv_live'})
            
        else:
            # Si obtener_valor_dolar_bcv() devuelve None o False sin lanzar excepción
            raise Exception("BCV devolvió vacío")

    except Exception as e:
        # --- CASO SIN INTERNET O FALLO DE BCV ---
        print(f"⚠️ Error de conexión/scraping ({e}). Buscando respaldo en DB...")
        ultimo_respaldo = obtener_ultimo_registro_completo()
        
        if ultimo_respaldo:
            return jsonify({
                'price': "{:.2f}".format(ultimo_respaldo['valor']),
                'source': 'cache_db',
                'offline': True  # <--- Agregamos esta señal
            })
        else:
            # Si ni siquiera hay nada en la base de datos
            return jsonify({'error': 'No hay conexión ni datos previos'}), 500
    
@app.route('/api/ultimo', methods=['GET'])
@login_required
def ultimo_valor():
    conexion = crear_conexion()
    if not conexion: return jsonify({'error': 'Error de conexión a DB'}), 500
    
    resultado = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT valor, fecha_hora FROM tipo_cambio ORDER BY fecha_hora DESC LIMIT 1")
            resultado = cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener último valor: {e}")
    finally:
        conexion.close()

    if resultado:
        valor = float(resultado['valor'])
        fecha_hora = resultado['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'valor': valor, 'fecha_hora': fecha_hora})
    else:
        return jsonify({'error': 'Sin registros en base de datos'}), 404

@app.route('/api/historico', methods=['GET'])
@login_required
def historico():
    conexion = crear_conexion()
    if not conexion: return jsonify({'error': 'Error de conexión a DB'}), 500

    filas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT valor, fecha_hora FROM tipo_cambio ORDER BY fecha_hora DESC LIMIT 50")
            filas = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener histórico: {e}")
    finally:
        conexion.close()

    historico_list = []
    for fila in filas:
        historico_list.append({
            "valor": float(fila['valor']), 
            "fecha_hora": fila['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(historico_list)

@app.route('/<path:path>')
@login_required
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    try:
        crear_tabla_si_no_existe()
    except Exception as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        
    app.run(debug=True, host='0.0.0.0', port=5000)