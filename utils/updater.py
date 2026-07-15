import urllib.request
import json
import os
import sys
import threading
import subprocess
from tkinter import messagebox

# Archivo de control centralizado alojado en el repositorio de GitHub
VERSION_URL = "https://raw.githubusercontent.com/FerchoGG2006/invent/main/version.json"
APP_VERSION = "1.1.5"

# Marcador para evitar bucle infinito de reinicios
_UPDATED_FLAG = "--just-updated"


def aplicar_actualizacion_pendiente():
    """
    Se ejecuta AL INICIO, ANTES de crear la ventana principal.
    Revisa si hay un ejecutable nuevo descargado previamente en la carpeta TEMP.
    Si lo encuentra, lo aplica (reemplaza el .exe actual) y reinicia la app.

    Retorna True si se está aplicando una actualización (la app se va a cerrar).
    Retorna False si no hay nada pendiente y la app debe continuar normalmente.
    """
    # No hacer nada en modo desarrollo
    if not getattr(sys, 'frozen', False):
        return False

    # Si acabamos de actualizarnos, limpiar la bandera y continuar
    if _UPDATED_FLAG in sys.argv:
        # Limpiar archivo pendiente por si quedó
        _limpiar_pendiente()
        return False

    exe_path = sys.executable
    exe_name = os.path.basename(exe_path)
    temp_dir = os.environ.get('TEMP') or os.path.dirname(exe_path)
    pending_exe = os.path.join(temp_dir, f"pending_{exe_name}")

    if not os.path.exists(pending_exe):
        return False

    # Hay una actualización pendiente — aplicarla
    bat_path = os.path.join(temp_dir, "apply_update.bat")
    bat_script = f"""@echo off
title Aplicando actualizacion...
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
ping 127.0.0.1 -n 3 > nul
move /y "{pending_exe}" "{exe_path}"
start "" "{exe_path}" {_UPDATED_FLAG}
del "%~f0"
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_script)

    subprocess.Popen([bat_path], shell=True)
    sys.exit(0)


def buscar_actualizaciones(app):
    """
    Busca actualizaciones en segundo plano DESPUÉS de que la app ya está abierta.
    Si encuentra una versión nueva, descarga el .exe silenciosamente a la carpeta TEMP
    como archivo "pendiente". Se aplicará la próxima vez que el usuario abra la app.
    """
    def check():
        try:
            req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            remote_version = data.get("version", APP_VERSION)
            mensaje = data.get("mensaje_global", "")
            update_url = data.get("update_url", "")

            # Mostrar "SMS" global si hay alguno
            if mensaje:
                app.root.after(1000, lambda: messagebox.showinfo("Notificación del Sistema", mensaje))

            # Verificar si la versión remota es diferente a la actual
            if remote_version != APP_VERSION and update_url:
                _descargar_pendiente(update_url)

        except Exception as e:
            print(f"No se pudieron verificar las actualizaciones (Modo Offline o error de red): {e}")

    threading.Thread(target=check, daemon=True).start()


def _descargar_pendiente(url):
    """
    Descarga el nuevo ejecutable de forma silenciosa y lo guarda como 'pending_NombreApp.exe'
    en la carpeta TEMP. No interrumpe al usuario, no reinicia nada.
    La actualización se aplicará automáticamente la próxima vez que se abra el programa.
    """
    if not getattr(sys, 'frozen', False):
        return

    exe_name = os.path.basename(sys.executable)
    temp_dir = os.environ.get('TEMP') or os.path.dirname(sys.executable)
    pending_exe = os.path.join(temp_dir, f"pending_{exe_name}")

    # Si ya hay un archivo pendiente, no descargar otra vez
    if os.path.exists(pending_exe):
        return

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response, open(pending_exe, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Actualización descargada silenciosamente: {pending_exe}")
    except Exception as e:
        print(f"Error al descargar actualización en segundo plano: {e}")
        # Limpiar archivo incompleto si falló
        if os.path.exists(pending_exe):
            try:
                os.remove(pending_exe)
            except OSError:
                pass


def _limpiar_pendiente():
    """Elimina el archivo de actualización pendiente si existe."""
    if not getattr(sys, 'frozen', False):
        return
    exe_name = os.path.basename(sys.executable)
    temp_dir = os.environ.get('TEMP') or os.path.dirname(sys.executable)
    pending_exe = os.path.join(temp_dir, f"pending_{exe_name}")
    if os.path.exists(pending_exe):
        try:
            os.remove(pending_exe)
        except OSError:
            pass
