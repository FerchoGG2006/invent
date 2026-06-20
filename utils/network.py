"""
Verificación asíncrona de conectividad a internet.
"""
import socket
import threading


def verificar_conexion_internet():
    """Intenta conexión TCP a DNS público de Google. Retorna True si hay internet."""
    try:
        socket.setdefaulttimeout(1.2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False


def verificar_conexion_async(callback):
    """
    Verifica la conexión en un hilo separado y llama a callback(conectado: bool).
    El callback se ejecuta en el hilo secundario; el caller debe usar root.after()
    para actualizar la UI.
    """
    def task():
        conn = verificar_conexion_internet()
        callback(conn)
    threading.Thread(target=task, daemon=True).start()
