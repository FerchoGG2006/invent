"""
Módulo de Configuración, Login, Registro y Splash Screen.
Contiene todas las ventanas de configuración del negocio y autenticación.
Rediseñado con CustomTkinter para una estética premium moderna.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import database
import sys
from utils.sync import probar_conexion_supabase


def mostrar_configuracion_inicial(app):
    """Muestra la ventana de configuración inicial del negocio."""
    from utils.printer import obtener_impresoras_sistema

    setup_win = ctk.CTkToplevel(app.root)
    setup_win.title("Configuración de Empresa - POS")
    setup_win.geometry("480x750")
    setup_win.configure(fg_color="#F8FAFC")
    setup_win.resizable(False, False)

    setup_win.update_idletasks()
    width = setup_win.winfo_width()
    height = setup_win.winfo_height()
    x = (setup_win.winfo_screenwidth() // 2) - (width // 2)
    y = (setup_win.winfo_screenheight() // 2) - (height // 2)
    setup_win.geometry(f'+{x}+{y}')

    def on_close():
        app.root.destroy()
        sys.exit(0)
    setup_win.protocol("WM_DELETE_WINDOW", on_close)

    # Header
    frame_header = ctk.CTkFrame(setup_win, fg_color="#4F46E5", corner_radius=0, height=70)
    frame_header.pack(fill=tk.X)
    ctk.CTkLabel(frame_header, text="✨ CONFIGURACIÓN DE TU NEGOCIO ✨", font=("Segoe UI", 13, "bold"), text_color="white").pack(pady=20)

    ctk.CTkLabel(setup_win, text="¡Bienvenido! Personaliza el sistema POS con los datos\nde tu empresa. Estos datos aparecerán en tus tickets y reportes.",
                 font=("Segoe UI", 10, "italic"), text_color="#64748B", justify=tk.CENTER).pack(pady=10)

    frame_form = ctk.CTkScrollableFrame(setup_win, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

    campos = [
        ("Nombre de la Empresa *", "nombre"),
        ("Propietario", "propietario"),
        ("Teléfono", "telefono"),
        ("Dirección", "direccion"),
        ("Mensaje del Ticket", "mensaje"),
    ]

    entries = {}
    for label_text, key in campos:
        ctk.CTkLabel(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
        entry = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6)
        entry.pack(fill=tk.X, padx=15, pady=1)
        entries[key] = entry

    entries["mensaje"].insert(0, "¡Gracias por su compra!")

    # Selector de Impresora
    ctk.CTkLabel(frame_form, text="Impresora Térmica (Opcional)", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    impresoras = obtener_impresoras_sistema()
    combo_impresora = ctk.CTkComboBox(frame_form, values=impresoras if impresoras else ["Ninguna"], font=("Segoe UI", 10), dropdown_font=("Segoe UI", 10), height=32, corner_radius=6)
    combo_impresora.pack(fill=tk.X, padx=15, pady=1)
    if impresoras:
        combo_impresora.set(impresoras[0])
    else:
        combo_impresora.set("Ninguna")

    # Selector de País
    ctk.CTkLabel(frame_form, text="País de Operación", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    paises = ["Chile", "Colombia", "México", "Argentina", "Otro / Ninguno (Solo local)"]
    combo_pais = ctk.CTkComboBox(frame_form, values=paises, font=("Segoe UI", 10), dropdown_font=("Segoe UI", 10), height=32, corner_radius=6)
    combo_pais.pack(fill=tk.X, padx=15, pady=1)
    combo_pais.set("Otro / Ninguno (Solo local)")

    # Campos Supabase
    ctk.CTkLabel(frame_form, text="Supabase URL (Nube - Opcional)", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(8, 1))
    entry_sb_url = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="https://xyz.supabase.co")
    entry_sb_url.pack(fill=tk.X, padx=15, pady=1)

    ctk.CTkLabel(frame_form, text="Supabase Anon Key (Nube - Opcional)", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    entry_sb_key = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="eyJhbGciOi...", show="*")
    entry_sb_key.pack(fill=tk.X, padx=15, pady=1)

    def guardar():
        nombre = entries["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre de la empresa es obligatorio.", parent=setup_win)
            return

        propietario = entries["propietario"].get().strip()
        telefono = entries["telefono"].get().strip()
        direccion = entries["direccion"].get().strip()
        mensaje = entries["mensaje"].get().strip() or "¡Gracias por su compra!"
        impresora = combo_impresora.get()
        if impresora == "Ninguna":
            impresora = ""
        pais = combo_pais.get()
        sb_url = entry_sb_url.get().strip()
        sb_key = entry_sb_key.get().strip()

        # Probar conexión Supabase si se ingresaron credenciales
        if sb_url or sb_key:
            if not sb_url or not sb_key:
                messagebox.showwarning("Atención", "Para activar la nube debes ingresar tanto la URL como la clave API de Supabase.", parent=setup_win)
                return
            exito_sb, msg_sb = probar_conexion_supabase(sb_url, sb_key)
            if not exito_sb:
                confirmar_error = messagebox.askyesno("Error de conexión a la nube", f"{msg_sb}\n\n¿Deseas guardar la configuración de todas formas?", parent=setup_win)
                if not confirmar_error:
                    return

        database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora, pais, sb_url, sb_key)
        app.config = database.obtener_configuracion()
        app.root.title(f"Control de Inventario y Ventas - {nombre}")
        setup_win.destroy()
        mostrar_registro_administrador(app)

    btn_continuar = ctk.CTkButton(frame_form, text="Continuar →", font=("Segoe UI", 11, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=38, corner_radius=8, command=guardar)
    btn_continuar.pack(fill=tk.X, padx=15, pady=20)


def mostrar_registro_administrador(app):
    """Muestra la ventana de registro del primer usuario administrador."""
    reg_win = ctk.CTkToplevel(app.root)
    reg_win.title("Crear Usuario Administrador")
    reg_win.geometry("420x460")
    reg_win.configure(fg_color="#F8FAFC")
    reg_win.resizable(False, False)

    reg_win.update_idletasks()
    width = reg_win.winfo_width()
    height = reg_win.winfo_height()
    x = (reg_win.winfo_screenwidth() // 2) - (width // 2)
    y = (reg_win.winfo_screenheight() // 2) - (height // 2)
    reg_win.geometry(f'+{x}+{y}')

    def on_close():
        app.root.destroy()
        sys.exit(0)
    reg_win.protocol("WM_DELETE_WINDOW", on_close)

    frame_header = ctk.CTkFrame(reg_win, fg_color="#1E293B", corner_radius=0, height=60)
    frame_header.pack(fill=tk.X)
    ctk.CTkLabel(frame_header, text="CREAR CUENTA DE ADMINISTRADOR", font=("Segoe UI", 12, "bold"), text_color="#FFFFFF").pack(pady=15)

    ctk.CTkLabel(reg_win, text="👤", font=("Segoe UI", 36), text_color="#1E293B").pack(pady=10)

    frame_form = ctk.CTkFrame(reg_win, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))

    ctk.CTkLabel(frame_form, text="Nombre de Usuario *", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(anchor=tk.W, padx=25, pady=(20, 2))
    entry_user = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=35, corner_radius=6)
    entry_user.pack(fill=tk.X, padx=25, pady=2)
    entry_user.focus_set()

    ctk.CTkLabel(frame_form, text="Contraseña *", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(anchor=tk.W, padx=25, pady=(15, 2))
    entry_pass = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=35, corner_radius=6, show="*")
    entry_pass.pack(fill=tk.X, padx=25, pady=2)

    def guardar_usuario():
        user = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not user:
            messagebox.showwarning("Usuario inválido", "El nombre de usuario no puede estar vacío.", parent=reg_win)
            return
        if not password or len(password) < 4:
            messagebox.showwarning("Contraseña inválida", "La contraseña es obligatoria y debe tener al menos 4 caracteres.", parent=reg_win)
            return

        exito = database.crear_usuario(user, password, "Administrador")
        if exito:
            reg_win.destroy()
            mostrar_login(app)
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario. El nombre de usuario ya existe.", parent=reg_win)

    btn_crear = ctk.CTkButton(frame_form, text="Crear Cuenta y Continuar", font=("Segoe UI", 11, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=38, corner_radius=8, command=guardar_usuario)
    btn_crear.pack(fill=tk.X, padx=25, pady=30)


def mostrar_login(app):
    """Muestra la ventana de inicio de sesión."""
    login_win = ctk.CTkToplevel(app.root)
    login_win.title("Iniciar Sesión")
    login_win.geometry("420x500")
    login_win.configure(fg_color="#F8FAFC")
    login_win.resizable(False, False)

    login_win.update_idletasks()
    width = login_win.winfo_width()
    height = login_win.winfo_height()
    x = (login_win.winfo_screenwidth() // 2) - (width // 2)
    y = (login_win.winfo_screenheight() // 2) - (height // 2)
    login_win.geometry(f'+{x}+{y}')

    def on_close():
        app.root.destroy()
        sys.exit(0)
    login_win.protocol("WM_DELETE_WINDOW", on_close)

    frame_header = ctk.CTkFrame(login_win, fg_color="#1E293B", corner_radius=0, height=65)
    frame_header.pack(fill=tk.X)

    nombre_empresa = app.config["nombre_empresa"].upper() if app.config else "SISTEMA POS"
    ctk.CTkLabel(frame_header, text=nombre_empresa, font=("Segoe UI", 13, "bold"), text_color="#FFFFFF").pack(pady=(12, 1))
    ctk.CTkLabel(frame_header, text="CONTROL DE ACCESO", font=("Segoe UI", 9, "bold"), text_color="#38BDF8").pack(pady=(0, 10))

    ctk.CTkLabel(login_win, text="🔒", font=("Segoe UI", 36), text_color="#1E293B").pack(pady=15)

    frame_form = ctk.CTkFrame(login_win, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))

    ctk.CTkLabel(frame_form, text="Usuario *", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(anchor=tk.W, padx=25, pady=(15, 2))
    entry_user = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=35, corner_radius=6)
    entry_user.pack(fill=tk.X, padx=25, pady=2)
    entry_user.focus_set()

    ctk.CTkLabel(frame_form, text="Contraseña *", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(anchor=tk.W, padx=25, pady=(10, 2))
    entry_pass = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=35, corner_radius=6, show="*")
    entry_pass.pack(fill=tk.X, padx=25, pady=2)

    def intentar_login(event=None):
        user = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not user or not password:
            messagebox.showwarning("Atención", "Por favor ingresa usuario y contraseña.", parent=login_win)
            return

        usuario_autenticado = database.verificar_usuario(user, password)
        if usuario_autenticado:
            app.current_user = usuario_autenticado
            login_win.destroy()
            app.root.deiconify()
        else:
            messagebox.showerror("Error de acceso", "Usuario o contraseña incorrectos.", parent=login_win)
            entry_pass.delete(0, tk.END)
            entry_pass.focus_set()

    entry_user.bind("<Return>", lambda e: entry_pass.focus_set())
    entry_pass.bind("<Return>", intentar_login)

    btn_login = ctk.CTkButton(frame_form, text="Iniciar Sesión", font=("Segoe UI", 11, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=38, corner_radius=8, command=intentar_login)
    btn_login.pack(fill=tk.X, padx=25, pady=25)


def cerrar_sesion(app):
    """Cierra la sesión actual y muestra la pantalla de login."""
    confirmar = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?")
    if confirmar:
        app.root.withdraw()
        app.current_user = None
        mostrar_login(app)


def mostrar_editar_configuracion(app):
    """Muestra la ventana de edición de la configuración del negocio."""
    from utils.printer import obtener_impresoras_sistema

    edit_win = ctk.CTkToplevel(app.root)
    edit_win.title("Editar Configuración del Negocio")
    edit_win.geometry("480x750")
    edit_win.configure(fg_color="#F8FAFC")
    edit_win.resizable(False, False)
    edit_win.grab_set()

    edit_win.update_idletasks()
    width = edit_win.winfo_width()
    height = edit_win.winfo_height()
    x = (edit_win.winfo_screenwidth() // 2) - (width // 2)
    y = (edit_win.winfo_screenheight() // 2) - (height // 2)
    edit_win.geometry(f'+{x}+{y}')

    frame_header = ctk.CTkFrame(edit_win, fg_color="#4F46E5", corner_radius=0, height=65)
    frame_header.pack(fill=tk.X)
    ctk.CTkLabel(frame_header, text="⚙️ CONFIGURACIÓN DEL NEGOCIO", font=("Segoe UI", 13, "bold"), text_color="white").pack(pady=18)

    ctk.CTkLabel(edit_win, text="Modifica los datos de tu empresa. Los cambios se reflejarán\nde inmediato en los nuevos tickets y reportes.",
                 font=("Segoe UI", 10, "italic"), text_color="#64748B", justify=tk.CENTER).pack(pady=10)

    frame_form = ctk.CTkScrollableFrame(edit_win, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

    campos = [
        ("Nombre de la Empresa *", "nombre", app.config.get("nombre_empresa", "")),
        ("Propietario", "propietario", app.config.get("propietario", "")),
        ("Teléfono", "telefono", app.config.get("telefono", "")),
        ("Dirección", "direccion", app.config.get("direccion", "")),
        ("Mensaje del Ticket", "mensaje", app.config.get("mensaje_ticket", "¡Gracias por su compra!")),
    ]

    entries = {}
    for label_text, key, default_val in campos:
        ctk.CTkLabel(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
        entry = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6)
        entry.pack(fill=tk.X, padx=15, pady=1)
        entry.insert(0, default_val)
        entries[key] = entry

    # Selector de Impresora
    ctk.CTkLabel(frame_form, text="Impresora Térmica", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    impresoras = obtener_impresoras_sistema()
    combo_impresora = ctk.CTkComboBox(frame_form, values=impresoras if impresoras else ["Ninguna"], font=("Segoe UI", 10), dropdown_font=("Segoe UI", 10), height=32, corner_radius=6)
    combo_impresora.pack(fill=tk.X, padx=15, pady=1)
    impresora_actual = app.config.get("impresora_ticket", "")
    if impresora_actual in impresoras:
        combo_impresora.set(impresora_actual)
    elif impresoras:
        combo_impresora.set(impresoras[0])
    else:
        combo_impresora.set("Ninguna")

    # Botón Probar Impresora
    def probar_impresora():
        from utils.printer import enviar_impresion_directa
        nombre = combo_impresora.get()
        if not nombre or nombre == "Ninguna":
            messagebox.showwarning("Atención", "Selecciona una impresora primero.", parent=edit_win)
            return
        exito, msg = enviar_impresion_directa(nombre, "=== PRUEBA DE IMPRESORA ===\nSistema POS Conectado\n===========================\n\n")
        if exito:
            messagebox.showinfo("Éxito", f"Prueba enviada a: {nombre}", parent=edit_win)
        else:
            messagebox.showerror("Error", f"No se pudo imprimir:\n{msg}", parent=edit_win)

    btn_test = ctk.CTkButton(frame_form, text="🖨️ Probar Impresora", font=("Segoe UI", 9, "bold"), fg_color="#F3F4F6", hover_color="#E5E7EB", text_color="#1F2937", height=28, corner_radius=6, command=probar_impresora)
    btn_test.pack(fill=tk.X, padx=15, pady=5)

    # Selector de País
    ctk.CTkLabel(frame_form, text="País de Operación", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    paises = ["Chile", "Colombia", "México", "Argentina", "Otro / Ninguno (Solo local)"]
    combo_pais = ctk.CTkComboBox(frame_form, values=paises, font=("Segoe UI", 10), dropdown_font=("Segoe UI", 10), height=32, corner_radius=6)
    combo_pais.pack(fill=tk.X, padx=15, pady=1)
    pais_actual = app.config.get("pais_operacion", "Otro / Ninguno (Solo local)")
    combo_pais.set(pais_actual)

    # Credenciales de Supabase
    ctk.CTkLabel(frame_form, text="Supabase URL (Nube)", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(8, 1))
    entry_sb_url = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="https://xyz.supabase.co")
    entry_sb_url.pack(fill=tk.X, padx=15, pady=1)
    entry_sb_url.insert(0, app.config.get("supabase_url", ""))

    ctk.CTkLabel(frame_form, text="Supabase Anon Key (Nube)", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(anchor=tk.W, padx=15, pady=(5, 1))
    entry_sb_key = ctk.CTkEntry(frame_form, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="eyJhbGciOi...", show="*")
    entry_sb_key.pack(fill=tk.X, padx=15, pady=1)
    entry_sb_key.insert(0, app.config.get("supabase_key", ""))

    # Botón Probar Supabase
    def probar_nube():
        url = entry_sb_url.get().strip()
        key = entry_sb_key.get().strip()
        if not url or not key:
            messagebox.showwarning("Atención", "Ingresa la URL y la clave API de Supabase para poder probar la conexión.", parent=edit_win)
            return
        exito_sb, msg_sb = probar_conexion_supabase(url, key)
        if exito_sb:
            messagebox.showinfo("Conexión en la Nube", msg_sb, parent=edit_win)
        else:
            messagebox.showerror("Error en la Nube", msg_sb, parent=edit_win)

    btn_test_sb = ctk.CTkButton(frame_form, text="☁️ Probar Conexión Nube", font=("Segoe UI", 9, "bold"), fg_color="#F3F4F6", hover_color="#E5E7EB", text_color="#1F2937", height=28, corner_radius=6, command=probar_nube)
    btn_test_sb.pack(fill=tk.X, padx=15, pady=5)

    def guardar():
        nombre = entries["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre de la empresa es obligatorio.", parent=edit_win)
            return

        propietario = entries["propietario"].get().strip()
        telefono = entries["telefono"].get().strip()
        direccion = entries["direccion"].get().strip()
        mensaje = entries["mensaje"].get().strip() or "¡Gracias por su compra!"
        impresora = combo_impresora.get()
        if impresora == "Ninguna":
            impresora = ""
        pais = combo_pais.get()
        sb_url = entry_sb_url.get().strip()
        sb_key = entry_sb_key.get().strip()

        if sb_url or sb_key:
            if not sb_url or not sb_key:
                messagebox.showwarning("Atención", "Para activar la nube debes ingresar tanto la URL como la clave API de Supabase.", parent=edit_win)
                return
            exito_sb, msg_sb = probar_conexion_supabase(sb_url, sb_key)
            if not exito_sb:
                confirmar_error = messagebox.askyesno("Error en la nube", f"{msg_sb}\n\n¿Deseas guardar la configuración de todas formas?", parent=edit_win)
                if not confirmar_error:
                    return

        database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora, pais, sb_url, sb_key)
        app.config = database.obtener_configuracion()
        app.actualizar_labels_facturacion()

        app.root.title(f"Control de Inventario y Ventas - {nombre}")
        edit_win.destroy()
        messagebox.showinfo("Éxito", "Configuración actualizada correctamente.")

    btn_guardar = ctk.CTkButton(frame_form, text="Guardar Cambios", font=("Segoe UI", 11, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=38, corner_radius=8, command=guardar)
    btn_guardar.pack(fill=tk.X, padx=15, pady=20)


def mostrar_splash(app, config):
    """Muestra la pantalla de carga con animación de barra."""
    app.root.withdraw()

    splash = ctk.CTkToplevel(app.root)
    splash.overrideredirect(True)
    splash.configure(fg_color="#1E293B")

    width = 500
    height = 300
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")

    frame_content = ctk.CTkFrame(splash, fg_color="#1E293B", corner_radius=0)
    frame_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)

    ctk.CTkLabel(frame_content, text="SISTEMA POS", font=("Segoe UI", 11, "bold"), text_color="#38BDF8").pack(pady=(15, 5))

    divider = ctk.CTkFrame(frame_content, fg_color="#334155", height=2, corner_radius=0)
    divider.pack(fill=tk.X, pady=10)

    ctk.CTkLabel(frame_content, text=config["nombre_empresa"].upper(), font=("Segoe UI", 18, "bold"), text_color="#FFFFFF", wraplength=440).pack(pady=15)

    ctk.CTkLabel(frame_content, text="Iniciando base de datos y componentes...", font=("Segoe UI", 10, "italic"), text_color="#94A3B8").pack(pady=(10, 0))

    loader_bg = ctk.CTkFrame(frame_content, fg_color="#334155", height=4, corner_radius=0)
    loader_bg.pack(fill=tk.X, pady=(15, 0))
    loader_fg = ctk.CTkFrame(loader_bg, fg_color="#10B981", height=4, width=1, corner_radius=0)
    loader_fg.pack(side=tk.LEFT)

    def animate(w):
        if w < 440:
            loader_fg.configure(width=w)
            splash.after(15, lambda: animate(w + 5))

    animate(1)

    def cerrar_splash():
        splash.destroy()
        mostrar_login(app)

    app.root.after(2000, cerrar_splash)
