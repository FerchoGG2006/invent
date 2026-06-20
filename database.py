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
        
        # --- TABLAS FASE 1 (EXISTENTES) ---
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                clave TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'Administrador'
            )
        """)

        # --- TABLAS FASE 2: VENTAS MEJORADAS ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                metodo_pago TEXT NOT NULL,
                monto REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas_producto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                nota_texto TEXT NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
            )
        """)

        # --- TABLAS FASE 3: INVENTARIO Y PROVEEDORES ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                color_hex TEXT DEFAULT '#E2E8F0',
                orden INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                notas TEXT,
                fecha_registro TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                usuario_id INTEGER,
                fecha TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                total REAL NOT NULL DEFAULT 0.0,
                notas TEXT,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mermas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                motivo TEXT NOT NULL,
                usuario_id INTEGER,
                fecha TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        # --- TABLAS FASE 4: CAJA ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cajas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ubicacion TEXT,
                activa INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turnos_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caja_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                fecha_apertura TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                fecha_cierre TIMESTAMP,
                monto_apertura REAL NOT NULL DEFAULT 0.0,
                monto_cierre_esperado REAL,
                monto_cierre_real REAL,
                diferencia REAL,
                estado TEXT DEFAULT 'Abierto',
                FOREIGN KEY (caja_id) REFERENCES cajas(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turno_id INTEGER NOT NULL,
                tipo TEXT NOT NULL, -- 'Ingreso', 'Egreso'
                monto REAL NOT NULL,
                descripcion TEXT,
                fecha TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (turno_id) REFERENCES turnos_caja(id) ON DELETE CASCADE
            )
        """)

        # --- MIGRACIONES (ALTER TABLE PARA TABLAS EXISTENTES) ---
        
        # Migraciones Configuracion
        columnas_config = [
            ("impresora_ticket", "TEXT"),
            ("pais_operacion", "TEXT DEFAULT 'Otro / Ninguno (Solo local)'")
        ]
        for col_name, col_type in columnas_config:
            try:
                cursor.execute(f"ALTER TABLE configuracion ADD COLUMN {col_name} {col_type};")
            except sqlite3.OperationalError:
                pass

        # Migraciones Ventas
        columnas_ventas = [
            ("cliente_nombre", "TEXT"), 
            ("cliente_identificacion", "TEXT"), 
            ("impuestos", "REAL DEFAULT 0.0"), 
            ("codigo_fiscal", "TEXT"), 
            ("fiscal_qr_url", "TEXT"),
            ("descuento", "REAL DEFAULT 0.0"),
            ("propina", "REAL DEFAULT 0.0"),
            ("es_cortesia", "INTEGER DEFAULT 0"),
            ("autorizado_por", "TEXT")
        ]
        for col_name, col_type in columnas_ventas:
            try:
                cursor.execute(f"ALTER TABLE ventas ADD COLUMN {col_name} {col_type};")
            except sqlite3.OperationalError:
                pass

        # Migraciones Productos
        columnas_productos = [
            ("proveedor_id", "INTEGER"),
            ("unidad_medida", "TEXT DEFAULT 'Unidad'"),
            ("margen_utilidad", "REAL DEFAULT 0.0")
        ]
        for col_name, col_type in columnas_productos:
            try:
                cursor.execute(f"ALTER TABLE productos ADD COLUMN {col_name} {col_type};")
            except sqlite3.OperationalError:
                pass

        # Migraciones Usuarios
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN permisos TEXT;")
        except sqlite3.OperationalError:
            pass

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
                SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, margen_utilidad, unidad_medida
                FROM productos 
                WHERE codigo LIKE ? OR nombre LIKE ?
                ORDER BY nombre
            """, (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("""
                SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, margen_utilidad, unidad_medida
                FROM productos 
                ORDER BY nombre
            """)
        return cursor.fetchall()

def insertar_producto(codigo, nombre, categoria, costo, venta, stock, min_stock, imagen, unidad_medida="Unidad", proveedor_id=None):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            margen = 0.0
            if costo > 0:
                margen = ((venta - costo) / costo) * 100
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, imagen_ruta, margen_utilidad, unidad_medida, proveedor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo, nombre, categoria, costo, venta, stock, min_stock, imagen, margen, unidad_medida, proveedor_id))
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
            SELECT v.id, p.codigo, p.nombre, v.cantidad, v.precio_unitario, v.total, v.fecha, v.metodo_pago, v.descuento, v.cliente_nombre, v.cliente_identificacion, v.impuestos, v.codigo_fiscal, v.fiscal_qr_url, v.es_cortesia, v.autorizado_por
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
        res = cursor.fetchone()
        return {
            "total": res[0], "cant": res[1], "efe": res[2], "tra": res[3], "utilidad": res[4]
        }

