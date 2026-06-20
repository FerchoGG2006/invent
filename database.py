import sqlite3
import os
import sys
import hashlib

def obtener_ruta_db():
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado por PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script de Python estándar
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "inventario_barberia.db")

DB_NAME = obtener_ruta_db()

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre TEXT NOT NULL,
                categoria TEXT,
                precio_costo REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                stock_minimo INTEGER DEFAULT 3,
                imagen_ruta TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                precio_costo_unitario REAL NOT NULL,
                total REAL NOT NULL,
                metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
                fecha TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                cliente_nombre TEXT,
                cliente_identificacion TEXT,
                impuestos REAL DEFAULT 0.0,
                codigo_fiscal TEXT,
                fiscal_qr_url TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                nombre_empresa TEXT NOT NULL,
                propietario TEXT,
                telefono TEXT,
                direccion TEXT,
                mensaje_ticket TEXT DEFAULT '¡Gracias por su compra!',
                impresora_ticket TEXT,
                pais_operacion TEXT DEFAULT 'Otro / Ninguno (Solo local)'
            )
        """)
        try:
            cursor.execute("ALTER TABLE configuracion ADD COLUMN impresora_ticket TEXT;")
        except sqlite3.OperationalError:
            pass # Ya existe la columna
        try:
            cursor.execute("ALTER TABLE configuracion ADD COLUMN pais_operacion TEXT DEFAULT 'Otro / Ninguno (Solo local)';")
        except sqlite3.OperationalError:
            pass
        for col_name, col_type in [("cliente_nombre", "TEXT"), ("cliente_identificacion", "TEXT"), ("impuestos", "REAL DEFAULT 0.0"), ("codigo_fiscal", "TEXT"), ("fiscal_qr_url", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE ventas ADD COLUMN {col_name} {col_type};")
            except sqlite3.OperationalError:
                pass
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                clave TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'Administrador'
            )
        """)
        conn.commit()



def reiniciar_base_datos():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DROP TABLE IF EXISTS ventas;")
        cursor.execute("DROP TABLE IF EXISTS productos;")
        # NO borrar la tabla configuracion para conservar los datos del negocio
        conn.commit()
    init_db()

def obtener_productos(filtro=""):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute("""
                SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, imagen_ruta 
                FROM productos 
                WHERE nombre LIKE ? OR categoria LIKE ? OR codigo LIKE ?
            """, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, imagen_ruta FROM productos")
        return cursor.fetchall()

def insertar_producto(codigo, nombre, categoria, costo, venta, stock, min_stock, imagen_ruta=""):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, imagen_ruta) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo if codigo.strip() else None, nombre, categoria, costo, venta, stock, min_stock, imagen_ruta))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def modificar_stock(producto_id, cantidad):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET stock = MAX(0, stock + ?) WHERE id = ?", (cantidad, producto_id))
        conn.commit()

