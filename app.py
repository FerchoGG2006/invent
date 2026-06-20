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


class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Ocultar inmediatamente para evitar parpadeos
        self.root.geometry("1200x750")
        self.root.configure(bg="#F8FAFC")  # Slate 50

        database.init_db()
        self.config = database.obtener_configuracion()

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

    # ==========================================
    # UTILIDADES DELEGADAS
    # ==========================================
    def obtener_ruta_imagenes(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "imagenes_productos")
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def verificar_conexion_async(self):
        def on_result(conectado):
            self.root.after(0, lambda: self.actualizar_indicador_conexion(conectado))
        verificar_conexion_async(on_result)

    def actualizar_indicador_conexion(self, conectado):
        if hasattr(self, "lbl_conexion_pos"):
            if conectado:
                self.lbl_conexion_pos.config(text="🟢 En línea", fg="#10B981")
            else:
                self.lbl_conexion_pos.config(text="🔴 Sin conexión", fg="#EF4444")

    def actualizar_labels_facturacion(self):
        if hasattr(self, "lbl_cliente_identificacion"):
            pais = self.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.config else "Otro"
            lbl_id_text = obtener_label_id_fiscal(pais)
            self.lbl_cliente_identificacion.config(text=lbl_id_text)

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

        # Estilo del Notebook (Pestañas)
        style.configure("TNotebook", background="#F8FAFC", borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#E2E8F0",
                        foreground="#334155",
                        padding=[15, 8],
                        font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#4F46E5")],
                  foreground=[("selected", "#FFFFFF")])

        # Estilo del Treeview
        style.configure("Treeview",
                        background="#FFFFFF",
                        foreground="#1E293B",
                        fieldbackground="#FFFFFF",
                        font=("Segoe UI", 9),
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background="#F1F5F9",
                        foreground="#334155",
                        font=("Segoe UI", 9, "bold"))
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

        # Agregar pestañas (Proveedores y Caja las añade sus propias clases o aquí)
        self.notebook.add(self.tab_inventario, text=" 📦 Inventario ")
        self.notebook.add(self.tab_pos, text=" 🛒 Punto de Venta ")
        self.notebook.add(self.tab_reportes, text=" 📊 Historial de Ventas ")

        # Evento al cambiar de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Inicializar controladores de cada pestaña
        self.inventario_controller = InventarioTab(self)
        self.pos_controller = PosTab(self)
        self.reportes_controller = ReportesTab(self)
        self.proveedores_controller = ProveedoresTab(self)
        self.caja_controller = CajaTab(self)

    # ==========================================
    # DELEGACIÓN DE MÉTODOS PARA COMPATIBILIDAD (Temporal o Helper)
    # ==========================================
    def cargar_datos(self):
        # Initial load logic via controller
        if hasattr(self, 'inventario_controller'):
            self.inventario_controller.cargar_datos(self.inventario_controller.entry_buscar.get())

    def pos_actualizar_alertas_pestaña(self):
        try:
            alertas = database.obtener_alertas_stock()
            if alertas > 0:
                self.notebook.tab(0, text=f" 📦 Inventario ({alertas} 🚨) ")
            else:
                self.notebook.tab(0, text=" 📦 Inventario ")
        except Exception:
            pass

    def on_tab_changed(self, event):
        pestaña_activa = self.notebook.index(self.notebook.select())
        if pestaña_activa == 0:
            self.inventario_controller.cargar_datos(self.inventario_controller.entry_buscar.get())
        elif pestaña_activa == 1:
            self.pos_controller.pos_actualizar_lista_productos(self.pos_controller.entry_busca_pos.get())
            self.pos_controller.pos_actualizar_tabla_carrito()
            self.verificar_conexion_async()
        elif pestaña_activa == 2:
            self.reportes_controller.reporte_actualizar_datos()

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
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()