def obtener_alertas_stock():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
        return cursor.fetchone()[0]

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

# ==========================================
# FASE 3: PROVEEDORES Y CATEGORÍAS
# ==========================================

def obtener_categorias():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion, color_hex, orden FROM categorias ORDER BY orden, nombre")
        return cursor.fetchall()

def insertar_categoria(nombre, descripcion="", color_hex="#E2E8F0", orden=0):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categorias (nombre, descripcion, color_hex, orden) VALUES (?, ?, ?, ?)",
                           (nombre.strip(), descripcion, color_hex, orden))
            conn.commit()
            return True, "Categoría agregada exitosamente."
        except sqlite3.IntegrityError:
            return False, "Ya existe una categoría con ese nombre."

def obtener_proveedores(filtro=""):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT id, nombre, contacto, telefono, email, direccion, notas FROM proveedores WHERE nombre LIKE ? OR contacto LIKE ?", (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT id, nombre, contacto, telefono, email, direccion, notas FROM proveedores ORDER BY nombre")
        return cursor.fetchall()

def insertar_proveedor(nombre, contacto, telefono, email, direccion, notas):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, contacto, telefono, email, direccion, notas))
        conn.commit()
        return True, "Proveedor agregado exitosamente."

def registrar_compra(proveedor_id, usuario_id, total, notas, detalle_productos):
    # detalle_productos es una lista de diccionarios: {"id", "cantidad", "precio_unitario"}
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO compras (proveedor_id, usuario_id, total, notas) VALUES (?, ?, ?, ?)",
                           (proveedor_id, usuario_id, total, notas))
            compra_id = cursor.lastrowid
            
            for item in detalle_productos:
                subtotal = item["cantidad"] * item["precio_unitario"]
                cursor.execute("""
                    INSERT INTO compras_detalle (compra_id, producto_id, cantidad, precio_unitario, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (compra_id, item["id"], item["cantidad"], item["precio_unitario"], subtotal))
                
                # Actualizar stock y precio de costo del producto (Promedio ponderado opcional, aquí solo reemplazamos o conservamos lógica de negocio. Por simplicidad, actualizamos stock y dejamos precio costo si el usuario lo editó antes, o se podría actualizar).
                cursor.execute("UPDATE productos SET stock = stock + ?, precio_costo = ? WHERE id = ?", 
                               (item["cantidad"], item["precio_unitario"], item["id"]))
                
            conn.commit()
            return True, "Compra registrada exitosamente y stock actualizado."
        except Exception as e:
            conn.rollback()
            return False, f"Error al registrar compra: {str(e)}"

def registrar_merma(producto_id, cantidad, motivo, usuario_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
            res = cursor.fetchone()
            if not res or res[0] < cantidad:
                return False, "Stock insuficiente para registrar esta merma."
            
            cursor.execute("INSERT INTO mermas (producto_id, cantidad, motivo, usuario_id) VALUES (?, ?, ?, ?)",
                           (producto_id, cantidad, motivo, usuario_id))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto_id))
            conn.commit()
            return True, "Merma registrada y stock descontado."
        except Exception as e:
            conn.rollback()
            return False, f"Error al registrar merma: {str(e)}"

def obtener_mermas():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, p.nombre, m.cantidad, m.motivo, m.fecha, u.usuario
            FROM mermas m
            JOIN productos p ON m.producto_id = p.id
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.fecha DESC
        """)
        return cursor.fetchall()