def registrar_venta(producto_id, cantidad, precio_unitario, metodo_pago, cliente_nombre="", cliente_identificacion="", impuestos=0.0, codigo_fiscal="", fiscal_qr_url=""):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            # Verificar stock disponible y capturar precio de costo actual
            cursor.execute("SELECT stock, precio_costo FROM productos WHERE id = ?", (producto_id,))
            res = cursor.fetchone()
            if not res:
                return False, "Producto no encontrado."
            stock_actual = res[0]
            precio_costo_actual = res[1]
            
            if stock_actual < cantidad:
                return False, f"Stock insuficiente. Disponible: {stock_actual}"
            
            total = cantidad * precio_unitario
            # Registrar en tabla ventas con el costo y campos fiscales
            cursor.execute("""
                INSERT INTO ventas (producto_id, cantidad, precio_unitario, precio_costo_unitario, total, metodo_pago, cliente_nombre, cliente_identificacion, impuestos, codigo_fiscal, fiscal_qr_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (producto_id, cantidad, precio_unitario, precio_costo_actual, total, metodo_pago, cliente_nombre, cliente_identificacion, impuestos, codigo_fiscal, fiscal_qr_url))
            
            # Descontar stock
            cursor.execute("""
                UPDATE productos 
                SET stock = stock - ? 
                WHERE id = ?
            """, (cantidad, producto_id))
            
            conn.commit()
            return True, "Venta registrada exitosamente."
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"

def obtener_ventas_reporte(filtro_fecha="Todo"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        condicion = ""
        if filtro_fecha == "Hoy":
            condicion = "WHERE date(v.fecha) = date('now', 'localtime')"
        elif filtro_fecha == "Últimos 7 días":
            condicion = "WHERE date(v.fecha) >= date('now', 'localtime', '-7 days')"
        elif filtro_fecha == "Este Mes":
            condicion = "WHERE strftime('%Y-%m', v.fecha) = strftime('%Y-%m', 'now', 'localtime')"

        query = f"""
            SELECT v.id, p.codigo, p.nombre, v.cantidad, v.precio_unitario, v.total, v.fecha, v.metodo_pago
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            {condicion}
            ORDER BY v.fecha DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

def obtener_resumen_ventas(filtro_fecha="Todo"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        condicion = ""
        if filtro_fecha == "Hoy":
            condicion = "WHERE date(fecha) = date('now', 'localtime')"
        elif filtro_fecha == "Últimos 7 días":
            condicion = "WHERE date(fecha) >= date('now', 'localtime', '-7 days')"
        elif filtro_fecha == "Este Mes":
            condicion = "WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"

        query = f"""
            SELECT 
                COALESCE(SUM(total), 0), 
                COUNT(id),
                COALESCE(SUM(CASE WHEN metodo_pago = 'Efectivo' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN metodo_pago = 'Transferencia' THEN total ELSE 0 END), 0),
                COALESCE(SUM(total - (cantidad * precio_costo_unitario)), 0)
            FROM ventas
            {condicion}
        """
        cursor.execute(query)
        total, cant, efe, tra, utilidad = cursor.fetchone()
        
        return {
            "total": total,
            "cant": cant,
            "efe": efe,
            "tra": tra,
            "utilidad": utilidad
        }

def obtener_alertas_stock():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
        return cursor.fetchone()[0]

def anular_venta(venta_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            # Obtener el producto_id y cantidad para reponer
            cursor.execute("SELECT producto_id, cantidad FROM ventas WHERE id = ?", (venta_id,))
            res = cursor.fetchone()
            if not res:
                return False, "Registro de venta no encontrado."
            producto_id, cantidad = res
            
            # Devolver el stock del producto
            cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))
            
            # Eliminar el registro de venta
            cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
            
            conn.commit()
            return True, "Venta anulada con éxito. Unidades devueltas al inventario."
        except Exception as e:
            conn.rollback()
            return False, f"Error al anular: {str(e)}"

def obtener_top_productos(filtro_fecha="Todo"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        condicion = ""
        if filtro_fecha == "Hoy":
            condicion = "WHERE date(v.fecha) = date('now', 'localtime')"
        elif filtro_fecha == "Últimos 7 días":
            condicion = "WHERE date(v.fecha) >= date('now', 'localtime', '-7 days')"
        elif filtro_fecha == "Este Mes":
            condicion = "WHERE strftime('%Y-%m', v.fecha) = strftime('%Y-%m', 'now', 'localtime')"

        query = f"""
            SELECT p.nombre, SUM(v.cantidad) as total_vendido
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            {condicion}
            GROUP BY v.producto_id
            ORDER BY total_vendido DESC
            LIMIT 3
        """
        cursor.execute(query)
        return cursor.fetchall()

def obtener_configuracion():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_empresa, propietario, telefono, direccion, mensaje_ticket, impresora_ticket, pais_operacion FROM configuracion WHERE id = 1")
        res = cursor.fetchone()
        if res:
            return {
                "nombre_empresa": res[0],
                "propietario": res[1] or "",
                "telefono": res[2] or "",
                "direccion": res[3] or "",
                "mensaje_ticket": res[4] or "¡Gracias por su compra!",
                "impresora_ticket": res[5] or "",
                "pais_operacion": res[6] or "Otro / Ninguno (Solo local)"
            }
        return None

def guardar_configuracion(nombre_empresa, propietario, telefono, direccion, mensaje_ticket, impresora_ticket="", pais_operacion="Otro / Ninguno (Solo local)"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM configuracion WHERE id = 1")
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            cursor.execute("""
                UPDATE configuracion 
                SET nombre_empresa = ?, propietario = ?, telefono = ?, direccion = ?, mensaje_ticket = ?, impresora_ticket = ?, pais_operacion = ?
                WHERE id = 1
            """, (nombre_empresa, propietario, telefono, direccion, mensaje_ticket, impresora_ticket, pais_operacion))
        else:
            cursor.execute("""
                INSERT INTO configuracion (id, nombre_empresa, propietario, telefono, direccion, mensaje_ticket, impresora_ticket, pais_operacion)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre_empresa, propietario, telefono, direccion, mensaje_ticket, impresora_ticket, pais_operacion))
        conn.commit()


def eliminar_configuracion():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM configuracion WHERE id = 1")
        conn.commit()

def hash_clave(clave):
    return hashlib.sha256(clave.encode('utf-8')).hexdigest()

def crear_usuario(usuario, clave, rol='Administrador'):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        clave_hash = hash_clave(clave)
        try:
            cursor.execute("""
                INSERT INTO usuarios (usuario, clave, rol)
                VALUES (?, ?, ?)
            """, (usuario.strip(), clave_hash, rol))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def verificar_usuario(usuario, clave):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        clave_hash = hash_clave(clave)
        cursor.execute("""
            SELECT id, usuario, rol 
            FROM usuarios 
            WHERE usuario = ? AND clave = ?
        """, (usuario.strip(), clave_hash))
        res = cursor.fetchone()
        if res:
            return {"id": res[0], "usuario": res[1], "rol": res[2]}
        return None

def eliminar_usuarios():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios")
        conn.commit()

def obtener_cantidad_usuarios():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        return cursor.fetchone()[0]



