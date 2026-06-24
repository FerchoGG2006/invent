"""
Sistema POS Universal - Punto de Entrada Principal
Orquesta los módulos de UI y delega a utils/ y modules/ para la lógica.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import os
import sys
import shutil

from utils.printer import obtener_impresoras_sistema, enviar_impresion_directa
from utils.network import verificar_conexion_internet, verificar_conexion_async
from utils.fiscal import obtener_label_id_fiscal
from utils import updater
from modules import config as config_module
from modules.inventario import InventarioTab
from modules.pos import PosTab
from modules.reportes import ReportesTab
from modules.proveedores import ProveedoresTab
from modules.caja import CajaTab
from modules.creditos import CreditosTab


class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Ocultar inmediatamente para evitar parpadeos
        self.root.geometry("1200x750")
        self.root.configure(fg_color=("#F8FAFC", "#0F172A"))  # Slate 50

        # Verificar y migrar datos de versiones anteriores antes de inicializar la base de datos
        self.verificar_y_migrar_datos()

        database.init_db()
        self.config = database.obtener_configuracion()
        
        import customtkinter as ctk
        if self.config and self.config.get("tema"):
            ctk.set_appearance_mode(self.config["tema"])
        else:
            ctk.set_appearance_mode("System")

        self.carrito = []  # Lista de items: {"id", "codigo", "nombre", "precio", "cantidad"}
        self.selected_cost_price = 0.0
        self.selected_sell_price = 0.0
        self.imagen_ruta_form = ""  # Ruta de la foto seleccionada en el formulario
        self.current_user = None

        self.crear_interfaz()
        self.cargar_datos()
        self.pos_actualizar_alertas_pestaña()

        # Handle the splash / configuration screen
        cant_usuarios = database.obtener_cantidad_usuarios()
        if not self.config or cant_usuarios == 0:
            self.root.after(100, self.mostrar_configuracion_inicial)
        else:
            self.root.title(f"Control de Inventario y Ventas - {self.config['nombre_empresa']}")
            self.mostrar_splash(self.config)

        # Buscar actualizaciones y mensajes globales en segundo plano
        updater.buscar_actualizaciones(self)

        # Iniciar sincronización en la nube en segundo plano
        from utils import sync
        sync.iniciar_hilo_sincronizacion(self)

    # ==========================================
    # DELEGACIÓN A MÓDULO DE CONFIGURACIÓN
    # ==========================================
    def mostrar_configuracion_inicial(self):
        config_module.mostrar_configuracion_inicial(self)

    def mostrar_registro_administrador(self):
        config_module.mostrar_registro_administrador(self)

    def mostrar_login(self):
        config_module.mostrar_login(self)

    def cerrar_sesion(self):
        config_module.cerrar_sesion(self)

    def mostrar_editar_configuracion(self):
        config_module.mostrar_editar_configuracion(self)

    def mostrar_splash(self, config):
        config_module.mostrar_splash(self, config)

    def mostrar_gestion_usuarios(self):
        from modules import usuarios as usuarios_module
        usuarios_module.mostrar_gestion_usuarios(self)

    # ==========================================
    # UTILIDADES DELEGADAS
    # ==========================================
    def obtener_ruta_imagenes(self):
        if getattr(sys, 'frozen', False):
            # En ejecutable compilado, guardamos en AppData para evitar problemas de permisos
            appdata = os.environ.get('APPDATA')
            if appdata:
                base_dir = os.path.join(appdata, "InventarioPOS")
            else:
                base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "imagenes_productos")
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def verificar_y_migrar_datos(self):
        """
        Detecta si es la primera vez que se ejecuta la versión instalada y ofrece migrar
        la base de datos y las imágenes de la versión portable antigua automáticamente
        o de forma interactiva.
        """
        if not getattr(sys, 'frozen', False):
            return

        db_dest_path = database.DB_NAME
        # Si la base de datos ya existe en AppData, no es necesario hacer ninguna migración
        if os.path.exists(db_dest_path):
            return

        # 1. Intentar migración silenciosa si los archivos están al lado del ejecutable o en el directorio actual
        exe_dir = os.path.dirname(sys.executable)
        cwd_dir = os.getcwd()
        
        posibles_rutas_db = [
            os.path.join(exe_dir, "inventario_barberia.db"),
            os.path.join(cwd_dir, "inventario_barberia.db")
        ]
        
        for ruta_origen in posibles_rutas_db:
            if os.path.exists(ruta_origen) and os.path.abspath(ruta_origen) != os.path.abspath(db_dest_path):
                try:
                    os.makedirs(os.path.dirname(db_dest_path), exist_ok=True)
                    shutil.copy2(ruta_origen, db_dest_path)
                    
                    # Copiar imágenes si existen en el origen
                    dir_imagenes_origen = os.path.join(os.path.dirname(ruta_origen), "imagenes_productos")
                    if os.path.exists(dir_imagenes_origen):
                        dir_imagenes_dest = self.obtener_ruta_imagenes()
                        for item in os.listdir(dir_imagenes_origen):
                            src_item = os.path.join(dir_imagenes_origen, item)
                            dst_item = os.path.join(dir_imagenes_dest, item)
                            if os.path.isdir(src_item):
                                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src_item, dst_item)
                    return  # Migración silenciosa completada con éxito
                except Exception as e:
                    print(f"Error en migración silenciosa: {e}")

        # 2. Si no se encontró de forma silenciosa, preguntar al usuario de forma interactiva
        resp = messagebox.askyesno(
            "Importar Datos de Versión Anterior",
            "Detectamos que esta es una instalación nueva del sistema.\n\n"
            "¿Deseas importar los productos y ventas de tu versión anterior?",
            parent=self.root
        )
        if not resp:
            return

        # Solicitar selección de base de datos
        ruta_seleccionada = filedialog.askopenfilename(
            title="Selecciona el archivo inventario_barberia.db de tu versión anterior",
            filetypes=[("Base de Datos SQLite", "inventario_barberia.db"), ("Todos los archivos de Base de Datos", "*.db")],
            parent=self.root
        )
        
        if ruta_seleccionada:
            try:
                os.makedirs(os.path.dirname(db_dest_path), exist_ok=True)
                shutil.copy2(ruta_seleccionada, db_dest_path)
                
                # Copiar carpeta de imágenes si existe al lado de la base de datos seleccionada
                dir_imagenes_origen = os.path.join(os.path.dirname(ruta_seleccionada), "imagenes_productos")
                if os.path.exists(dir_imagenes_origen):
                    dir_imagenes_dest = self.obtener_ruta_imagenes()
                    for item in os.listdir(dir_imagenes_origen):
                        src_item = os.path.join(dir_imagenes_origen, item)
                        dst_item = os.path.join(dir_imagenes_dest, item)
                        if os.path.isdir(src_item):
                            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src_item, dst_item)
                
                messagebox.showinfo(
                    "Importación Exitosa",
                    "¡Tus datos han sido importados con éxito!\nEl sistema se iniciará ahora con tu información anterior.",
                    parent=self.root
                )
            except Exception as e:
                messagebox.showerror(
                    "Error de Importación",
                    f"No se pudieron importar los datos:\n{str(e)}",
                    parent=self.root
                )

    def verificar_conexion_async(self):
        def on_result(conectado):
            self.root.after(0, lambda: self.actualizar_indicador_conexion(conectado))
        verificar_conexion_async(on_result)

    def actualizar_indicador_conexion(self, conectado):
        if hasattr(self, "lbl_conexion_pos"):
            if conectado:
                self.lbl_conexion_pos.configure(text="🟢 En línea", text_color="#10B981")
            else:
                self.lbl_conexion_pos.configure(text="🔴 Sin conexión", text_color="#EF4444")

    def actualizar_labels_facturacion(self):
        if hasattr(self, "lbl_cliente_identificacion"):
            pais = self.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.config else "Otro"
            lbl_id_text = obtener_label_id_fiscal(pais)
            self.lbl_cliente_identificacion.configure(text=lbl_id_text)

    # ==========================================
    # VISTA PREVIA DE IMAGEN (HELPER)
    # ==========================================
    def actualizar_vista_previa_label(self, label, ruta, tamano):
        try:
            if not ruta or not os.path.exists(ruta):
                label.config(image="", text="Sin imagen", compound="center")
                label.image = None
                return
            from PIL import Image, ImageTk
            img = Image.open(ruta)
            # Redimensionamiento proporcional manteniendo la relación de aspecto original
            img.thumbnail(tamano, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text="", compound="center")
            label.image = photo
        except Exception:
            label.config(image="", text="Error al cargar imagen", compound="center")
            label.image = None

    # ==========================================
    # INTERFAZ PRINCIPAL (FRAMEWORK DE PESTAÑAS)
    # ==========================================
    def crear_interfaz(self):
        # --- Estilos Globales de ttk ---
        style = ttk.Style()
        style.theme_use("clam")

        # Estilo del Treeview
        self.actualizar_estilos_treeview()

        # Contenedor principal de pestañas usando CustomTkinter
        import customtkinter as ctk
        self.notebook = ctk.CTkTabview(
            self.root, 
            command=self.on_tab_changed,
            segmented_button_selected_color="#4F46E5",
            segmented_button_unselected_color=("#E2E8F0", "#334155"),
            segmented_button_selected_hover_color="#4338CA",
            text_color="#1E293B"
        )
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear y registrar pestañas
        self.notebook.add(" 📦 Inventario ")
        self.notebook.add(" 🛒 Punto de Venta ")
        self.notebook.add(" 📓 Créditos ")
        self.notebook.add(" 📊 Historial de Ventas ")
        self.notebook.add(" 🚚 Proveedores ")
        self.notebook.add(" 💰 Caja y Turnos ")
        self.notebook.add(" 📈 Analíticas ")

        # Guardar referencias de los frames de cada pestaña
        self.tab_inventario = self.notebook.tab(" 📦 Inventario ")
        self.tab_pos = self.notebook.tab(" 🛒 Punto de Venta ")
        self.tab_creditos = self.notebook.tab(" 📓 Créditos ")
        self.tab_reportes = self.notebook.tab(" 📊 Historial de Ventas ")
        self.tab_proveedores = self.notebook.tab(" 🚚 Proveedores ")
        self.tab_caja = self.notebook.tab(" 💰 Caja y Turnos ")
        self.tab_analiticas = self.notebook.tab(" 📈 Analíticas ")

        # Inicializar controladores de cada pestaña
        self.inventario_controller = InventarioTab(self)
        self.pos_controller = PosTab(self)
        self.creditos_controller = CreditosTab(self)
        self.reportes_controller = ReportesTab(self)
        self.proveedores_controller = ProveedoresTab(self)
        self.caja_controller = CajaTab(self)
        
        # Configurar atajos de teclado globales
        self.configurar_atajos_teclado()
        
        # Verificar stock bajo al iniciar
        self.root.after(2000, self.verificar_stock_bajo_inicio)
        
    def actualizar_estilos_treeview(self):
        style = ttk.Style()
        import customtkinter as ctk
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            bg_color = "#1E293B"       # Slate 800
            fg_color = "#F8FAFC"       # Slate 50
            heading_bg = "#0F172A"     # Slate 900
            heading_fg = "#F8FAFC"     # Slate 50
            selected_bg = "#334155"    # Slate 700
            selected_fg = "#FFFFFF"
        else:
            bg_color = "#FFFFFF"
            fg_color = "#0F172A"       # Slate 900
            heading_bg = "#F1F5F9"     # Slate 100
            heading_fg = "#334155"     # Slate 700
            selected_bg = "#E0E7FF"    # Indigo 100
            selected_fg = "#312E81"    # Indigo 900

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=bg_color,
                        font=("Segoe UI", 9),
                        rowheight=30)
        
        style.configure("Treeview.Heading",
                        background=heading_bg,
                        foreground=heading_fg,
                        font=("Segoe UI", 9, "bold"))
        
        style.map("Treeview",
                  background=[('selected', selected_bg)],
                  foreground=[('selected', selected_fg)])

    def verificar_stock_bajo_inicio(self):
        productos_bajos = database.obtener_productos_stock_bajo()
        if productos_bajos:
            msg = f"¡Atención! Tienes {len(productos_bajos)} producto(s) con stock por debajo del mínimo permitido.\n\n"
            for p in productos_bajos[:5]: # Mostrar maximo 5
                msg += f"• {p[2]} (Stock: {p[3]} - Mín: {p[4]})\n"
            if len(productos_bajos) > 5:
                msg += f"... y {len(productos_bajos) - 5} más."
            
            messagebox.showwarning("Notificación de Stock Bajo", msg)

    # ==========================================
    # ATAJOS DE TECLADO GLOBALES
    # ==========================================
    def configurar_atajos_teclado(self):
        # F1 a F6 para cambiar pestañas
        def cambiar_tab(indice):
            tabs = [" 📦 Inventario ", " 🛒 Punto de Venta ", " 📊 Historial de Ventas ", " 🚚 Proveedores ", " 💰 Caja y Turnos ", " 📈 Analíticas "]
            if 0 <= indice < len(tabs):
                try:
                    self.notebook.set(tabs[indice])
                    self.on_tab_changed()
                except ValueError:
                    pass

        self.root.bind("<F1>", lambda e: cambiar_tab(0))
        self.root.bind("<F2>", lambda e: cambiar_tab(1))
        self.root.bind("<F3>", lambda e: cambiar_tab(2))
        self.root.bind("<F4>", lambda e: cambiar_tab(3))
        self.root.bind("<F5>", lambda e: cambiar_tab(4))
        self.root.bind("<F6>", lambda e: cambiar_tab(5))

    # ==========================================
    # DELEGACIÓN DE MÉTODOS PARA COMPATIBILIDAD (Temporal o Helper)
    # ==========================================
    def cargar_datos(self):
        # Initial load logic via controller
        if hasattr(self, 'inventario_controller'):
            self.inventario_controller.cargar_datos(self.inventario_controller.entry_buscar.get())

    def pos_actualizar_alertas_pestaña(self):
        # Deshabilitado el indicador de alertas en el nombre del Tab ya que CTkTabview no permite modificar texto dinámicamente de forma directa fácilmente
        pass

    def on_tab_changed(self):
        tab_activa = self.notebook.get().strip()
        if tab_activa == "📦 Inventario":
            self.inventario_controller.cargar_datos(self.inventario_controller.entry_buscar.get())
        elif tab_activa == "🛒 Punto de Venta":
            self.pos_controller.pos_actualizar_lista_productos(self.pos_controller.entry_busca_pos.get())
            self.pos_controller.pos_actualizar_tabla_carrito()
            self.verificar_conexion_async()
        elif tab_activa == "📊 Historial de Ventas":
            self.reportes_controller.reporte_actualizar_datos()
        elif tab_activa == "📈 Analíticas":
            self.reportes_controller.analitica_actualizar_datos()
        elif tab_activa == "🚚 Proveedores":
            self.proveedores_controller.cargar_datos(self.proveedores_controller.entry_buscar.get())
        elif tab_activa == "💰 Caja y Turnos":
            self.caja_controller.verificar_estado()

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


if __name__ == "__main__":
    import customtkinter as ctk
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = InventarioApp(root)
    root.mainloop()
