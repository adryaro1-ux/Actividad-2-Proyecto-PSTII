import pymysql
import os
import pytz
from datetime import datetime
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# --- Configuración de la Base de Datos ---
DB_HOST = os.getenv("DB_HOST", 'localhost')
DB_USER = os.getenv("DB_USER", 'root')
DB_PASSWORD = os.getenv("DB_PASSWORD", '')
DB_NAME = os.getenv("DB_DATABASE", 'data_sync_db') 

def crear_conexion():
    """Establece conexión y retorna diccionarios en lugar de tuplas."""
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor # Crucial para ver nombres en la tabla
        )
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

# --- 1. INICIALIZACIÓN DE TABLAS ---
def crear_tabla_si_no_existe():
    conexion = crear_conexion()
    if not conexion: return
    try:
        with conexion.cursor() as cursor:
            # Tabla para el Dólar
            cursor.execute('''CREATE TABLE IF NOT EXISTS tipo_cambio (
                id INT AUTO_INCREMENT PRIMARY KEY,
                valor DECIMAL(10,4) NOT NULL,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Tabla para Usuarios (Con ROL para gestión)
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL, 
                rol VARCHAR(50) NOT NULL DEFAULT 'Operador',
                activo BOOLEAN DEFAULT TRUE,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_login DATETIME NULL)''')
            
            # Dentro de crear_tabla_si_no_existe() en db.py añade:
            cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(50),
                accion VARCHAR(255),
                detalles TEXT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL)''')
            
            # Tabla para Reportes
            cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                numero_poliza VARCHAR(50), 
                nombre_apellido VARCHAR(255),
                cedula VARCHAR(50),
                contratante VARCHAR(255),
                num_control VARCHAR(50),
                proveedor VARCHAR(255),
                estado VARCHAR(100),
                patologia VARCHAR(255),
                monto DECIMAL(10, 2),
                tratamiento VARCHAR(255),
                observaciones TEXT,
                fecha_creado DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id))''')
        conexion.commit()
    finally:
        conexion.close()

# --- 2. VALOR DEL DÓLAR ---
def insertar_valor(valor, fecha_actualizacion):
    conn = crear_conexion()
    try:
        cursor = conn.cursor()
        # Ajustado a tu tabla REAL 'tipo_cambio' con solo 2 columnas manuales
        sql = "INSERT INTO tipo_cambio (valor, fecha_hora) VALUES (%s, %s)"
        
        # Enviamos solo los 2 datos que existen en tu tabla
        cursor.execute(sql, (valor, fecha_actualizacion))
        conn.commit()
        
        print(f"✅ VALOR REALMENTE GUARDADO EN tipo_cambio: {valor}")
    except Exception as e:
        print(f"❌ Error interno en la inserción: {e}")
    finally:
        cursor.close()
        conn.close()

def obtener_ultimo_historico():
    conn = None
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        # Seleccionamos como String para evitar errores de objetos Decimal/Float
        cursor.execute("SELECT CAST(valor AS CHAR) FROM tipo_cambio ORDER BY fecha_hora DESC LIMIT 1")
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            return float(resultado[0]) # Lo convertimos a float en Python
        return None
    except Exception as e:
        # Si sigue saliendo 0, imprimimos el tipo de error para debug
        print(f"DEBUG DB: {e}")
        return None
    finally:
        if conn: conn.close()

def obtener_ultimo_registro_completo():
    conn = None
    try:
        conn = crear_conexion()
        cursor = conn.cursor() 
        sql = "SELECT valor, fecha_hora FROM tipo_cambio ORDER BY fecha_hora DESC LIMIT 1"
        cursor.execute(sql)
        resultado = cursor.fetchone()
        
        if resultado:
            # Si es un diccionario, usamos las llaves. Si es tupla, usamos índices.
            if isinstance(resultado, dict):
                return {'valor': float(resultado['valor']), 'fecha_hora': resultado['fecha_hora']}
            else:
                return {'valor': float(resultado[0]), 'fecha_hora': resultado[1]}
        return None
    except Exception as e:
        print(f"❌ Error real en DB: {e}")
        return None
    finally:
        if conn: conn.close()

