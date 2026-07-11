import urllib.request
import json
import os
import sys
import threading
import subprocess
from tkinter import messagebox

# Archivo de control centralizado alojado en el repositorio de GitHub
VERSION_URL = "https://raw.githubusercontent.com/FerchoGG2006/invent/main/version.json"
APP_VERSION = "1.1.3"

def buscar_actualizaciones(app):
    """
    Busca actualizaciones en segundo plano para no bloquear la interfaz gráfica.
    Si encuentra un mensaje global o una nueva versión, los muestra en el hilo principal.
    """
    def check():
        try:
            req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            remote_version = data.get("version", APP_VERSION)
            mensaje = data.get("mensaje_global", "")
            update_url = data.get("update_url", "")
            forzar = data.get("forzar_actualizacion", False)
            
            # Mostrar "SMS" global
            if mensaje:
                app.root.after(1000, lambda: messagebox.showinfo("Notificación del Sistema", mensaje))
                
            # Verificar si la versión remota es diferente a la actual (más nueva)
            if remote_version != APP_VERSION and update_url:
                # Iniciar la actualización automáticamente en segundo plano sin preguntar
                app.root.after(2000, lambda: iniciar_actualizacion(app, update_url))
                
        except Exception as e:
            print(f"No se pudieron verificar las actualizaciones (Modo Offline o error de red): {e}")
            
    threading.Thread(target=check, daemon=True).start()

# Función eliminada: preguntar_actualizacion, ya no se usa porque es automático.

def iniciar_actualizacion(app, url):
    """
    Descarga el nuevo ejecutable y crea un script BATCH temporal para reemplazar el archivo actual en ejecución.
    """
    # Si estamos en modo desarrollo (py app.py), no intentar actualizar.
    if not getattr(sys, 'frozen', False):
        return

    exe_path = sys.executable
    exe_name = os.path.basename(exe_path)
    
    # Usar el directorio temporal del sistema para evitar problemas de escritura en Archivos de Programa
    temp_dir = os.environ.get('TEMP') or os.path.dirname(exe_path)
    new_exe_path = os.path.join(temp_dir, f"new_{exe_name}")
    bat_path = os.path.join(temp_dir, "updater.bat")

    # Mostrar progreso
    progress_win = app.root
    progress_win.config(cursor="wait")
    
    def download_and_run():
        try:
            # Descargar archivo
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response, open(new_exe_path, 'wb') as out_file:
                out_file.write(response.read())

            # Crear script batch para reemplazar
            # Si el programa está instalado en C:\Program Files, requerirá elevación de privilegios (UAC)
            bat_script = f"""@echo off
title Actualizacion de InventarioPOS
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador para aplicar la actualizacion...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
echo Reemplazando archivo ejecutable, por favor espere...
ping 127.0.0.1 -n 4 > nul
move /y "{new_exe_path}" "{exe_path}"
start "" "{exe_path}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_script)

            # Ejecutar el .bat y cerrar la app actual
            subprocess.Popen([bat_path], shell=True)
            app.root.after(100, app.root.destroy)

        except Exception as e:
            app.root.after(0, lambda: messagebox.showerror("Error", f"Fallo al descargar la actualización: {e}"))
            app.root.after(0, lambda: progress_win.config(cursor=""))

    # Descargar en hilo separado para que no se congele la ventana mientras descarga
    threading.Thread(target=download_and_run, daemon=True).start()
