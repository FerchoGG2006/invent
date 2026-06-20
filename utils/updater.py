import urllib.request
import json
import os
import sys
import threading
import subprocess
from tkinter import messagebox

# Archivo de control centralizado alojado en el repositorio de GitHub
VERSION_URL = "https://raw.githubusercontent.com/FerchoGG2006/invent/main/version.json"
APP_VERSION = "1.0.0"

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
                app.root.after(2000, lambda: preguntar_actualizacion(app, remote_version, update_url, forzar))
                
        except Exception as e:
            print(f"No se pudieron verificar las actualizaciones (Modo Offline o error de red): {e}")
            
    threading.Thread(target=check, daemon=True).start()

def preguntar_actualizacion(app, version, url, forzar):
    texto = f"¡Nueva actualización encontrada! (Versión {version})\n\n¿Deseas descargarla e instalarla ahora?\nEl proceso tomará unos segundos y la aplicación se reiniciará automáticamente."
    
    if forzar:
        messagebox.showinfo("Actualización Crítica", f"Es necesario actualizar a la versión {version} para continuar. Se procederá a descargar e instalar la actualización.")
        iniciar_actualizacion(app, url)
    else:
        resp = messagebox.askyesno("Actualización Disponible", texto)
        if resp:
            iniciar_actualizacion(app, url)

def iniciar_actualizacion(app, url):
    """
    Descarga el nuevo ejecutable y crea un script BATCH temporal para reemplazar el archivo actual en ejecución.
    """
    # Si estamos en modo desarrollo (py app.py), no actualizar el exe.
    if not getattr(sys, 'frozen', False):
        messagebox.showinfo("Desarrollo", "Estás ejecutando el código fuente. La actualización automática solo funciona en el archivo .exe compilado.")
        return

    exe_path = sys.executable
    exe_dir = os.path.dirname(exe_path)
    exe_name = os.path.basename(exe_path)
    new_exe_path = os.path.join(exe_dir, f"new_{exe_name}")
    bat_path = os.path.join(exe_dir, "updater.bat")

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
            bat_script = f"""@echo off
echo Actualizando el sistema, por favor espere...
ping 127.0.0.1 -n 3 > nul
move /y "{new_exe_path}" "{exe_path}"
start "" "{exe_path}"
del "%~f0"
"""
            with open(bat_path, "w") as f:
                f.write(bat_script)

            # Ejecutar el .bat oculto y cerrar la app actual
            subprocess.Popen([bat_path], shell=True)
            app.root.after(100, app.root.destroy)

        except Exception as e:
            app.root.after(0, lambda: messagebox.showerror("Error", f"Fallo al descargar la actualización: {e}"))
            app.root.after(0, lambda: progress_win.config(cursor=""))

    # Descargar en hilo separado para que no se congele la ventana mientras descarga
    threading.Thread(target=download_and_run, daemon=True).start()