# --- 3. GESTIÓN DE USUARIOS (Para el Administrador) ---

def obtener_todos_los_usuarios():
    """El Admin usa esta función para gestionar la lista de usuarios."""
    conn = crear_conexion()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, rol, activo, fecha_registro FROM users")
            return cursor.fetchall()
    finally:
        conn.close()

def obtener_usuario_por_id(user_id):
    conn = crear_conexion()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def obtener_usuario_por_username(username):
    conn = crear_conexion()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
    finally:
        conn.close()

def crear_nuevo_usuario_db(username, password, rol, activo=True):
    conn = crear_conexion()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, rol, activo) VALUES (%s, %s, %s, %s)", 
                           (username, password, rol, activo))
            conn.commit()
            return True
    except: return False
    finally:
        conn.close()

def actualizar_usuario_db(user_id, data):
    conn = crear_conexion()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            # Si el Administrador envió una contraseña nueva
            if data.get('password') and data.get('password').strip() != "":
                sql = """UPDATE users 
                         SET username=%s, password=%s, rol=%s, activo=%s 
                         WHERE id=%s"""
                params = (data.get('username'), data.get('password'), 
                          data.get('rol'), data.get('activo'), user_id)
            else:
                # Si no hay contraseña nueva, solo actualizamos el resto
                sql = """UPDATE users 
                         SET username=%s, rol=%s, activo=%s 
                         WHERE id=%s"""
                params = (data.get('username'), data.get('rol'), 
                          data.get('activo'), user_id)
            
            cursor.execute(sql, params)
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Error al actualizar usuario: {e}")
        return False
    finally:
        conn.close()

def eliminar_usuario_db(user_id):
    conn = crear_conexion()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return True
    finally:
        conn.close()

# --- 4. REPORTES (Lógica de Visibilidad) ---

def obtener_reportes_por_usuario(user_id=None):
    """Si user_id es None, el Admin ve todo. Si no, solo lo del Operador."""
    conexion = crear_conexion()
    if not conexion: return []
    try:
        with conexion.cursor() as cursor:
            if user_id is None:
                cursor.execute("SELECT * FROM reports ORDER BY fecha_creado DESC")
            else:
                cursor.execute("SELECT * FROM reports WHERE user_id = %s ORDER BY fecha_creado DESC", (user_id,))
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_reporte_por_id(reporte_id):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM reports WHERE id = %s", (reporte_id,))
            return cursor.fetchone()
    finally:
        conexion.close()

def obtener_todos_los_reportes():
    """Retorna absolutamente todos los reportes de la base de datos."""
    conexion = crear_conexion()
    if not conexion: return []
    try:
        with conexion.cursor() as cursor:
            # Traemos todo y unimos con la tabla users para saber quién lo creó si es necesario
            sql = "SELECT * FROM reports ORDER BY fecha_creado DESC"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_reportes_por_fecha(fecha):
    """Filtra reportes por fecha usando la conexión de DolarSync."""
    conexion = crear_conexion() # Usamos tu función existente
    if not conexion: return []
    try:
        with conexion.cursor() as cursor:
            # Filtramos comparando solo la parte de la fecha (YYYY-MM-DD)
            query = "SELECT * FROM reports WHERE DATE(fecha_creado) = %s ORDER BY fecha_creado DESC"
            cursor.execute(query, (fecha,))
            return cursor.fetchall()
    finally:
        conexion.close()

