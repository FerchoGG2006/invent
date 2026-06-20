"""
Módulo de Configuración, Login, Registro y Splash Screen.
Contiene todas las ventanas de configuración del negocio y autenticación.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database
import sys


def mostrar_configuracion_inicial(app):
    """Muestra la ventana de configuración inicial del negocio."""
    from utils.printer import obtener_impresoras_sistema

    setup_win = tk.Toplevel(app.root)
    setup_win.title("Configuración de Empresa - POS")
    setup_win.geometry("450x640")
    setup_win.configure(bg="#F8FAFC")
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
    frame_header = tk.Frame(setup_win, bg="#4F46E5")
    frame_header.pack(fill=tk.X)
    tk.Label(frame_header, text="✨ CONFIGURACIÓN DE TU NEGOCIO ✨", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white").pack(pady=15)

    tk.Label(setup_win, text="¡Bienvenido! Personaliza el sistema POS con los datos\nde tu empresa. Estos datos aparecerán en tus tickets y reportes.",
             font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#64748B", justify=tk.CENTER).pack(pady=15)

    frame_form = tk.Frame(setup_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

    campos = [
        ("Nombre de la Empresa *", "nombre"),
        ("Propietario", "propietario"),
        ("Teléfono", "telefono"),
        ("Dirección", "direccion"),
        ("Mensaje del Ticket", "mensaje"),
    ]

    entries = {}
    for label_text, key in campos:
        tk.Label(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
        border = tk.Frame(frame_form, bg="#E2E8F0")
        border.pack(fill=tk.X, padx=20, pady=2)
        entry = tk.Entry(border, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
        entry.pack(fill=tk.X, padx=1, pady=1, ipady=4)
        entries[key] = entry

    entries["mensaje"].insert(0, "¡Gracias por su compra!")

    # Selector de Impresora
    tk.Label(frame_form, text="Impresora Térmica (Opcional)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
    impresoras = obtener_impresoras_sistema()
    combo_impresora = ttk.Combobox(frame_form, values=impresoras, state="readonly", font=("Segoe UI", 9))
    combo_impresora.pack(fill=tk.X, padx=20, pady=2)
    if impresoras:
        combo_impresora.set(impresoras[0])

    # Selector de País
    tk.Label(frame_form, text="País de Operación", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
    paises = ["Chile", "Colombia", "México", "Argentina", "Otro / Ninguno (Solo local)"]
    combo_pais = ttk.Combobox(frame_form, values=paises, state="readonly", font=("Segoe UI", 9))
    combo_pais.pack(fill=tk.X, padx=20, pady=2)
    combo_pais.set("Otro / Ninguno (Solo local)")

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
        pais = combo_pais.get()

        database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora, pais)
        app.config = database.obtener_configuracion()
        app.root.title(f"Control de Inventario y Ventas - {nombre}")
        setup_win.destroy()
        mostrar_registro_administrador(app)

    btn_continuar = tk.Button(frame_form, text="Continuar →", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=guardar)
    btn_continuar.pack(fill=tk.X, padx=20, pady=15, ipady=8)
    btn_continuar.bind("<Enter>", lambda e: btn_continuar.config(bg="#4338CA"))
    btn_continuar.bind("<Leave>", lambda e: btn_continuar.config(bg="#4F46E5"))


def mostrar_registro_administrador(app):
    """Muestra la ventana de registro del primer usuario administrador."""
    reg_win = tk.Toplevel(app.root)
    reg_win.title("Crear Usuario Administrador")
    reg_win.geometry("400x420")
    reg_win.configure(bg="#F8FAFC")
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

    frame_header = tk.Frame(reg_win, bg="#1E293B")
    frame_header.pack(fill=tk.X)
    tk.Label(frame_header, text="CREAR CUENTA DE ADMINISTRADOR", font=("Segoe UI", 11, "bold"), bg="#1E293B", fg="#FFFFFF").pack(pady=15)

    tk.Label(reg_win, text="👤", font=("Segoe UI", 36), bg="#F8FAFC").pack(pady=15)

    frame_form = tk.Frame(reg_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))

    tk.Label(frame_form, text="Nombre de Usuario *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(15, 2))
    border_user = tk.Frame(frame_form, bg="#E2E8F0")
    border_user.pack(fill=tk.X, padx=20, pady=2)
    entry_user = tk.Entry(border_user, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
    entry_user.pack(fill=tk.X, padx=1, pady=1, ipady=4)
    entry_user.focus_set()

    tk.Label(frame_form, text="Contraseña *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(10, 2))
    border_pass = tk.Frame(frame_form, bg="#E2E8F0")
    border_pass.pack(fill=tk.X, padx=20, pady=2)
    entry_pass = tk.Entry(border_pass, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A", show="*")
    entry_pass.pack(fill=tk.X, padx=1, pady=1, ipady=4)

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

    btn_crear = tk.Button(frame_form, text="Crear Cuenta y Continuar", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar_usuario)
    btn_crear.pack(fill=tk.X, padx=20, pady=25, ipady=8)
    btn_crear.bind("<Enter>", lambda e: btn_crear.config(bg="#059669"))
    btn_crear.bind("<Leave>", lambda e: btn_crear.config(bg="#10B981"))


def mostrar_login(app):
    """Muestra la ventana de inicio de sesión."""
    login_win = tk.Toplevel(app.root)
    login_win.title("Iniciar Sesión")
    login_win.geometry("400x480")
    login_win.configure(bg="#F8FAFC")
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

    frame_header = tk.Frame(login_win, bg="#1E293B")
    frame_header.pack(fill=tk.X)

    nombre_empresa = app.config["nombre_empresa"].upper() if app.config else "SISTEMA POS"
    tk.Label(frame_header, text=nombre_empresa, font=("Segoe UI", 12, "bold"), bg="#1E293B", fg="#FFFFFF").pack(pady=(15, 2))
    tk.Label(frame_header, text="CONTROL DE ACCESO", font=("Segoe UI", 8, "bold"), bg="#1E293B", fg="#38BDF8").pack(pady=(0, 15))

    tk.Label(login_win, text="🔒", font=("Segoe UI", 36), bg="#F8FAFC").pack(pady=20)

    frame_form = tk.Frame(login_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))

    tk.Label(frame_form, text="Usuario *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=25, pady=(15, 2))
    border_user = tk.Frame(frame_form, bg="#E2E8F0")
    border_user.pack(fill=tk.X, padx=25, pady=2)
    entry_user = tk.Entry(border_user, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
    entry_user.pack(fill=tk.X, padx=1, pady=1, ipady=4)
    entry_user.focus_set()

    tk.Label(frame_form, text="Contraseña *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=25, pady=(10, 2))
    border_pass = tk.Frame(frame_form, bg="#E2E8F0")
    border_pass.pack(fill=tk.X, padx=25, pady=2)
    entry_pass = tk.Entry(border_pass, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A", show="*")
    entry_pass.pack(fill=tk.X, padx=1, pady=1, ipady=4)

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

    btn_login = tk.Button(frame_form, text="Iniciar Sesión", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=intentar_login)
    btn_login.pack(fill=tk.X, padx=25, pady=25, ipady=8)
    btn_login.bind("<Enter>", lambda e: btn_login.config(bg="#4338CA"))
    btn_login.bind("<Leave>", lambda e: btn_login.config(bg="#4F46E5"))


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

    edit_win = tk.Toplevel(app.root)
    edit_win.title("Editar Configuración del Negocio")
    edit_win.geometry("450x740")
    edit_win.configure(bg="#F8FAFC")
    edit_win.resizable(False, False)
    edit_win.grab_set()

    edit_win.update_idletasks()
    width = edit_win.winfo_width()
    height = edit_win.winfo_height()
    x = (edit_win.winfo_screenwidth() // 2) - (width // 2)
    y = (edit_win.winfo_screenheight() // 2) - (height // 2)
    edit_win.geometry(f'+{x}+{y}')

    frame_header = tk.Frame(edit_win, bg="#4F46E5")
    frame_header.pack(fill=tk.X)
    tk.Label(frame_header, text="⚙️ CONFIGURACIÓN DEL NEGOCIO", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white").pack(pady=15)

    tk.Label(edit_win, text="Modifica los datos de tu empresa. Los cambios se reflejarán\nde inmediato en los nuevos tickets y reportes.",
             font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#64748B", justify=tk.CENTER).pack(pady=15)

    frame_form = tk.Frame(edit_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
    frame_form.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

    campos = [
        ("Nombre de la Empresa *", "nombre", app.config.get("nombre_empresa", "")),
        ("Propietario", "propietario", app.config.get("propietario", "")),
        ("Teléfono", "telefono", app.config.get("telefono", "")),
        ("Dirección", "direccion", app.config.get("direccion", "")),
        ("Mensaje del Ticket", "mensaje", app.config.get("mensaje_ticket", "¡Gracias por su compra!")),
    ]

    entries = {}
    for label_text, key, default_val in campos:
        tk.Label(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
        border = tk.Frame(frame_form, bg="#E2E8F0")
        border.pack(fill=tk.X, padx=20, pady=2)
        entry = tk.Entry(border, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
        entry.pack(fill=tk.X, padx=1, pady=1, ipady=4)
        entry.insert(0, default_val)
        entries[key] = entry

    # Selector de Impresora
    tk.Label(frame_form, text="Impresora Térmica", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
    impresoras = obtener_impresoras_sistema()
    combo_impresora = ttk.Combobox(frame_form, values=impresoras, state="readonly", font=("Segoe UI", 9))
    combo_impresora.pack(fill=tk.X, padx=20, pady=2)
    impresora_actual = app.config.get("impresora_ticket", "")
    if impresora_actual in impresoras:
        combo_impresora.set(impresora_actual)
    elif impresoras:
        combo_impresora.set(impresoras[0])

    # Botón Probar Impresora
    def probar_impresora():
        from utils.printer import enviar_impresion_directa
        nombre = combo_impresora.get()
        if not nombre:
            messagebox.showwarning("Atención", "Selecciona una impresora primero.", parent=edit_win)
            return
        exito, msg = enviar_impresion_directa(nombre, "=== PRUEBA DE IMPRESORA ===\nSistema POS Conectado\n===========================\n\n")
        if exito:
            messagebox.showinfo("Éxito", f"Prueba enviada a: {nombre}", parent=edit_win)
        else:
            messagebox.showerror("Error", f"No se pudo imprimir:\n{msg}", parent=edit_win)

    btn_test = tk.Button(frame_form, text="🖨️ Probar Impresora", font=("Segoe UI", 8, "bold"), bg="#E2E8F0", fg="#1E293B", bd=0, cursor="hand2", command=probar_impresora)
    btn_test.pack(fill=tk.X, padx=20, pady=5, ipady=3)

    # Selector de País
    tk.Label(frame_form, text="País de Operación", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(8, 2))
    paises = ["Chile", "Colombia", "México", "Argentina", "Otro / Ninguno (Solo local)"]
    combo_pais = ttk.Combobox(frame_form, values=paises, state="readonly", font=("Segoe UI", 9))
    combo_pais.pack(fill=tk.X, padx=20, pady=2)
    pais_actual = app.config.get("pais_operacion", "Otro / Ninguno (Solo local)")
    combo_pais.set(pais_actual)

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
        pais = combo_pais.get()

        database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora, pais)
        app.config = database.obtener_configuracion()
        app.actualizar_labels_facturacion()

        app.root.title(f"Control de Inventario y Ventas - {nombre}")
        edit_win.destroy()
        messagebox.showinfo("Éxito", "Configuración actualizada correctamente.")

    btn_guardar = tk.Button(frame_form, text="Guardar Cambios", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar)
    btn_guardar.pack(fill=tk.X, padx=20, pady=15, ipady=8)
    btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#059669"))
    btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#10B981"))


def mostrar_splash(app, config):
    """Muestra la pantalla de carga con animación de barra."""
    app.root.withdraw()

    splash = tk.Toplevel(app.root)
    splash.overrideredirect(True)
    splash.configure(bg="#1E293B")

    width = 500
    height = 300
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")

    frame_content = tk.Frame(splash, bg="#1E293B")
    frame_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)

    tk.Label(frame_content, text="SISTEMA POS", font=("Segoe UI", 10, "bold"), bg="#1E293B", fg="#38BDF8").pack(pady=(15, 5))

    divider = tk.Frame(frame_content, bg="#334155", height=2)
    divider.pack(fill=tk.X, pady=10)

    tk.Label(frame_content, text=config["nombre_empresa"].upper(), font=("Segoe UI", 20, "bold"), bg="#1E293B", fg="#FFFFFF", wraplength=440).pack(pady=15)

    tk.Label(frame_content, text="Iniciando base de datos y componentes...", font=("Segoe UI", 9, "italic"), bg="#1E293B", fg="#94A3B8").pack(pady=(10, 0))

    loader_bg = tk.Frame(frame_content, bg="#334155", height=4)
    loader_bg.pack(fill=tk.X, pady=(15, 0))
    loader_fg = tk.Frame(loader_bg, bg="#10B981", height=4, width=1)
    loader_fg.pack(side=tk.LEFT)

    def animate(w):
        if w < 440:
            loader_fg.config(width=w)
            splash.after(15, lambda: animate(w + 5))

    animate(1)

    def cerrar_splash():
        splash.destroy()
        mostrar_login(app)

    app.root.after(2000, cerrar_splash)
