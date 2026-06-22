import urllib.request
import urllib.error
import json
import threading
import time
import database

# Variables globales para indicar el estado de la sincronización en la UI
estado_sincronizacion = "No configurado"
ultimo_intento = ""
ultimo_error = ""

def iniciar_hilo_sincronizacion(app):
    """Inicia el proceso de sincronización en segundo plano."""
    thread = threading.Thread(target=bucle_sincronizacion, args=(app,), daemon=True)
    thread.start()

def bucle_sincronizacion(app):
    global estado_sincronizacion, ultimo_intento, ultimo_error
    
    while True:
        try:
            config = database.obtener_configuracion()
            if not config or not config.get("supabase_url") or not config.get("supabase_key"):
                estado_sincronizacion = "No configurado"
                time.sleep(30)
                continue

            url_base = config["supabase_url"].rstrip("/")
            key = config["supabase_key"]
            
            estado_sincronizacion = "Sincronizando..."
            
            # 1. Sincronizar Productos (Upsert de todos los productos para mantener stock al día)
            exito_prod, err_prod = sincronizar_productos(url_base, key)
            
            # 2. Sincronizar Ventas (Subir las que tengan sincronizado = 0)
            exito_ventas, err_ventas = sincronizar_ventas(url_base, key)
            
            if exito_prod and exito_ventas:
                estado_sincronizacion = "Sincronizado"
                ultimo_error = ""
            else:
                errores = []
                if not exito_prod and err_prod:
                    errores.append(f"Productos: {err_prod}")
                if not exito_ventas and err_ventas:
                    errores.append(f"Ventas: {err_ventas}")
                estado_sincronizacion = "Error de conexión"
                ultimo_error = " | ".join(errores)
                print(f"Error en sincronización: {ultimo_error}")
            
            ultimo_intento = time.strftime("%H:%M:%S")
            
        except Exception as e:
            estado_sincronizacion = "Error de conexión"
            ultimo_error = str(e)
            ultimo_intento = time.strftime("%H:%M:%S")
            print(f"Error en sincronización en la nube: {e}")
            
        # Sincroniza cada 30 segundos
        time.sleep(30)

def sincronizar_productos(url_base, key):
    """Sincroniza todos los productos a Supabase con upsert. Devuelve (exito, error_msg)."""
    try:
        productos = database.obtener_todos_productos()
        if not productos:
            return True, ""
            
        payload = []
        for p in productos:
            payload.append({
                "id": p[0],
                "codigo": p[1] or "",
                "nombre": p[2],
                "categoria": p[3] or "",
                "precio_venta": p[4],
                "stock": p[5],
                "stock_minimo": p[6]
            })
            
        url = f"{url_base}/rest/v1/productos"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
        return True, ""
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode('utf-8', errors='replace')
        except Exception:
            pass
        return False, f"HTTP {e.code}: {body[:200]}"
    except Exception as e:
        return False, str(e)

def sincronizar_ventas(url_base, key):
    """Sincroniza ventas no sincronizadas a Supabase. Devuelve (exito, error_msg)."""
    try:
        ventas = database.obtener_ventas_no_sincronizadas()
        if not ventas:
            return True, ""
            
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        errores_ventas = []
        for v in ventas:
            try:
                # Convertir fecha de SQLite a formato ISO 8601 para PostgreSQL
                fecha_str = v[6] or ""
                if fecha_str and "T" not in fecha_str:
                    # SQLite usa "YYYY-MM-DD HH:MM:SS", PostgreSQL espera ISO 8601
                    fecha_str = fecha_str.replace(" ", "T")
                
                payload = {
                    "id": v[0],
                    "codigo": v[1] or "",
                    "nombre": v[2] or "",
                    "cantidad": v[3],
                    "precio_unitario": v[4],
                    "total": v[5],
                    "fecha": fecha_str if fecha_str else None,
                    "metodo_pago": v[7] or "Efectivo",
                    "descuento": v[8] or 0.0,
                    "cliente_nombre": v[9] or "",
                    "impuestos": v[10] or 0.0
                }
                
                url = f"{url_base}/rest/v1/ventas"
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(payload).encode('utf-8'), 
                    headers=headers, 
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    response.read()
                    database.marcar_venta_sincronizada(v[0])
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode('utf-8', errors='replace')
                except Exception:
                    pass
                # Si es un conflicto (409) o ya existe (23505), marcar como sincronizada
                if e.code == 409 or "23505" in body:
                    database.marcar_venta_sincronizada(v[0])
                else:
                    errores_ventas.append(f"Venta {v[0]}: HTTP {e.code} - {body[:100]}")
            except Exception as e:
                errores_ventas.append(f"Venta {v[0]}: {str(e)}")
        
        if errores_ventas:
            return False, "; ".join(errores_ventas[:3])  # Limitar mensajes
        return True, ""
    except Exception as e:
        return False, str(e)

def probar_conexion_supabase(url, key):
    """Prueba si las credenciales de Supabase son correctas llamando al endpoint de la API."""
    try:
        url_base = url.rstrip("/")
        test_url = f"{url_base}/auth/v1/health"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        req = urllib.request.Request(test_url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in [200, 204]:
                return True, "Conexión a Supabase exitosa."
            return False, f"Respuesta de servidor: Código {response.status}"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "Error de autenticación: La clave API (Key) de Supabase es inválida."
        return False, f"Error del servidor (Código {e.code}): {e.reason}"
    except Exception as e:
        return False, f"Fallo al conectar: {str(e)}"