def insertar_reporte(user_id, data):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        with conexion.cursor() as cursor:
            # Corregido: 12 columnas y 12 parámetros %s
            sql = """INSERT INTO reports (user_id, numero_poliza, nombre_apellido, cedula, contratante, num_control, 
                     proveedor, estado, patologia, monto_bs, monto_dolar, tratamiento, observaciones) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (
                user_id, data['numero_poliza'], data['nombre_apellido'], data['cedula'], data['contratante'],
                data['num_control'], data['proveedor'], data['estado'],
                data['patologia'], data['monto_bs'], data['monto_dolar'], 
                data['tratamiento'], data['observaciones']
            ))
            conexion.commit()
            return True
    finally:
        conexion.close()

def actualizar_reporte(reporte_id, user_id, data):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        with conexion.cursor() as cursor:
            # Actualizamos ambos montos
            sql = """UPDATE reports SET numero_poliza=%s nombre_apellido=%s, cedula=%s, contratante=%s, num_control=%s, 
                     proveedor=%s, estado=%s, patologia=%s, monto_bs=%s, monto_dolar=%s, tratamiento=%s, observaciones=%s 
                     WHERE id=%s"""
            cursor.execute(sql, (
                data['numero_poliza'], data['nombre_apellido'], data['cedula'], data['contratante'], 
                data['num_control'], data['proveedor'], data['estado'], 
                data['patologia'], data['monto_bs'], data['monto_dolar'], 
                data['tratamiento'], data['observaciones'], reporte_id
            ))
            conexion.commit()
            return True
    finally:
        conexion.close()

def eliminar_reporte(reporte_id, user_id):
    """Elimina si el reporte pertenece al usuario (Seguridad para Operadores)."""
    conn = crear_conexion()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM reports WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (reporte_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    finally: conn.close()

def eliminar_reporte_administrativo(reporte_id):
    conn = crear_conexion()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM reports WHERE id = %s"
            cursor.execute(sql, (reporte_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally: conn.close()

def actualizar_reporte_administrativo(reporte_id, data):
    """Actualiza cualquier reporte por su ID sin filtrar por usuario."""
    conn = crear_conexion()
    try:
        with conn.cursor() as cursor:
            # SQL actualizado con las dos columnas de dinero
            sql = """UPDATE reports SET 
                     numero_poliza=%s, nombre_apellido=%s, cedula=%s, contratante=%s, num_control=%s, 
                     proveedor=%s, estado=%s, patologia=%s, monto_dolar=%s, 
                     monto_bs=%s, tratamiento=%s, observaciones=%s 
                     WHERE id = %s"""
            
            cursor.execute(sql, (
                data['numero_poliza'],
                data['nombre_apellido'], 
                data['cedula'], 
                data['contratante'],
                data['num_control'], 
                data['proveedor'], 
                data['estado'],
                data['patologia'], 
                data['monto_dolar'],
                data['monto_bs'],     
                data['tratamiento'],
                data['observaciones'], 
                reporte_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error en actualización administrativa: {e}")
        return False
    finally:
        conn.close()

def obtener_todos_los_reportes():
    """Trae todos los reportes de la tabla para los Gerentes."""
    conn = crear_conexion()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM reports ORDER BY fecha_creado DESC"
            cursor.execute(sql)
            return cursor.fetchall()
    finally: conn.close()

def registrar_evento(user_id, username, accion, detalles=""):
    conn = crear_conexion()
    if not conn: return
    try:
        # Generamos la hora exacta de Venezuela
        zona_ve = pytz.timezone('America/Caracas')
        fecha_actual = datetime.now(zona_ve).strftime('%Y-%m-%d %H:%M:%S')

        with conn.cursor() as cursor:
            # Insertamos 'fecha_actual' manualmente en la columna fecha_hora
            sql = """INSERT INTO audit_logs (user_id, username, accion, detalles, fecha_hora) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (user_id, username, accion, detalles, fecha_actual))
            
            if accion == "Inicio de Sesión":
                sql_user = "UPDATE users SET ultimo_login = %s WHERE id = %s"
                cursor.execute(sql_user, (fecha_actual, user_id))
            
            conn.commit()
    except Exception as e:
        print(f"❌ Error en bitácora: {e}")
    finally:
        conn.close()