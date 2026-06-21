import urllib.request
import json
import threading
import time
import database

# Variables globales para indicar el estado de la sincronización en la UI
estado_sincronizacion = "No configurado"
ultimo_intento = ""

def iniciar_hilo_sincronizacion(app):
    """Inicia el proceso de sincronización en segundo plano."""
    thread = threading.Thread(target=bucle_sincronizacion, args=(app,), daemon=True)
    thread.start()

def bucle_sincronizacion(app):
    global estado_sincronizacion, ultimo_intento
    
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
            sincronizar_productos(url_base, key)
            
            # 2. Sincronizar Ventas (Subir las que tengan sincronizado = 0)
            sincronizar_ventas(url_base, key)
            
            estado_sincronizacion = "Sincronizado"
            ultimo_intento = time.strftime("%H:%M:%S")
            
        except Exception as e:
            estado_sincronizacion = "Error de conexión"
            print(f"Error en sincronización en la nube: {e}")
            
        # Sincroniza cada 30 segundos
        time.sleep(30)

def sincronizar_productos(url_base, key):
    productos = database.obtener_todos_productos()
    if not productos:
        return
        
    payload = []
    for p in productos:
        payload.append({
            "id": p[0],
            "codigo": p[1],
            "nombre": p[2],
            "categoria": p[3],
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

def sincronizar_ventas(url_base, key):
    ventas = database.obtener_ventas_no_sincronizadas()
    if not ventas:
        return
        
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    for v in ventas:
        payload = {
            "id": v[0],
            "codigo": v[1],
            "nombre": v[2],
            "cantidad": v[3],
            "precio_unitario": v[4],
            "total": v[5],
            "fecha": v[6],
            "metodo_pago": v[7],
            "descuento": v[8] or 0.0,
            "cliente_nombre": v[9] or "",
            "impuestos": v[10] or 0.0
        }
        
        # Enviar venta individual a Supabase
        url = f"{url_base}/rest/v1/ventas"
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
            # Si tiene éxito, marcar localmente como sincronizado
            database.marcar_venta_sincronizada(v[0])

def probar_conexion_supabase(url, key):
    """Prueba si las credenciales de Supabase son correctas llamando al endpoint de la API."""
    try:
        url_base = url.rstrip("/")
        test_url = f"{url_base}/rest/v1/"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        req = urllib.request.Request(test_url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in [200, 204]:
                return True, "Conexión a Supabase exitosa."
            return False, f"Respuesta de servidor: Código {response.status}"
    except Exception as e:
        return False, f"Fallo al conectar: {str(e)}"