def eliminar_producto(producto_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            # Check si tiene ventas
            cursor.execute("SELECT COUNT(*) FROM ventas WHERE producto_id = ?", (producto_id,))
            if cursor.fetchone()[0] > 0:
                return False, "No se puede eliminar el producto porque tiene ventas asociadas. Considérelo ponerlo inactivo o cambiar su stock a 0."
            
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()
            return True, "Producto eliminado exitosamente."
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"

def actualizar_producto(p_id, codigo, nombre, categoria, costo, venta, stock, min_stock, proveedor_id, unidad_medida):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            margen = 0.0
            if costo > 0:
                margen = ((venta - costo) / costo) * 100
                
            cursor.execute("""
                UPDATE productos 
                SET codigo=?, nombre=?, categoria=?, precio_costo=?, precio_venta=?, stock=?, stock_minimo=?, proveedor_id=?, unidad_medida=?, margen_utilidad=?
                WHERE id=?
            """, (codigo, nombre, categoria, costo, venta, stock, min_stock, proveedor_id, unidad_medida, margen, p_id))
            conn.commit()
            return True, "Producto actualizado exitosamente."
        except sqlite3.IntegrityError:
            return False, "Error de integridad (el código ya existe)."
        except Exception as e:
            return False, f"Error: {str(e)}"

# ==========================================
# FASE 4: CAJA Y TURNOS
# ==========================================

def abrir_turno_caja(usuario_id, monto_apertura, caja_id=1):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Insertar caja por defecto si no existe
        cursor.execute("INSERT OR IGNORE INTO cajas (id, nombre, ubicacion) VALUES (1, 'Caja Principal', 'Mostrador')")
        
        # Verificar si hay turno abierto
        cursor.execute("SELECT id FROM turnos_caja WHERE estado = 'Abierto' AND caja_id = ?", (caja_id,))
        if cursor.fetchone():
            return False, "Ya existe un turno abierto para esta caja."
            
        cursor.execute("INSERT INTO turnos_caja (caja_id, usuario_id, monto_apertura) VALUES (?, ?, ?)",
                       (caja_id, usuario_id, monto_apertura))
        turno_id = cursor.lastrowid
        cursor.execute("INSERT INTO movimientos_caja (turno_id, tipo, monto, descripcion) VALUES (?, 'Ingreso', ?, 'Apertura de Turno')",
                       (turno_id, monto_apertura))
        conn.commit()
        return True, "Turno abierto exitosamente."

def cerrar_turno_caja(turno_id, monto_cierre_real):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Obtener monto apertura y movimientos
        cursor.execute("SELECT monto_apertura FROM turnos_caja WHERE id = ?", (turno_id,))
        apertura = cursor.fetchone()[0]
        
        # TODO: Sumar ventas en efectivo durante este turno. Por simplicidad, tomaremos las ventas del día si el turno dura un día.
        # En un sistema real de turnos, las ventas deben registrar el turno_id.
        # Por ahora lo dejaremos simplificado.
        
        # Se requiere asociar ventas al turno en futuras mejoras.
        
        diferencia = monto_cierre_real - apertura # Simplificado
        cursor.execute("""
            UPDATE turnos_caja 
            SET fecha_cierre = datetime('now', 'localtime'), monto_cierre_real = ?, diferencia = ?, estado = 'Cerrado'
            WHERE id = ?
        """, (monto_cierre_real, diferencia, turno_id))
        cursor.execute("INSERT INTO movimientos_caja (turno_id, tipo, monto, descripcion) VALUES (?, 'Ingreso', ?, 'Cierre de Turno (Declarado)')",
                       (turno_id, monto_cierre_real))
        conn.commit()
        return True, "Turno cerrado exitosamente."
