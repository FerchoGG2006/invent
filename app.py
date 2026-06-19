import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import os
import sys
import shutil
import ctypes
from PIL import Image, ImageTk


class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Ocultar inmediatamente para evitar parpadeos
        self.root.geometry("1200x750")
        self.root.configure(bg="#F8FAFC") # Slate 50
        
        database.init_db()
        self.config = database.obtener_configuracion()
        
        self.carrito = [] # Lista de items: {"id", "codigo", "nombre", "precio", "cantidad"}
        self.selected_cost_price = 0.0
        self.selected_sell_price = 0.0
        self.imagen_ruta_form = "" # Ruta de la foto seleccionada en el formulario
        
        self.crear_interfaz()
        self.cargar_datos()
        self.pos_actualizar_alertas_pestaña()
        self.configurar_atajos()

        # Handle the splash / configuration screen
        cant_usuarios = database.obtener_cantidad_usuarios()
        if not self.config or cant_usuarios == 0:
            self.root.after(100, self.mostrar_configuracion_inicial)
        else:
            self.root.title(f"Control de Inventario y Ventas - {self.config['nombre_empresa']}")
            self.mostrar_splash(self.config)

    def mostrar_configuracion_inicial(self):
        setup_win = tk.Toplevel(self.root)
        setup_win.title("Configuración de Empresa - POS")
        setup_win.geometry("450x640")
        setup_win.configure(bg="#F8FAFC")
        setup_win.resizable(False, False)
        
        # Center the window
        setup_win.update_idletasks()
        width = setup_win.winfo_width()
        height = setup_win.winfo_height()
        x = (setup_win.winfo_screenwidth() // 2) - (width // 2)
        y = (setup_win.winfo_screenheight() // 2) - (height // 2)
        setup_win.geometry(f'+{x}+{y}')
        
        # If they close this window, exit the app since config is required on first run
        def on_close():
            self.root.destroy()
            sys.exit(0)
        setup_win.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header
        frame_header = tk.Frame(setup_win, bg="#4F46E5") # Premium Indigo banner
        frame_header.pack(fill=tk.X)
        
        tk.Label(frame_header, text="✨ CONFIGURACIÓN DE TU NEGOCIO ✨", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white").pack(pady=15)
        
        tk.Label(setup_win, text="¡Bienvenido! Personaliza el sistema POS con los datos\nde tu empresa. Estos datos aparecerán en tus tickets y reportes.", 
                 font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#64748B", justify=tk.CENTER).pack(pady=15)
        
        # Form Container
        frame_form = tk.Frame(setup_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        inputs = {}
        campos_setup = [
            ("Nombre del Negocio *", "nombre_empresa", "Mi Negocio / Tienda / Barbería"),
            ("Propietario / Administrador", "propietario", "Nombre del dueño"),
            ("Teléfono de Contacto", "telefono", "+56 9 1234 5678"),
            ("Dirección del Local", "direccion", "Calle Falsa 123, Ciudad"),
            ("Mensaje al Pie del Ticket", "mensaje_ticket", "¡Gracias por su compra! Vuelva pronto.")
        ]
        
        for label_text, key, placeholder in campos_setup:
            tk.Label(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(6, 1))
            border_frame = tk.Frame(frame_form, bg="#E2E8F0")
            border_frame.pack(fill=tk.X, padx=20, pady=1)
            
            entry = tk.Entry(border_frame, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
            entry.pack(fill=tk.X, padx=1, pady=1, ipady=3)
            inputs[key] = entry
            
            # Simple placeholder behavior or just insert default for ticket
            if key == "mensaje_ticket":
                entry.insert(0, "¡Gracias por su compra!")
        
        def guardar():
            nombre = inputs["nombre_empresa"].get().strip()
            if not nombre:
                messagebox.showwarning("Falta información", "El Nombre del Negocio es obligatorio.", parent=setup_win)
                return
            
            propietario = inputs["propietario"].get().strip()
            telefono = inputs["telefono"].get().strip()
            direccion = inputs["direccion"].get().strip()
            mensaje = inputs["mensaje_ticket"].get().strip() or "¡Gracias por su compra!"
            
            impresora = combo_printer.get()
            if impresora == "Ninguna (Solo PDF/Guardar)":
                impresora = ""
                
            database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora)
            
            self.config = {
                "nombre_empresa": nombre,
                "propietario": propietario,
                "telefono": telefono,
                "direccion": direccion,
                "mensaje_ticket": mensaje,
                "impresora_ticket": impresora
            }
            
            # Update title
            self.root.title(f"Control de Inventario y Ventas - {nombre}")
            setup_win.destroy()
            self.mostrar_registro_administrador()
            
        # Impresora Combobox
        tk.Label(frame_form, text="Impresora de Tickets", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(6, 1))
        border_printer = tk.Frame(frame_form, bg="#E2E8F0")
        border_printer.pack(fill=tk.X, padx=20, pady=1)
        
        printers_list = ["Ninguna (Solo PDF/Guardar)"] + self.obtener_impresoras_sistema()
        combo_printer = ttk.Combobox(border_printer, values=printers_list, state="readonly", font=("Segoe UI", 9))
        combo_printer.pack(fill=tk.X, padx=1, pady=1)
        combo_printer.set("Ninguna (Solo PDF/Guardar)")
        
        btn_guardar = tk.Button(frame_form, text="Siguiente: Crear Cuenta", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar)
        btn_guardar.pack(fill=tk.X, padx=20, pady=15, ipady=8)
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#059669"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#10B981"))


    def mostrar_registro_administrador(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Registro de Administrador")
        reg_win.geometry("400x400")
        reg_win.configure(bg="#F8FAFC")
        reg_win.resizable(False, False)
        
        # Center the window
        reg_win.update_idletasks()
        width = reg_win.winfo_width()
        height = reg_win.winfo_height()
        x = (reg_win.winfo_screenwidth() // 2) - (width // 2)
        y = (reg_win.winfo_screenheight() // 2) - (height // 2)
        reg_win.geometry(f'+{x}+{y}')
        
        # If they close this window, exit the app
        def on_close():
            self.root.destroy()
            sys.exit(0)
        reg_win.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header
        frame_header = tk.Frame(reg_win, bg="#4F46E5") # Indigo banner
        frame_header.pack(fill=tk.X)
        
        tk.Label(frame_header, text="🔒 REGISTRO DE ADMINISTRADOR", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white").pack(pady=15)
        
        tk.Label(reg_win, text="Crea tu cuenta de usuario administrador para proteger\nel acceso y poder ingresar al sistema POS.", 
                 font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#64748B", justify=tk.CENTER).pack(pady=15)
        
        # Form Container
        frame_form = tk.Frame(reg_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=45, pady=(0, 25))
        
        tk.Label(frame_form, text="Usuario Administrador *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(15, 2))
        border_user = tk.Frame(frame_form, bg="#E2E8F0")
        border_user.pack(fill=tk.X, padx=20, pady=2)
        entry_user = tk.Entry(border_user, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
        entry_user.pack(fill=tk.X, padx=1, pady=1, ipady=4)
        entry_user.insert(0, "admin")
        
        tk.Label(frame_form, text="Contraseña *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(10, 2))
        border_pass = tk.Frame(frame_form, bg="#E2E8F0")
        border_pass.pack(fill=tk.X, padx=20, pady=2)
        entry_pass = tk.Entry(border_pass, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A", show="*")
        entry_pass.pack(fill=tk.X, padx=1, pady=1, ipady=4)
        
        def guardar_usuario():
            user = entry_user.get().strip()
            password = entry_pass.get().strip()
            
            if not user:
                messagebox.showwarning("Falta información", "El Usuario Administrador es obligatorio.", parent=reg_win)
                return
            if not password or len(password) < 4:
                messagebox.showwarning("Contraseña inválida", "La contraseña es obligatoria y debe tener al menos 4 caracteres.", parent=reg_win)
                return
                
            exito = database.crear_usuario(user, password, "Administrador")
            if exito:
                reg_win.destroy()
                self.mostrar_login()
            else:
                messagebox.showerror("Error", "No se pudo registrar el usuario. El nombre de usuario ya existe.", parent=reg_win)
                
        btn_crear = tk.Button(frame_form, text="Crear Cuenta y Continuar", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar_usuario)
        btn_crear.pack(fill=tk.X, padx=20, pady=25, ipady=8)
        btn_crear.bind("<Enter>", lambda e: btn_crear.config(bg="#059669"))
        btn_crear.bind("<Leave>", lambda e: btn_crear.config(bg="#10B981"))

    def mostrar_login(self):
        login_win = tk.Toplevel(self.root)
        login_win.title("Iniciar Sesión")
        login_win.geometry("400x480")
        login_win.configure(bg="#F8FAFC")
        login_win.resizable(False, False)
        
        # Center the window
        login_win.update_idletasks()
        width = login_win.winfo_width()
        height = login_win.winfo_height()
        x = (login_win.winfo_screenwidth() // 2) - (width // 2)
        y = (login_win.winfo_screenheight() // 2) - (height // 2)
        login_win.geometry(f'+{x}+{y}')
        
        # If they close the login window, close the app
        def on_close():
            self.root.destroy()
            sys.exit(0)
        login_win.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header
        frame_header = tk.Frame(login_win, bg="#1E293B") # Dark Slate premium banner
        frame_header.pack(fill=tk.X)
        
        nombre_empresa = self.config["nombre_empresa"].upper() if self.config else "SISTEMA POS"
        tk.Label(frame_header, text=nombre_empresa, font=("Segoe UI", 12, "bold"), bg="#1E293B", fg="#FFFFFF").pack(pady=(15, 2))
        tk.Label(frame_header, text="CONTROL DE ACCESO", font=("Segoe UI", 8, "bold"), bg="#1E293B", fg="#38BDF8").pack(pady=(0, 15))
        
        # Icon / Graphic element
        tk.Label(login_win, text="🔒", font=("Segoe UI", 36), bg="#F8FAFC").pack(pady=20)
        
        # Form Container
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
                self.current_user = usuario_autenticado
                login_win.destroy()
                self.root.deiconify() # Show the main app window!
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

    def cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?")
        if confirmar:
            self.root.withdraw()
            self.current_user = None
            self.mostrar_login()

    def mostrar_editar_configuracion(self):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Editar Configuración del Negocio")
        edit_win.geometry("450x690")
        edit_win.configure(bg="#F8FAFC")
        edit_win.resizable(False, False)
        edit_win.grab_set()

        
        # Center the window
        edit_win.update_idletasks()
        width = edit_win.winfo_width()
        height = edit_win.winfo_height()
        x = (edit_win.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_win.winfo_screenheight() // 2) - (height // 2)
        edit_win.geometry(f'+{x}+{y}')
        
        # Header
        frame_header = tk.Frame(edit_win, bg="#4F46E5")
        frame_header.pack(fill=tk.X)
        tk.Label(frame_header, text="⚙️ CONFIGURACIÓN DEL NEGOCIO", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white").pack(pady=15)
        
        tk.Label(edit_win, text="Modifica los datos de tu empresa. Los cambios se reflejarán\nde inmediato en los nuevos tickets y reportes.", 
                 font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#64748B", justify=tk.CENTER).pack(pady=15)
        
        # Form Container
        frame_form = tk.Frame(edit_win, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        inputs = {}
        campos_setup = [
            ("Nombre del Negocio *", "nombre_empresa"),
            ("Propietario / Administrador", "propietario"),
            ("Teléfono de Contacto", "telefono"),
            ("Dirección del Local", "direccion"),
            ("Mensaje al Pie del Ticket", "mensaje_ticket")
        ]
        
        current_config = database.obtener_configuracion() or {
            "nombre_empresa": "",
            "propietario": "",
            "telefono": "",
            "direccion": "",
            "mensaje_ticket": "¡Gracias por su compra!"
        }
        
        for label_text, key in campos_setup:
            tk.Label(frame_form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(10, 2))
            border_frame = tk.Frame(frame_form, bg="#E2E8F0")
            border_frame.pack(fill=tk.X, padx=20, pady=2)
            entry = tk.Entry(border_frame, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
            entry.pack(fill=tk.X, padx=1, pady=1, ipady=4)
            inputs[key] = entry
            
            # Load current value
            entry.insert(0, current_config.get(key, ""))
            
        # Impresora Combobox
        tk.Label(frame_form, text="Impresora de Tickets", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569").pack(anchor=tk.W, padx=20, pady=(6, 1))
        
        frame_printer_line = tk.Frame(frame_form, bg="#FFFFFF")
        frame_printer_line.pack(fill=tk.X, padx=20, pady=2)
        
        border_printer = tk.Frame(frame_printer_line, bg="#E2E8F0")
        border_printer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        printers_list = ["Ninguna (Solo PDF/Guardar)"] + self.obtener_impresoras_sistema()
        combo_printer = ttk.Combobox(border_printer, values=printers_list, state="readonly", font=("Segoe UI", 9))
        combo_printer.pack(fill=tk.X, padx=1, pady=1)
        
        curr_printer = current_config.get("impresora_ticket", "")
        if curr_printer and curr_printer in printers_list:
            combo_printer.set(curr_printer)
        else:
            combo_printer.set("Ninguna (Solo PDF/Guardar)")
            
        def probar_impresora():
            impresora_sel = combo_printer.get()
            if impresora_sel == "Ninguna (Solo PDF/Guardar)" or not impresora_sel:
                messagebox.showwarning("Atención", "Selecciona una impresora de la lista para probarla.", parent=edit_win)
                return
            
            # Send test print text
            texto_test = (
                "==========================================\n"
                "           PRUEBA DE IMPRESIÓN            \n"
                "==========================================\n"
                f"Impresora: {impresora_sel}\n"
                "Estado: Conectada y operativa.\n\n"
                "¡Conexión establecida con éxito!\n"
                "==========================================\n"
            )
            exito, msg = self.enviar_impresion_directa(impresora_sel, texto_test)
            if exito:
                messagebox.showinfo("Éxito", "Prueba enviada a la impresora.", parent=edit_win)
            else:
                messagebox.showerror("Error", f"Fallo al imprimir prueba:\n{msg}", parent=edit_win)
                
        btn_probar = tk.Button(frame_printer_line, text="Probar", font=("Segoe UI", 8, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, cursor="hand2", command=probar_impresora)
        btn_probar.pack(side=tk.LEFT, padx=(5, 0), ipady=3, ipadx=10)
        btn_probar.bind("<Enter>", lambda e: btn_probar.config(bg="#CBD5E1"))
        btn_probar.bind("<Leave>", lambda e: btn_probar.config(bg="#E2E8F0"))
        
        def guardar():
            nombre = inputs["nombre_empresa"].get().strip()
            if not nombre:
                messagebox.showwarning("Falta información", "El Nombre del Negocio es obligatorio.", parent=edit_win)
                return
            
            propietario = inputs["propietario"].get().strip()
            telefono = inputs["telefono"].get().strip()
            direccion = inputs["direccion"].get().strip()
            mensaje = inputs["mensaje_ticket"].get().strip() or "¡Gracias por su compra!"
            
            impresora = combo_printer.get()
            if impresora == "Ninguna (Solo PDF/Guardar)":
                impresora = ""
                
            database.guardar_configuracion(nombre, propietario, telefono, direccion, mensaje, impresora)
            self.config = {
                "nombre_empresa": nombre,
                "propietario": propietario,
                "telefono": telefono,
                "direccion": direccion,
                "mensaje_ticket": mensaje,
                "impresora_ticket": impresora
            }
            
            # Update title and close
            self.root.title(f"Control de Inventario y Ventas - {nombre}")
            edit_win.destroy()
            messagebox.showinfo("Éxito", "Configuración actualizada correctamente.")
            
        btn_guardar = tk.Button(frame_form, text="Guardar Cambios", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar)
        btn_guardar.pack(fill=tk.X, padx=20, pady=15, ipady=8)
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#059669"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#10B981"))


    def mostrar_splash(self, config):
        self.root.withdraw()
        
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.configure(bg="#1E293B")
        
        # Geometry and centering
        width = 500
        height = 300
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Layout
        frame_content = tk.Frame(splash, bg="#1E293B")
        frame_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        tk.Label(frame_content, text="SISTEMA POS", font=("Segoe UI", 10, "bold"), bg="#1E293B", fg="#38BDF8").pack(pady=(15, 5))
        
        # Divider
        divider = tk.Frame(frame_content, bg="#334155", height=2)
        divider.pack(fill=tk.X, pady=10)
        
        # Business name
        tk.Label(frame_content, text=config["nombre_empresa"].upper(), font=("Segoe UI", 20, "bold"), bg="#1E293B", fg="#FFFFFF", wraplength=440).pack(pady=15)
        
        tk.Label(frame_content, text="Iniciando base de datos y componentes...", font=("Segoe UI", 9, "italic"), bg="#1E293B", fg="#94A3B8").pack(pady=(10, 0))
        
        # Loader line simulation
        loader_bg = tk.Frame(frame_content, bg="#334155", height=4)
        loader_bg.pack(fill=tk.X, pady=(15, 0))
        loader_fg = tk.Frame(loader_bg, bg="#10B981", height=4, width=1)
        loader_fg.pack(side=tk.LEFT)
        
        # Simple animation
        def animate(w):
            if w < 440:
                loader_fg.config(width=w)
                splash.after(15, lambda: animate(w + 5))
        
        animate(1)
        
        def cerrar_splash():
            splash.destroy()
            self.mostrar_login()
            
        self.root.after(2000, cerrar_splash)


    def obtener_ruta_imagenes(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "imagenes_productos")
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def obtener_impresoras_sistema(self):
        try:
            winspool = ctypes.WinDLL('winspool.drv')
            flags = 2 | 4 # PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS
            level = 4
            
            class PRINTER_INFO_4(ctypes.Structure):
                _fields_ = [
                    ("pPrinterName", ctypes.c_wchar_p),
                    ("pServerName", ctypes.c_wchar_p),
                    ("Attributes", ctypes.c_uint32)
                ]
                
            needed = ctypes.c_ulong(0)
            returned = ctypes.c_ulong(0)
            
            # Obtener el tamaño necesario
            winspool.EnumPrintersW(flags, None, level, None, 0, ctypes.byref(needed), ctypes.byref(returned))
            if needed.value == 0:
                return []
                
            buffer = ctypes.create_string_buffer(needed.value)
            if winspool.EnumPrintersW(flags, None, level, buffer, needed.value, ctypes.byref(needed), ctypes.byref(returned)):
                array_type = PRINTER_INFO_4 * returned.value
                printers = array_type.from_buffer(buffer)
                return [p.pPrinterName for p in printers]
        except Exception:
            pass
        return []

    def enviar_impresion_directa(self, nombre_impresora, texto_ticket):
        try:
            winspool = ctypes.WinDLL('winspool.drv')
            
            hPrinter = ctypes.c_void_p()
            if not winspool.OpenPrinterW(nombre_impresora, ctypes.byref(hPrinter), None):
                raise Exception(f"No se pudo abrir la impresora '{nombre_impresora}'.")
                
            try:
                class DOC_INFO_1(ctypes.Structure):
                    _fields_ = [
                        ("pDocName", ctypes.c_wchar_p),
                        ("pOutputFile", ctypes.c_wchar_p),
                        ("pDatatype", ctypes.c_wchar_p)
                    ]
                    
                doc_info = DOC_INFO_1()
                doc_info.pDocName = "Ticket de Venta POS"
                doc_info.pOutputFile = None
                doc_info.pDatatype = "RAW"
                
                doc_id = winspool.StartDocPrinterW(hPrinter, 1, ctypes.byref(doc_info))
                if doc_id <= 0:
                    raise Exception("No se pudo iniciar el documento en el spooler.")
                    
                try:
                    if not winspool.StartPagePrinter(hPrinter):
                        raise Exception("No se pudo iniciar la página en el spooler.")
                        
                    try:
                        # Inicializar impresora (ESC @)
                        init_printer = b"\x1b\x40"
                        # Pulso de apertura cajón monedero
                        open_drawer = b"\x1b\x70\x00\x19\xfa"
                        
                        # Codificar en cp1252 para conservar tildes/eñes
                        ticket_bytes = texto_ticket.encode('cp1252', errors='replace')
                        
                        # Avance de líneas y corte de papel automático
                        feed_and_cut = b"\n\n\n\n\x1d\x56\x42\x00"
                        
                        data_to_send = init_printer + open_drawer + ticket_bytes + feed_and_cut
                        
                        bytes_written = ctypes.c_ulong(0)
                        if not winspool.WritePrinter(hPrinter, data_to_send, len(data_to_send), ctypes.byref(bytes_written)):
                            raise Exception("Error al escribir los bytes en el spooler.")
                    finally:
                        winspool.EndPagePrinter(hPrinter)
                finally:
                    winspool.EndDocPrinter(hPrinter)
            finally:
                winspool.ClosePrinter(hPrinter)
            return True, "Ticket enviado correctamente."
        except Exception as e:
            return False, str(e)


    def crear_interfaz(self):
        # --- Estilos Globales de ttk ---
        style = ttk.Style()
        style.theme_use("clam")
        
        # Estilo del Notebook (Pestañas)
        style.configure("TNotebook", background="#F8FAFC", borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background="#E2E8F0", 
                        foreground="#475569", 
                        padding=[18, 8], 
                        font=("Segoe UI", 10, "bold"), 
                        borderwidth=0)
        style.map("TNotebook.Tab", 
                  background=[("selected", "#FFFFFF"), ("active", "#CBD5E1")],
                  foreground=[("selected", "#4F46E5")])

        # Estilo de la Tabla (Treeview)
        style.configure("Treeview", 
                        background="#FFFFFF", 
                        foreground="#334155", 
                        rowheight=36, 
                        font=("Segoe UI", 10),
                        fieldbackground="#FFFFFF",
                        borderwidth=0,
                        highlightthickness=0)
                        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background="#1E293B", 
                        foreground="white",
                        borderwidth=0,
                        relief="flat")
                        
        style.map("Treeview.Heading", background=[('active', '#0F172A')])
        style.map("Treeview", 
                  background=[('selected', '#E0E7FF')], 
                  foreground=[('selected', '#312E81')])

        # Contenedor principal de pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear frames para cada pestaña
        self.tab_inventario = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_pos = tk.Frame(self.notebook, bg="#F8FAFC")
        self.tab_reportes = tk.Frame(self.notebook, bg="#F8FAFC")

        # Agregar pestañas
        self.notebook.add(self.tab_inventario, text=" 📦 Inventario ")
        self.notebook.add(self.tab_pos, text=" 🛒 Punto de Venta ")
        self.notebook.add(self.tab_reportes, text=" 📊 Historial de Ventas ")

        # Evento al cambiar de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Construir cada sección
        self.construir_tab_inventario()
        self.construir_tab_pos()
        self.construir_tab_reportes()

    # ==========================================
    # ACTUALIZAR BADGE DE ALERTAS
    # ==========================================
    def pos_actualizar_alertas_pestaña(self):
        try:
            alertas = database.obtener_alertas_stock()
            if alertas > 0:
                self.notebook.tab(0, text=f" 📦 Inventario ({alertas} 🚨) ")
            else:
                self.notebook.tab(0, text=" 📦 Inventario ")
        except Exception:
            pass

    # ==========================================
    # VISTA PREVIA DE IMAGEN (HELPER)
    # ==========================================
    def actualizar_vista_previa_label(self, label, ruta, tamano):
        try:
            if not ruta or not os.path.exists(ruta):
                label.config(image="", text="Sin imagen", compound="center")
                label.image = None
                return
            img = Image.open(ruta)
            # Redimensionamiento proporcional manteniendo la relación de aspecto original
            img.thumbnail(tamano, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text="", compound="center")
            label.image = photo # Conservar referencia
        except Exception:
            label.config(image="", text="Error de imagen", compound="center")
            label.image = None

    # ==========================================
    # PESTAÑA 1: INVENTARIO
    # ==========================================
    def construir_tab_inventario(self):
        # Panel Izquierdo (Formulario)
        frame_form = tk.Frame(self.tab_inventario, bg="#FFFFFF", width=340, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        frame_form.pack_propagate(False)

        tk.Label(frame_form, text="REGISTRAR PRODUCTO", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=(10, 5))

        # Grid frame for compact 2-column inputs
        grid_inputs = tk.Frame(frame_form, bg="#FFFFFF")
        grid_inputs.pack(fill=tk.X, padx=15, pady=(5, 5))
        
        grid_inputs.columnconfigure(0, weight=1)
        grid_inputs.columnconfigure(1, weight=1)
        
        campos = [
            ("Referencia *", "codigo", 0, 0),
            ("Nombre *", "nombre", 0, 1),
            ("Precio Costo", "costo", 1, 0),
            ("Precio Venta", "venta", 1, 1),
            ("Stock Inicial", "stock", 2, 0),
            ("Stock Mínimo", "min_stock", 2, 1)
        ]
        
        self.inputs = {}
        for label_text, key, row, col in campos:
            cell = tk.Frame(grid_inputs, bg="#FFFFFF")
            cell.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")
            
            tk.Label(cell, text=label_text, font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W, pady=(0, 1))
            border_frame = tk.Frame(cell, bg="#E2E8F0")
            border_frame.pack(fill=tk.X)
            entry = tk.Entry(border_frame, font=("Segoe UI", 9), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
            entry.pack(fill=tk.X, padx=1, pady=1, ipady=3)
            self.inputs[key] = entry

        self.inputs["min_stock"].insert(0, "3")

        # Campo para Imagen (No obligatorio)
        tk.Label(frame_form, text="Imagen del Producto", font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W, padx=20, pady=(5, 1))
        frame_img_sel = tk.Frame(frame_form, bg="#FFFFFF")
        frame_img_sel.pack(fill=tk.X, padx=20, pady=2)
        
        self.btn_select_img = tk.Button(frame_img_sel, text="Seleccionar Foto", font=("Segoe UI", 8, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, cursor="hand2", command=self.pos_seleccionar_imagen)
        self.btn_select_img.pack(side=tk.LEFT, ipady=3, ipadx=8)
        self.btn_select_img.bind("<Enter>", lambda e: self.btn_select_img.config(bg="#CBD5E1"))
        self.btn_select_img.bind("<Leave>", lambda e: self.btn_select_img.config(bg="#E2E8F0"))
        
        self.lbl_img_path = tk.Label(frame_img_sel, text="Sin foto", font=("Segoe UI", 8), bg="#FFFFFF", fg="#94A3B8", anchor=tk.W)
        self.lbl_img_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Recuadro Vista Previa Formulario (contenedor de tamaño fijo en píxeles más compacto)
        frame_form_img_container = tk.Frame(frame_form, bg="#F8FAFC", width=280, height=120, bd=1, relief=tk.SOLID)
        frame_form_img_container.pack(pady=5, padx=20, fill=tk.X)
        frame_form_img_container.pack_propagate(False)
        self.lbl_img_preview = tk.Label(frame_form_img_container, text="Sin vista previa", font=("Segoe UI", 8, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_img_preview.pack(expand=True, fill=tk.BOTH)

        btn_guardar = tk.Button(frame_form, text="Guardar Producto", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, 
                                activebackground="#3730A3", activeforeground="white", cursor="hand2", command=self.guardar_producto)
        btn_guardar.pack(fill=tk.X, padx=25, pady=(5, 2), ipady=7)
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#4338CA"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#4F46E5"))

        # Botón de Vaciar Base de Datos (Mantenimiento de pruebas)
        btn_reset = tk.Button(frame_form, text="Vaciar Todo (Reiniciar)", font=("Segoe UI", 8, "bold"), bg="#FFF5F5", fg="#EF4444", bd=0, cursor="hand2", command=self.reiniciar_sistema)
        btn_reset.pack(fill=tk.X, padx=25, pady=(2, 5), ipady=3)

        # Panel Derecho (Tabla y Buscador)
        frame_grid = tk.Frame(self.tab_inventario, bg="#F8FAFC")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)

        # Buscador
        frame_busca = tk.Frame(frame_grid, bg="#F8FAFC")
        frame_busca.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_busca, text="Buscar:", font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg="#475569").pack(side=tk.LEFT, padx=(5, 10))
        
        busca_border = tk.Frame(frame_busca, bg="#E2E8F0")
        busca_border.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar = tk.Entry(busca_border, font=("Segoe UI", 10), bg="#FFFFFF", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
        self.entry_buscar.pack(fill=tk.X, padx=1, pady=1, ipady=5)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        # Botones de ajuste de stock y Vista Previa de Tabla (Empacar primero a la derecha)
        frame_botones = tk.Frame(frame_grid, bg="#F8FAFC")
        frame_botones.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        btn_mas = tk.Button(frame_botones, text="+", font=("Segoe UI", 14, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, width=3, cursor="hand2", command=lambda: self.ajustar_stock(1))
        btn_mas.pack(pady=5, ipady=6)

        # Tabla (Empacar después a la izquierda para ocupar el resto del espacio)
        columnas = ("id", "codigo", "nombre", "costo", "venta", "stock", "min_stock")
        self.tabla = ttk.Treeview(frame_grid, columns=columnas, show="headings")
        
        headers = [("ID", 40), ("Referencia", 100), ("Nombre", 220), ("Costo", 90), ("Venta", 90), ("Stock", 70), ("Mínimo", 70)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)

        self.tabla.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tabla.tag_configure("alerta", background="#FEF2F2", foreground="#991B1B")
        
        # Enlazar selección
        self.tabla.bind("<<TreeviewSelect>>", self.inv_on_producto_select)
        btn_menos = tk.Button(frame_botones, text="-", font=("Segoe UI", 14, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, width=3, cursor="hand2", command=lambda: self.ajustar_stock(-1))
        btn_menos.pack(pady=5, ipady=6)

        btn_mas.bind("<Enter>", lambda e: btn_mas.config(bg="#CBD5E1"))
        btn_mas.bind("<Leave>", lambda e: btn_mas.config(bg="#E2E8F0"))
        btn_menos.bind("<Enter>", lambda e: btn_menos.config(bg="#CBD5E1"))
        btn_menos.bind("<Leave>", lambda e: btn_menos.config(bg="#E2E8F0"))
        
        # Recuadro Imagen de Producto Seleccionado
        tk.Label(frame_botones, text="Foto:", font=("Segoe UI", 9, "bold"), bg="#F8FAFC", fg="#64748B").pack(pady=(15, 2))
        frame_inv_img_container = tk.Frame(frame_botones, bg="#FFFFFF", width=240, height=200, bd=1, relief=tk.SOLID)
        frame_inv_img_container.pack(pady=2, fill=tk.X)
        frame_inv_img_container.pack_propagate(False)
        self.lbl_inv_foto_preview = tk.Label(frame_inv_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#94A3B8", compound="center")
        self.lbl_inv_foto_preview.pack(expand=True, fill=tk.BOTH)

    def pos_seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen del Producto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.gif")]
        )
        if ruta:
            self.imagen_ruta_form = ruta
            nombre_archivo = ruta.split("/")[-1]
            self.lbl_img_path.config(text=nombre_archivo, fg="#0F172A")
            self.actualizar_vista_previa_label(self.lbl_img_preview, ruta, (270, 110))

    def inv_on_producto_select(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.lbl_inv_foto_preview.config(image="", text="Sin foto")
            self.lbl_inv_foto_preview.image = None
            return
        valores = self.tabla.item(seleccion[0])["values"]
        p_id = int(valores[0])
        
        # Buscar la ruta de la imagen en la base de datos
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT imagen_ruta FROM productos WHERE id = ?", (p_id,))
            res = cursor.fetchone()
            if res and res[0]:
                self.actualizar_vista_previa_label(self.lbl_inv_foto_preview, res[0], (230, 190))
            else:
                self.lbl_inv_foto_preview.config(image="", text="Sin foto")
                self.lbl_inv_foto_preview.image = None

    # ==========================================
    # PESTAÑA 2: PUNTO DE VENTA (POS)
    # ==========================================
    def construir_tab_pos(self):
        # Panel Izquierdo (Búsqueda de Productos para venta)
        frame_pos_left = tk.Frame(self.tab_pos, bg="#FFFFFF", width=460, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_pos_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame_pos_left, text="SELECCIONAR PRODUCTO", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=15)
        
        # Entrada de Búsqueda POS
        frame_busca_pos = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_busca_pos.pack(fill=tk.X, padx=15, pady=(0, 10))
        tk.Label(frame_busca_pos, text="Buscar:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=(5, 10))
        
        busca_pos_border = tk.Frame(frame_busca_pos, bg="#E2E8F0")
        busca_pos_border.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busca_pos = tk.Entry(busca_pos_border, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0)
        self.entry_busca_pos.pack(fill=tk.X, padx=1, pady=1, ipady=5)
        self.entry_busca_pos.bind("<KeyRelease>", lambda e: self.pos_actualizar_lista_productos(self.entry_busca_pos.get()))
        self.entry_busca_pos.bind("<Return>", self.pos_on_busca_enter)
        
        # Tabla de Productos para POS
        columnas_prod = ("id", "codigo", "nombre", "precio", "stock")
        self.tabla_pos_prod = ttk.Treeview(frame_pos_left, columns=columnas_prod, show="headings")
        
        headers_prod = [("ID", 40), ("Referencia", 90), ("Nombre", 160), ("Precio", 85), ("Stock", 65)]
        for col, (texto, ancho) in zip(columnas_prod, headers_prod):
            self.tabla_pos_prod.heading(col, text=texto)
            self.tabla_pos_prod.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
        self.tabla_pos_prod.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Escuchar evento de selección
        self.tabla_pos_prod.bind("<<TreeviewSelect>>", self.pos_on_producto_select)
        
        # Control de Cantidad, Precio Venta y Agregar
        frame_control_add = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_control_add.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(frame_control_add, text="Cant:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=2)
        self.entry_cant_pos = tk.Entry(frame_control_add, font=("Segoe UI", 10, "bold"), width=5, bg="#F8FAFC", bd=1, relief=tk.SOLID, justify=tk.CENTER)
        self.entry_cant_pos.pack(side=tk.LEFT, padx=5, ipady=3)
        self.entry_cant_pos.insert(0, "1")
        self.entry_cant_pos.bind("<Return>", self.pos_on_cant_enter)

        tk.Label(frame_control_add, text="Precio Venta ($):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=(10, 2))
        self.entry_precio_pos = tk.Entry(frame_control_add, font=("Segoe UI", 10, "bold"), width=10, bg="#F8FAFC", bd=1, relief=tk.SOLID, justify=tk.CENTER)
        self.entry_precio_pos.pack(side=tk.LEFT, padx=5, ipady=3)
        self.entry_precio_pos.bind("<Return>", self.pos_on_precio_enter)
        
        btn_agregar_carro = tk.Button(frame_control_add, text="Agregar", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=self.pos_agregar_al_carrito)
        btn_agregar_carro.pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)
        btn_agregar_carro.bind("<Enter>", lambda e: btn_agregar_carro.config(bg="#4338CA"))
        btn_agregar_carro.bind("<Leave>", lambda e: btn_agregar_carro.config(bg="#4F46E5"))

        # Recuadro Imagen de Vista Previa POS
        frame_pos_preview = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_pos_preview.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        tk.Label(frame_pos_preview, text="Imagen del Producto:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B").pack(side=tk.LEFT, padx=5, anchor=tk.N)
        frame_pos_img_container = tk.Frame(frame_pos_preview, bg="#F8FAFC", width=240, height=180, bd=1, relief=tk.SOLID)
        frame_pos_img_container.pack(side=tk.LEFT, padx=10)
        frame_pos_img_container.pack_propagate(False)
        self.lbl_pos_foto_preview = tk.Label(frame_pos_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_pos_foto_preview.pack(expand=True, fill=tk.BOTH)

        # Panel Derecho (Carrito de Compra)
        frame_pos_right = tk.Frame(self.tab_pos, bg="#FFFFFF", width=540, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_pos_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)
        
        tk.Label(frame_pos_right, text="CARRITO DE VENTAS", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=15)
        
        # Tabla Carrito
        columnas_carro = ("id", "codigo", "nombre", "precio", "cantidad", "total")
        self.tabla_carro = ttk.Treeview(frame_pos_right, columns=columnas_carro, show="headings")
        headers_carro = [("ID", 40), ("Referencia", 90), ("Nombre", 160), ("Precio", 80), ("Cant.", 60), ("Total", 90)]
        for col, (texto, ancho) in zip(columnas_carro, headers_carro):
            self.tabla_carro.heading(col, text=texto)
            self.tabla_carro.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
        self.tabla_carro.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Panel de cobro y total
        frame_total = tk.Frame(frame_pos_right, bg="#FFFFFF")
        frame_total.pack(fill=tk.X, padx=15, pady=15)
        
        self.lbl_total_pos = tk.Label(frame_total, text="TOTAL: $0", font=("Segoe UI", 15, "bold"), bg="#FFFFFF", fg="#0F172A")
        self.lbl_total_pos.pack(side=tk.LEFT, padx=5)
        
        btn_quitar = tk.Button(frame_total, text="Quitar", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.pos_quitar_del_carrito)
        btn_quitar.pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)
        
        btn_registrar_venta = tk.Button(frame_total, text="Registrar Venta", font=("Segoe UI", 11, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=self.pos_procesar_venta)
        btn_registrar_venta.pack(side=tk.RIGHT, padx=10, ipady=5, ipadx=15)
        btn_registrar_venta.bind("<Enter>", lambda e: btn_registrar_venta.config(bg="#059669"))
        btn_registrar_venta.bind("<Leave>", lambda e: btn_registrar_venta.config(bg="#10B981"))

        # Selector de Método de Pago
        tk.Label(frame_total, text="Pago:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.RIGHT, padx=(10, 5))
        self.combo_pago = ttk.Combobox(frame_total, values=["Efectivo", "Transferencia"], state="readonly", width=12, font=("Segoe UI", 10))
        self.combo_pago.pack(side=tk.RIGHT, padx=5, ipady=2)
        self.combo_pago.set("Efectivo")

    # ==========================================
    # PESTAÑA 3: HISTORIAL DE VENTAS
    # ==========================================
    def construir_tab_reportes(self):
        # Panel superior con 4 tarjetas de resumen financiero
        frame_cards = tk.Frame(self.tab_reportes, bg="#F8FAFC")
        frame_cards.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Tarjeta 1: Ventas Totales del Rango
        self.card_hoy = tk.Frame(frame_cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        self.card_hoy.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=12)
        
        self.lbl_card_hoy_titulo = tk.Label(self.card_hoy, text="Ventas del Período", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B")
        self.lbl_card_hoy_titulo.pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.lbl_card_hoy_valor = tk.Label(self.card_hoy, text="$0", font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#4F46E5")
        self.lbl_card_hoy_valor.pack(anchor=tk.W, padx=15, pady=(2, 0))
        self.lbl_card_hoy_sub = tk.Label(self.card_hoy, text="0 transacciones", font=("Segoe UI", 8), bg="#FFFFFF", fg="#94A3B8")
        self.lbl_card_hoy_sub.pack(anchor=tk.W, padx=15)

        # Tarjeta 2: Ingresos por Tipo de Pago
        self.card_total = tk.Frame(frame_cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        self.card_total.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=12)
        
        self.lbl_card_tot_titulo = tk.Label(self.card_total, text="Ingresos por Pago", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B")
        self.lbl_card_tot_titulo.pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.lbl_card_tot_valor = tk.Label(self.card_total, text="Efectivo / Transferencia", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#0F172A")
        self.lbl_card_tot_valor.pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.lbl_card_tot_sub = tk.Label(self.card_total, text="Efe: $0 | Transf: $0", font=("Segoe UI", 9), bg="#FFFFFF", fg="#475569")
        self.lbl_card_tot_sub.pack(anchor=tk.W, padx=15)

        # Tarjeta 3: Utilidad Real (Ganancia Neta)
        self.card_utilidad = tk.Frame(frame_cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        self.card_utilidad.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=12)
        
        self.lbl_card_ut_titulo = tk.Label(self.card_utilidad, text="Ganancia Neta (Utilidad)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B")
        self.lbl_card_ut_titulo.pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.lbl_card_ut_valor = tk.Label(self.card_utilidad, text="$0", font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#10B981")
        self.lbl_card_ut_valor.pack(anchor=tk.W, padx=15, pady=(2, 0))
        self.lbl_card_ut_sub = tk.Label(self.card_utilidad, text="Ingreso - Costo Adquisición", font=("Segoe UI", 8), bg="#FFFFFF", fg="#059669")
        self.lbl_card_ut_sub.pack(anchor=tk.W, padx=15)

        # Tarjeta 4: Top 3 Más Vendidos
        self.card_top = tk.Frame(frame_cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        self.card_top.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=12)
        
        self.lbl_card_top_titulo = tk.Label(self.card_top, text="Top 3 Más Vendidos", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B")
        self.lbl_card_top_titulo.pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.lbl_card_top_valor = tk.Label(self.card_top, text="Cargando...", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155", justify=tk.LEFT)
        self.lbl_card_top_valor.pack(anchor=tk.W, padx=15, pady=(5, 0))

        # Grid de Reportes
        frame_reporte_grid = tk.Frame(self.tab_reportes, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        frame_reporte_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header de controles (Filtro de fecha y botones de acción)
        frame_controles_rep = tk.Frame(frame_reporte_grid, bg="#FFFFFF")
        frame_controles_rep.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(frame_controles_rep, text="TRANSACCIONES REGISTRADAS", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side=tk.LEFT)
        
        # Selector de Fecha
        tk.Label(frame_controles_rep, text="Filtrar:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B").pack(side=tk.LEFT, padx=(30, 5))
        self.combo_filtro_fecha = ttk.Combobox(frame_controles_rep, values=["Todo", "Hoy", "Últimos 7 días", "Este Mes"], state="readonly", width=15, font=("Segoe UI", 9))
        self.combo_filtro_fecha.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_fecha.set("Todo")
        self.combo_filtro_fecha.bind("<<ComboboxSelected>>", lambda e: self.reporte_actualizar_datos())
        
        # Botones de Acciones en Reportes
        btn_exportar = tk.Button(frame_controles_rep, text="Exportar Reporte (CSV)", font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="white", bd=0, cursor="hand2", command=self.exportar_reporte_csv)
        btn_exportar.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_exportar.bind("<Enter>", lambda e: btn_exportar.config(bg="#0F172A"))
        btn_exportar.bind("<Leave>", lambda e: btn_exportar.config(bg="#1E293B"))

        btn_corte = tk.Button(frame_controles_rep, text="Corte de Caja", font=("Segoe UI", 9, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=self.generar_corte_caja)
        btn_corte.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_corte.bind("<Enter>", lambda e: btn_corte.config(bg="#059669"))
        btn_corte.bind("<Leave>", lambda e: btn_corte.config(bg="#10B981"))

        btn_backup = tk.Button(frame_controles_rep, text="Respaldar DB", font=("Segoe UI", 9, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=self.respaldar_base_datos)
        btn_backup.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_backup.bind("<Enter>", lambda e: btn_backup.config(bg="#3730A3"))
        btn_backup.bind("<Leave>", lambda e: btn_backup.config(bg="#4F46E5"))

        btn_anular = tk.Button(frame_controles_rep, text="Anular Venta", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.anular_venta_seleccionada)
        btn_anular.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_anular.bind("<Enter>", lambda e: btn_anular.config(bg="#DC2626"))
        btn_anular.bind("<Leave>", lambda e: btn_anular.config(bg="#EF4444"))

        btn_config = tk.Button(frame_controles_rep, text="⚙️ Configuración", font=("Segoe UI", 9, "bold"), bg="#475569", fg="white", bd=0, cursor="hand2", command=self.mostrar_editar_configuracion)
        btn_config.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_config.bind("<Enter>", lambda e: btn_config.config(bg="#334155"))
        btn_config.bind("<Leave>", lambda e: btn_config.config(bg="#475569"))

        btn_logout = tk.Button(frame_controles_rep, text="🚪 Cerrar Sesión", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.cerrar_sesion)
        btn_logout.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="#DC2626"))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="#EF4444"))

        # Tabla del reporte
        columnas_rep = ("id", "codigo", "nombre", "cantidad", "precio", "total", "fecha", "metodo_pago")
        self.tabla_reporte = ttk.Treeview(frame_reporte_grid, columns=columnas_rep, show="headings")
        
        headers_rep = [("ID Venta", 60), ("Referencia", 100), ("Producto", 220), ("Cant.", 60), ("Precio Unit.", 95), ("Total Venta", 100), ("Fecha / Hora", 150), ("Método", 95)]
        for col, (texto, ancho) in zip(columnas_rep, headers_rep):
            self.tabla_reporte.heading(col, text=texto)
            self.tabla_reporte.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
            
        self.tabla_reporte.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    # ==========================================
    # CONFIGURAR ATAJOS DE TECLADO
    # ==========================================
    def configurar_atajos(self):
        for entry in self.inputs.values():
            entry.bind("<Return>", lambda e: self.guardar_producto())

    # ==========================================
    # RESPALDAR BASE DE DATOS
    # ==========================================
    def respaldar_base_datos(self):
        nombre_negocio = "negocio"
        if self.config and self.config.get("nombre_empresa"):
            nombre_negocio = "".join([c for c in self.config["nombre_empresa"] if c.isalnum() or c in (" ", "_")]).strip().replace(" ", "_").lower()
        
        ruta_destino = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Base de Datos", "*.db")],
            title="Guardar Respaldo de Base de Datos",
            initialfile=f"respaldo_inventario_{nombre_negocio}.db"
        )
        if not ruta_destino:
            return
        try:
            shutil.copy2(database.DB_NAME, ruta_destino)
            messagebox.showinfo("Respaldo Exitoso", f"Base de datos respaldada correctamente en:\n{ruta_destino}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo respaldar la base de datos:\n{str(e)}")

    # ==========================================
    # REINICIAR SISTEMA (VACIAR)
    # ==========================================
    def reiniciar_sistema(self):
        confirmar = messagebox.askyesno(
            "⚠️ ATENCIÓN: Reiniciar Sistema",
            "¿Estás absolutamente seguro de que deseas VACIAR TODO el sistema?\n\n"
            "Esto eliminará permanentemente TODOS los productos, sus fotos locales y el historial de ventas.\n"
            "Usa esta opción solo para limpiar los datos de prueba antes de entregar al cliente.\n\n"
            "¿Deseas continuar?"
        )
        if not confirmar:
            return
            
        try:
            borrar_config = messagebox.askyesno(
                "Borrar Configuración de Empresa",
                "¿También deseas eliminar la configuración de la empresa (nombre del negocio, dirección, ticket, etc.)?\n\n"
                "Elige SÍ si vas a entregar el sistema a un nuevo cliente para que ingrese sus datos al iniciar."
            )
            
            database.reiniciar_base_datos()
            
            if borrar_config:
                database.eliminar_configuracion()
                database.eliminar_usuarios()
                self.config = None
                self.root.title("Control de Inventario y Ventas")
                self.cargar_datos()
                self.pos_actualizar_alertas_pestaña()
            
            # Intentar limpiar la carpeta local de fotos
            img_dir = self.obtener_ruta_imagenes()
            if os.path.exists(img_dir):
                shutil.rmtree(img_dir)
                os.makedirs(img_dir, exist_ok=True)
                
            messagebox.showinfo("Sistema Reiniciado", "El sistema ha sido vaciado con éxito.")
            
            if borrar_config:
                self.root.withdraw()
                self.mostrar_configuracion_inicial()
            else:
                self.cargar_datos()
                self.pos_actualizar_alertas_pestaña()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reiniciar el sistema: {str(e)}")

    # ==========================================
    # ANULAR VENTA SELECCIONADA
    # ==========================================
    def anular_venta_seleccionada(self):
        seleccion = self.tabla_reporte.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una transacción de la tabla para anularla.")
            return
            
        valores = self.tabla_reporte.item(seleccion[0])["values"]
        venta_id = int(valores[0])
        producto_nombre = valores[2]
        
        confirmar = messagebox.askyesno(
            "Confirmar Anulación",
            f"¿Estás seguro de que deseas anular la venta ID {venta_id} ({producto_nombre})?\n\n"
            "Esto eliminará permanentemente la venta y devolverá el stock de unidades al inventario."
        )
        if not confirmar:
            return
            
        exito, msg = database.anular_venta(venta_id)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.reporte_actualizar_datos()
            self.pos_actualizar_alertas_pestaña()
        else:
            messagebox.showerror("Error", msg)

    # ==========================================
    # CORTE DE CAJA DIARIO (POPUP)
    # ==========================================
    def generar_corte_caja(self):
        from datetime import datetime
        fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
        resumen = database.obtener_resumen_ventas("Hoy")
        
        texto_corte = (
            "=== CORTE DE CAJA (HOY) ===\n"
            f"Fecha: {fecha_hoy}\n\n"
            f"Total Recaudado: ${resumen['total']:,.0f}\n"
            f"Transacciones: {resumen['cant']}\n\n"
            "Desglose de Pago:\n"
            f"- Efectivo: ${resumen['efe']:,.0f}\n"
            f"- Transferencia: ${resumen['tra']:,.0f}\n\n"
            f"Ganancia Neta (Utilidad): ${resumen['utilidad']:,.0f}\n"
            "==========================="
        )
        
        # Crear ventana emergente
        win = tk.Toplevel(self.root)
        win.title("Corte de Caja Diario")
        win.geometry("340x380")
        win.configure(bg="#F8FAFC")
        win.grab_set()
        
        tk.Label(win, text="Cierre de Caja del Día", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=15)
        
        txt = tk.Text(win, font=("Consolas", 10), height=10, width=38, bd=1, relief=tk.SOLID, bg="#FFFFFF", fg="#334155")
        txt.pack(pady=5, padx=15)
        txt.insert(tk.END, texto_corte)
        txt.config(state=tk.DISABLED)
        
        def copiar():
            self.root.clipboard_clear()
            self.root.clipboard_append(texto_corte)
            messagebox.showinfo("Copiado", "¡Corte de caja copiado al portapapeles!")
            win.destroy()
            
        btn_copiar = tk.Button(win, text="Copiar y Cerrar", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=copiar)
        btn_copiar.pack(fill=tk.X, padx=15, pady=15, ipady=6)

    # ==========================================
    # EXPORTAR CSV
    # ==========================================
    def exportar_reporte_csv(self):
        filtro = self.combo_filtro_fecha.get()
        ventas = database.obtener_ventas_reporte(filtro)
        if not ventas:
            messagebox.showinfo("Exportar", "No hay registros de ventas para exportar con el filtro actual.")
            return
            
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            title="Guardar Reporte de Ventas",
            initialfile=f"Reporte_Ventas_{filtro.replace(' ', '_')}.csv"
        )
        if not ruta:
            return
            
        try:
            with open(ruta, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["ID Venta", "Referencia", "Producto", "Cantidad", "Precio Unitario", "Total Venta", "Fecha", "Método de Pago"])
                for v in ventas:
                    writer.writerow([v[0], v[1] or "---", v[2], v[3], f"{v[4]:.2f}", f"{v[5]:.2f}", v[6], v[7]])
            messagebox.showinfo("Exportación Exitosa", f"El archivo ha sido guardado exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{str(e)}")

    # ==========================================
    # CONTROLADOR DE EVENTOS DE PESTAÑA
    # ==========================================
    def on_tab_changed(self, event):
        pestaña_activa = self.notebook.index(self.notebook.select())
        if pestaña_activa == 0:
            self.cargar_datos(self.entry_buscar.get())
        elif pestaña_activa == 1:
            self.pos_actualizar_lista_productos(self.entry_busca_pos.get())
            self.pos_actualizar_tabla_carrito()
        elif pestaña_activa == 2:
            self.reporte_actualizar_datos()

    # ==========================================
    # LÓGICA DE INVENTARIO
    # ==========================================
    def cargar_datos(self, filtro=""):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        productos = database.obtener_productos(filtro)
        for p in productos:
            costo_f = f"${p[4]:,.0f}"
            venta_f = f"${p[5]:,.0f}"
            valores = (p[0], p[1] or "---", p[2], costo_f, venta_f, p[6], p[7])
            tag = "alerta" if p[6] <= p[7] else ""
            self.tabla.insert("", tk.END, values=valores, tags=(tag,))
        self.pos_actualizar_alertas_pestaña()
        self.lbl_inv_foto_preview.config(image="", text="Sin foto")
        self.lbl_inv_foto_preview.image = None

    def guardar_producto(self):
        codigo = self.inputs["codigo"].get().strip()
        nombre = self.inputs["nombre"].get().strip()
        
        if not codigo:
            messagebox.showwarning("Falta información", "La Referencia del producto es obligatoria.")
            return
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre del producto es obligatorio.")
            return

        try:
            costo = float(self.inputs["costo"].get() or 0)
            venta = float(self.inputs["venta"].get() or 0)
            stock = int(self.inputs["stock"].get() or 0)
            min_stock = int(self.inputs["min_stock"].get() or 3)
        except ValueError:
            messagebox.showerror("Error de formato", "Los precios y el stock deben ser números válidos.")
            return

        # Copiar imagen a directorio local antes de guardar en DB
        imagen_destino = ""
        if self.imagen_ruta_form and os.path.exists(self.imagen_ruta_form):
            try:
                extension = os.path.splitext(self.imagen_ruta_form)[1]
                nombre_seguro = "".join([c for c in codigo if c.isalnum()])
                nombre_archivo = f"{nombre_seguro}{extension}"
                
                img_dir = self.obtener_ruta_imagenes()
                imagen_destino = os.path.join(img_dir, nombre_archivo)
                
                if os.path.abspath(self.imagen_ruta_form) != os.path.abspath(imagen_destino):
                    shutil.copy2(self.imagen_ruta_form, imagen_destino)
            except Exception:
                pass

        exito = database.insertar_producto(codigo, nombre, "", costo, venta, stock, min_stock, imagen_destino)
        if exito:
            self.cargar_datos(self.entry_buscar.get())
            for entry in self.inputs.values(): entry.delete(0, tk.END)
            self.inputs["min_stock"].insert(0, "3")
            self.imagen_ruta_form = ""
            self.lbl_img_path.config(text="Sin foto", fg="#94A3B8")
            self.lbl_img_preview.config(image="", text="Sin vista previa")
            self.lbl_img_preview.image = None
            self.inputs["codigo"].focus()
        else:
            messagebox.showerror("Error", "La Referencia ya está registrada.")
        self.pos_actualizar_alertas_pestaña()

    def ajustar_stock(self, cantidad):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla primero.")
            return
        
        producto_id = self.tabla.item(seleccion[0])["values"][0]
        database.modificar_stock(producto_id, cantidad)
        self.cargar_datos(self.entry_buscar.get())
        self.pos_actualizar_alertas_pestaña()

    # ==========================================
    # LÓGICA DE PUNTO DE VENTA (POS)
    # ==========================================
    def pos_actualizar_lista_productos(self, filtro=""):
        for item in self.tabla_pos_prod.get_children():
            self.tabla_pos_prod.delete(item)
        productos = database.obtener_productos(filtro)
        for p in productos:
            precio_f = f"${p[5]:,.0f}"
            self.tabla_pos_prod.insert("", tk.END, values=(p[0], p[1] or "---", p[2], precio_f, p[6]))

    def pos_on_producto_select(self, event):
        seleccion = self.tabla_pos_prod.selection()
        if not seleccion:
            self.lbl_pos_foto_preview.config(image="", text="Sin foto")
            self.lbl_pos_foto_preview.image = None
            return
        item = self.tabla_pos_prod.item(seleccion[0])["values"]
        p_id = int(item[0])
        
        # Consultar la DB para obtener los precios exactos (costo, venta estándar e imagen)
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT precio_costo, precio_venta, imagen_ruta FROM productos WHERE id = ?", (p_id,))
            res = cursor.fetchone()
            if res:
                self.selected_cost_price = res[0]
                self.selected_sell_price = res[1]
                
                # Cargar el precio de venta sugerido por defecto en el input
                self.entry_precio_pos.delete(0, tk.END)
                self.entry_precio_pos.insert(0, f"{res[1]:.0f}")
                
                # Cargar imagen de vista previa
                if res[2]:
                    self.actualizar_vista_previa_label(self.lbl_pos_foto_preview, res[2], (230, 170))
                else:
                    self.lbl_pos_foto_preview.config(image="", text="Sin foto")
                    self.lbl_pos_foto_preview.image = None

    def pos_agregar_al_carrito(self):
        seleccion = self.tabla_pos_prod.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la lista primero.")
            return
        
        # Validar cantidad
        try:
            cantidad = int(self.entry_cant_pos.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.")
            return

        # Validar precio unitario de venta
        try:
            precio_venta = float(self.entry_precio_pos.get())
            if precio_venta <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El precio de venta debe ser un número válido mayor a 0.")
            return

        # Validación Inteligente de Margen de Ganancia (Prevención de Pérdidas)
        if precio_venta < self.selected_cost_price:
            confirmar = messagebox.askyesno(
                "⚠️ Advertencia de Pérdidas", 
                f"El precio ingresado (${precio_venta:,.0f}) es menor al precio de costo (${self.selected_cost_price:,.0f}).\n"
                "Esta transacción generará pérdidas directas.\n\n¿Estás seguro de que deseas continuar?"
            )
            if not confirmar:
                return

        item_seleccionado = self.tabla_pos_prod.item(seleccion[0])["values"]
        p_id = int(item_seleccionado[0])
        p_codigo = item_seleccionado[1]
        p_nombre = item_seleccionado[2]
        p_stock = int(item_seleccionado[4])

        # Verificar si ya está en el carrito para sumar la cantidad
        carrito_item = next((item for item in self.carrito if item["id"] == p_id), None)
        nueva_cantidad = cantidad
        if carrito_item:
            nueva_cantidad += carrito_item["cantidad"]

        # Validar stock disponible
        if nueva_cantidad > p_stock:
            messagebox.showwarning("Sin stock suficiente", f"No puedes agregar esa cantidad. Stock disponible: {p_stock}")
            return

        if carrito_item:
            carrito_item["cantidad"] = nueva_cantidad
            # Actualizar también con el precio de venta ingresado
            carrito_item["precio"] = precio_venta
        else:
            self.carrito.append({
                "id": p_id,
                "codigo": p_codigo,
                "nombre": p_nombre,
                "precio": precio_venta, # Usar el precio dinámico especificado
                "cantidad": cantidad
            })

        self.entry_cant_pos.delete(0, tk.END)
        self.entry_cant_pos.insert(0, "1")
        self.pos_actualizar_tabla_carrito()

    def pos_actualizar_tabla_carrito(self):
        for item in self.tabla_carro.get_children():
            self.tabla_carro.delete(item)
        
        total_acumulado = 0.0
        for item in self.carrito:
            total_item = item["precio"] * item["cantidad"]
            total_acumulado += total_item
            
            valores = (
                item["id"], 
                item["codigo"], 
                item["nombre"], 
                f"${item['precio']:,.0f}", 
                item["cantidad"], 
                f"${total_item:,.0f}"
            )
            self.tabla_carro.insert("", tk.END, values=valores)
            
        self.lbl_total_pos.config(text=f"TOTAL: ${total_acumulado:,.0f}")

    def pos_quitar_del_carrito(self):
        seleccion = self.tabla_carro.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un artículo del carrito para quitarlo.")
            return
        
        item_id = int(self.tabla_carro.item(seleccion[0])["values"][0])
        self.carrito = [item for item in self.carrito if item["id"] != item_id]
        self.pos_actualizar_tabla_carrito()

    def pos_procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito para realizar una venta.")
            return

        metodo_pago = self.combo_pago.get()
        carrito_copia = list(self.carrito)

        # Registrar cada artículo
        errores = []
        for item in self.carrito:
            exito, msg = database.registrar_venta(item["id"], item["cantidad"], item["precio"], metodo_pago)
            if not exito:
                errores.append(f"{item['nombre']}: {msg}")

        if errores:
            messagebox.showerror("Error al procesar ventas", "\n".join(errores))
        else:
            messagebox.showinfo("Venta exitosa", "¡La venta ha sido registrada con éxito!")
            self.carrito = []
            self.pos_actualizar_tabla_carrito()
            self.pos_actualizar_lista_productos(self.entry_busca_pos.get())
            self.pos_actualizar_alertas_pestaña()
            self.lbl_pos_foto_preview.config(image="", text="Sin foto")
            self.lbl_pos_foto_preview.image = None
            
            # Generar ticket térmico
            self.pos_generar_ticket(carrito_copia, metodo_pago)

    def pos_generar_ticket(self, carrito_copia, metodo_pago):
        try:
            import datetime
            fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Obtener el directorio de tickets al lado del ejecutable/script
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            dir_tickets = os.path.join(base_dir, "tickets")
            os.makedirs(dir_tickets, exist_ok=True)
            
            filename_txt = f"ticket_{timestamp_file}.txt"
            path_ticket_txt = os.path.join(dir_tickets, filename_txt)
            
            # Calcular total
            total_acumulado = sum(item["precio"] * item["cantidad"] for item in carrito_copia)
            
            # Formato térmico estandarizado
            nombre_empresa = self.config["nombre_empresa"].upper()
            if len(nombre_empresa) > 40:
                nombre_empresa = nombre_empresa[:37] + "..."
                
            lineas = [
                "==========================================",
                f"{nombre_empresa.center(42)}",
                "=========================================="
            ]
            
            if self.config.get("propietario"):
                lineas.append(f" Propietario: {self.config['propietario']}")
            if self.config.get("telefono"):
                lineas.append(f" Tel: {self.config['telefono']}")
            if self.config.get("direccion"):
                lineas.append(f" Dir: {self.config['direccion']}")
                
            lineas.extend([
                f" Fecha: {fecha_str}",
                f" Metodo Pago: {metodo_pago}",
                "------------------------------------------",
                f"{'Cant':<5}{'Producto':<22}{'Precio':<8}{'Total':<7}",
                "------------------------------------------"
            ])
            
            for item in carrito_copia:
                total_item = item["precio"] * item["cantidad"]
                nombre_prod = item["nombre"]
                if len(nombre_prod) > 20:
                    nombre_prod = nombre_prod[:17] + "..."
                precio_str = f"${item['precio']:,.0f}"
                total_str = f"${total_item:,.0f}"
                lineas.append(f"{item['cantidad']:<5}{nombre_prod:<22}{precio_str:<9}{total_str}")
                
            lineas.extend([
                "------------------------------------------",
                f"TOTAL A PAGAR:               ${total_acumulado:,.0f}",
                "=========================================="
            ])
            
            # Dynamic wrapped footer message
            import textwrap
            mensaje_ticket = self.config.get("mensaje_ticket", "¡Gracias por su compra!")
            for line in textwrap.wrap(mensaje_ticket, 40):
                lineas.append(line.center(42))
                
            lineas.append("==========================================")
            
            texto_ticket = "\n".join(lineas)
            
            # Guardar .txt siempre
            with open(path_ticket_txt, "w", encoding="utf-8") as f:
                f.write(texto_ticket)
            
            # --- Mostrar diálogo de acciones post-venta ---
            self._mostrar_dialogo_ticket(texto_ticket, lineas, path_ticket_txt, timestamp_file, dir_tickets, carrito_copia, total_acumulado, metodo_pago, fecha_str)
            
        except Exception as e:
            messagebox.showerror("Error al generar ticket", f"No se pudo crear el ticket: {str(e)}")

    def _mostrar_dialogo_ticket(self, texto_ticket, lineas, path_txt, timestamp_file, dir_tickets, carrito_copia, total_acumulado, metodo_pago, fecha_str):
        win = tk.Toplevel(self.root)
        win.title("Comprobante de Venta")
        win.geometry("500x680")
        win.configure(bg="#F8FAFC")
        win.grab_set()
        win.resizable(False, False)
        
        # ── BOTONES (se empaquetan PRIMERO al fondo para que siempre sean visibles) ──
        frame_btns = tk.Frame(win, bg="#F8FAFC")
        frame_btns.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 15))
        
        def imprimir_ticket():
            impresora_configurada = self.config.get("impresora_ticket") if self.config else ""
            if impresora_configurada:
                exito, msg = self.enviar_impresion_directa(impresora_configurada, texto_ticket)
                if exito:
                    messagebox.showinfo("Imprimiendo", "El ticket se ha enviado directamente a la impresora térmica.", parent=win)
                else:
                    messagebox.showerror("Error de impresión", f"No se pudo imprimir directamente:\n{msg}\n\nSe intentará abrir el archivo para impresión manual.", parent=win)
                    try:
                        os.startfile(path_txt, "print")
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo imprimir manualmente: {str(e)}", parent=win)
            else:
                try:
                    os.startfile(path_txt, "print")
                    messagebox.showinfo("Imprimiendo", "El ticket se ha enviado a la impresora.", parent=win)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo imprimir: {str(e)}", parent=win)

        
        def guardar_pdf():
            try:
                ruta_pdf = filedialog.asksaveasfilename(
                    parent=win,
                    defaultextension=".pdf",
                    filetypes=[("Archivo PDF", "*.pdf")],
                    title="Guardar Factura PDF",
                    initialfile=f"Factura_{timestamp_file}.pdf",
                    initialdir=dir_tickets
                )
                if not ruta_pdf:
                    return
                
                self._generar_pdf_ticket(lineas, ruta_pdf)
                messagebox.showinfo("PDF Guardado", f"La factura PDF se guardó en:\n{ruta_pdf}", parent=win)
                os.startfile(ruta_pdf)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}", parent=win)
        
        # Fila de botones principales
        frame_btns_row = tk.Frame(frame_btns, bg="#F8FAFC")
        frame_btns_row.pack(fill=tk.X, pady=(0, 6))
        
        btn_imprimir = tk.Button(frame_btns_row, text="🖨️  Imprimir Ticket", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=imprimir_ticket)
        btn_imprimir.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(0, 4))
        btn_imprimir.bind("<Enter>", lambda e: btn_imprimir.config(bg="#4338CA"))
        btn_imprimir.bind("<Leave>", lambda e: btn_imprimir.config(bg="#4F46E5"))
        
        btn_pdf = tk.Button(frame_btns_row, text="📄  Guardar PDF", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=guardar_pdf)
        btn_pdf.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(4, 0))
        btn_pdf.bind("<Enter>", lambda e: btn_pdf.config(bg="#059669"))
        btn_pdf.bind("<Leave>", lambda e: btn_pdf.config(bg="#10B981"))
        
        btn_cerrar = tk.Button(frame_btns, text="Cerrar", font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#475569", bd=0, cursor="hand2", command=win.destroy)
        btn_cerrar.pack(fill=tk.X, ipady=7)
        btn_cerrar.bind("<Enter>", lambda e: btn_cerrar.config(bg="#CBD5E1"))
        btn_cerrar.bind("<Leave>", lambda e: btn_cerrar.config(bg="#E2E8F0"))
        
        # ── SEPARADOR VISUAL ──
        tk.Frame(win, bg="#E2E8F0", height=1).pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 0))
        
        # ── BANNER SUPERIOR ──
        frame_banner = tk.Frame(win, bg="#F8FAFC")
        frame_banner.pack(fill=tk.X)
        
        tk.Label(frame_banner, text="✅", font=("Segoe UI", 24), bg="#F8FAFC").pack(pady=(15, 0))
        tk.Label(frame_banner, text="¡Venta Registrada con Éxito!", font=("Segoe UI", 14, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=(2, 2))
        
        # Total destacado
        tk.Label(frame_banner, text=f"${total_acumulado:,.0f}", font=("Segoe UI", 28, "bold"), bg="#F8FAFC", fg="#10B981").pack(pady=(0, 5))
        
        # ── TARJETAS RESUMEN ──
        frame_cards = tk.Frame(win, bg="#F8FAFC")
        frame_cards.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        total_items = sum(item["cantidad"] for item in carrito_copia)
        total_productos = len(carrito_copia)
        
        card_data = [
            ("Método de Pago", metodo_pago, "#4F46E5"),
            ("Artículos", f"{total_items} uds ({total_productos} prod.)", "#D97706"),
            ("Fecha", fecha_str.split(" ")[0], "#0891B2"),
        ]
        
        for titulo, valor, color in card_data:
            card = tk.Frame(frame_cards, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3, ipady=5)
            tk.Label(card, text=titulo, font=("Segoe UI", 7, "bold"), bg="#FFFFFF", fg="#94A3B8").pack(anchor=tk.W, padx=10, pady=(4, 0))
            tk.Label(card, text=valor, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg=color).pack(anchor=tk.W, padx=10, pady=(0, 3))
        
        # ── DETALLE DEL COMPROBANTE ──
        frame_ticket_outer = tk.Frame(win, bg="#F8FAFC")
        frame_ticket_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))
        
        tk.Label(frame_ticket_outer, text="DETALLE DEL COMPROBANTE", font=("Segoe UI", 8, "bold"), bg="#F8FAFC", fg="#94A3B8").pack(anchor=tk.W, pady=(0, 3))
        
        frame_ticket = tk.Frame(frame_ticket_outer, bg="#FFFFF0", highlightbackground="#E2E8F0", highlightthickness=1)
        frame_ticket.pack(fill=tk.BOTH, expand=True)
        
        txt = tk.Text(frame_ticket, font=("Consolas", 9), bg="#FFFFF0", fg="#334155", bd=0, wrap=tk.NONE, padx=12, pady=8, selectbackground="#E0E7FF")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, texto_ticket)
        txt.config(state=tk.DISABLED)

    def _generar_pdf_ticket(self, lineas, ruta_pdf):
        """Genera un PDF básico del ticket sin dependencias externas usando formato PDF crudo."""
        font_size = 10
        line_height = 14
        margin_x = 40
        margin_top = 40
        page_width = 300
        page_height = margin_top + (len(lineas) + 2) * line_height + 40
        
        # Construir el contenido de texto PDF (stream)
        text_commands = [f"BT", f"/F1 {font_size} Tf"]
        y_pos = page_height - margin_top
        
        for linea in lineas:
            # Escapar caracteres especiales de PDF
            linea_safe = linea.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            text_commands.append(f"1 0 0 1 {margin_x} {y_pos} Tm")
            text_commands.append(f"({linea_safe}) Tj")
            y_pos -= line_height
        
        text_commands.append("ET")
        stream_content = "\n".join(text_commands)
        stream_length = len(stream_content)
        
        # Construir los objetos PDF
        objects = []
        offsets = []
        
        pdf_header = "%PDF-1.4\n"
        current_pos = len(pdf_header)
        
        # Objeto 1: Catálogo
        offsets.append(current_pos)
        obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        objects.append(obj1)
        current_pos += len(obj1)
        
        # Objeto 2: Páginas
        offsets.append(current_pos)
        obj2 = "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        objects.append(obj2)
        current_pos += len(obj2)
        
        # Objeto 3: Página
        offsets.append(current_pos)
        obj3 = f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        objects.append(obj3)
        current_pos += len(obj3)
        
        # Objeto 4: Contenido (stream de texto)
        offsets.append(current_pos)
        obj4 = f"4 0 obj\n<< /Length {stream_length} >>\nstream\n{stream_content}\nendstream\nendobj\n"
        objects.append(obj4)
        current_pos += len(obj4)
        
        # Objeto 5: Fuente
        offsets.append(current_pos)
        obj5 = "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n"
        objects.append(obj5)
        current_pos += len(obj5)
        
        # Tabla de referencias cruzadas (xref)
        xref_pos = current_pos
        xref = "xref\n"
        xref += f"0 {len(objects) + 1}\n"
        xref += "0000000000 65535 f \n"
        for offset in offsets:
            xref += f"{offset:010d} 00000 n \n"
        
        # Trailer
        trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
        
        # Escribir el PDF completo
        with open(ruta_pdf, "w", encoding="latin-1") as f:
            f.write(pdf_header)
            for obj in objects:
                f.write(obj)
            f.write(xref)
            f.write(trailer)

    # ==========================================
    # CONTROLADORES DE EVENTO DE TECLADO (BUSCADOR INTELIGENTE)
    # ==========================================
    def pos_on_busca_enter(self, event):
        children = self.tabla_pos_prod.get_children()
        if children:
            first_item = children[0]
            self.tabla_pos_prod.selection_set(first_item)
            self.tabla_pos_prod.focus(first_item)
            self.pos_on_producto_select(None)
            
            # Foco a cantidad y autoselección
            self.entry_cant_pos.focus_set()
            self.entry_cant_pos.select_range(0, tk.END)
            self.entry_cant_pos.icursor(tk.END)

    def pos_on_cant_enter(self, event):
        # Foco a precio de venta y autoselección
        self.entry_precio_pos.focus_set()
        self.entry_precio_pos.select_range(0, tk.END)
        self.entry_precio_pos.icursor(tk.END)

    def pos_on_precio_enter(self, event):
        # Agregar e ir de nuevo al buscador
        self.pos_agregar_al_carrito()
        self.entry_busca_pos.delete(0, tk.END)
        self.pos_actualizar_lista_productos("")
        self.entry_busca_pos.focus_set()

    # ==========================================
    # LÓGICA DE HISTORIAL / REPORTES
    # ==========================================
    def reporte_actualizar_datos(self):
        filtro = self.combo_filtro_fecha.get()
        resumen = database.obtener_resumen_ventas(filtro)
        
        # Tarjeta 1: Ventas Totales del Rango
        self.lbl_card_hoy_valor.config(text=f"${resumen['total']:,.0f}")
        self.lbl_card_hoy_sub.config(text=f"{resumen['cant']} transacciones")
        
        # Tarjeta 2: Detalle Métodos
        self.lbl_card_tot_sub.config(
            text=f"Efe: ${resumen['efe']:,.0f}  |  Transf: ${resumen['tra']:,.0f}"
        )
        
        # Tarjeta 3: Utilidad Real (Ganancia Neta)
        self.lbl_card_ut_valor.config(text=f"${resumen['utilidad']:,.0f}")
        if resumen['utilidad'] >= 0:
            self.lbl_card_ut_valor.config(fg="#10B981") # Verde
        else:
            self.lbl_card_ut_valor.config(fg="#EF4444") # Rojo si hay pérdida histórica

        # Tarjeta 4: Top 3 Más Vendidos
        top_prods = database.obtener_top_productos(filtro)
        if top_prods:
            top_texto = "\n".join([f"{i+1}. {p[0]} ({p[1]} uds)" for i, p in enumerate(top_prods)])
            self.lbl_card_top_valor.config(text=top_texto)
        else:
            self.lbl_card_top_valor.config(text="Sin ventas en el período")

        # Cargar tabla
        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)
            
        ventas = database.obtener_ventas_reporte(filtro)
        for v in ventas:
            precio_f = f"${v[4]:,.0f}"
            total_f = f"${v[5]:,.0f}"
            valores = (v[0], v[1] or "---", v[2], v[3], precio_f, total_f, v[6], v[7])
            self.tabla_reporte.insert("", tk.END, values=valores)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()
