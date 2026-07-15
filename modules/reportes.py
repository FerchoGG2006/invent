import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import database
import csv
import datetime
import calendar

# Importar Matplotlib para los gráficos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def rc(color_val):
    if isinstance(color_val, tuple):
        import customtkinter as ctk
        try:
            return color_val[1] if ctk.get_appearance_mode() == "Dark" else color_val[0]
        except Exception:
            return color_val[0]
    return color_val


class CalendarDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback, cancel_callback):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.geometry("320x350")
        self.configure(fg_color=("#F8FAFC", "#0F172A"))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        width = 320
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        self.callback = callback
        self.cancel_callback = cancel_callback
        self.hoy = datetime.datetime.now()
        self.year = self.hoy.year
        self.month = self.hoy.month
        
        self.protocol("WM_DELETE_WINDOW", self.cancelar)
        
        self.crear_interfaz()
        self.dibujar_calendario()
        
    def crear_interfaz(self):
        # Header (Mes y Año con flechas)
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        self.btn_prev = ctk.CTkButton(self.frame_header, text="◀", width=30, height=30, 
                                     fg_color=("#E2E8F0", "#1E293B"), text_color=("#0F172A", "#F8FAFC"),
                                     hover_color=("#CBD5E1", "#334155"), corner_radius=6, command=self.mes_anterior)
        self.btn_prev.pack(side=tk.LEFT)
        
        self.lbl_mes_anio = ctk.CTkLabel(self.frame_header, text="", font=("Segoe UI", 12, "bold"), text_color=("#0F172A", "#F8FAFC"))
        self.lbl_mes_anio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_next = ctk.CTkButton(self.frame_header, text="▶", width=30, height=30, 
                                     fg_color=("#E2E8F0", "#1E293B"), text_color=("#0F172A", "#F8FAFC"),
                                     hover_color=("#CBD5E1", "#334155"), corner_radius=6, command=self.mes_siguiente)
        self.btn_next.pack(side=tk.RIGHT)
        
        # Días de la semana
        self.frame_semana = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_semana.pack(fill=tk.X, padx=15)
        
        dias = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for i, dia in enumerate(dias):
            color = "#EF4444" if i in [5, 6] else ("#475569", "#CBD5E1")
            lbl = ctk.CTkLabel(self.frame_semana, text=dia, font=("Segoe UI", 10, "bold"), text_color=color, width=40)
            lbl.grid(row=0, column=i, padx=2, pady=2)
            
        # Grid del Calendario
        self.frame_dias = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dias.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))
        
    def dibujar_calendario(self):
        for widget in self.frame_dias.winfo_children():
            widget.destroy()
            
        meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes_anio.configure(text=f"{meses_nombres[self.month-1]} {self.year}")
        
        cal = calendar.monthcalendar(self.year, self.month)
        
        for r_idx, week in enumerate(cal):
            for c_idx, day in enumerate(week):
                if day == 0:
                    lbl = ctk.CTkLabel(self.frame_dias, text="", width=40, height=32)
                    lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2)
                else:
                    es_hoy = (self.year == self.hoy.year and self.month == self.hoy.month and day == self.hoy.day)
                    
                    if es_hoy:
                        fg = "#4F46E5"
                        hover = "#3730A3"
                        text_col = "white"
                    else:
                        fg = ("#FFFFFF", "#1E293B")
                        hover = ("#F1F5F9", "#334155")
                        text_col = ("#0F172A", "#F8FAFC")
                        
                    btn = ctk.CTkButton(self.frame_dias, text=str(day), width=40, height=32,
                                       fg_color=fg, text_color=text_col, hover_color=hover,
                                       corner_radius=6, font=("Segoe UI", 10, "bold"),
                                       border_color=("#E2E8F0", "#334155") if not es_hoy else None,
                                       border_width=1 if not es_hoy else 0,
                                       command=lambda d=day: self.seleccionar_dia(d))
                    btn.grid(row=r_idx, column=c_idx, padx=2, pady=2)
                    
    def mes_anterior(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.dibujar_calendario()
        
    def mes_siguiente(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.dibujar_calendario()
        
    def seleccionar_dia(self, dia):
        fecha = datetime.date(self.year, self.month, dia)
        self.callback(fecha)
        self.destroy()
        
    def cancelar(self):
        self.cancel_callback()
        self.destroy()

class ReportesTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_reportes
        self.tab_analiticas = app.tab_analiticas
        self.ventas_data = []

        # Listas para guardar las referencias de los lienzos de Matplotlib
        self.canvas_tendencia = None
        self.canvas_pagos = None
        self.canvas_productos = None

        self.construir_tab()
        self.construir_tab_analiticas()

    # ==========================================
    # PESTAÑA: HISTORIAL DE VENTAS
    # ==========================================
    def construir_tab(self):
        # Panel superior con 4 tarjetas de resumen financiero
        frame_cards = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_cards.pack(fill=tk.X, padx=15, pady=(15, 5))

        # Tarjeta 1: Ventas Totales del Rango
        self.card_hoy = ctk.CTkFrame(frame_cards, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=8)
        self.card_hoy.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.lbl_card_hoy_titulo = ctk.CTkLabel(self.card_hoy, text="Ventas del Período", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8")))
        self.lbl_card_hoy_titulo.pack(anchor=tk.W, padx=15, pady=(10, 0))
        self.lbl_card_hoy_valor = ctk.CTkLabel(self.card_hoy, text="$0", font=("Segoe UI", 18, "bold"), text_color="#4F46E5")
        self.lbl_card_hoy_valor.pack(anchor=tk.W, padx=15, pady=(2, 0))
        self.lbl_card_hoy_sub = ctk.CTkLabel(self.card_hoy, text="0 transacciones", font=("Segoe UI", 9), text_color="#94A3B8")
        self.lbl_card_hoy_sub.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Tarjeta 2: Ingresos por Tipo de Pago
        self.card_total = ctk.CTkFrame(frame_cards, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=8)
        self.card_total.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.lbl_card_tot_titulo = ctk.CTkLabel(self.card_total, text="Ingresos por Pago", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8")))
        self.lbl_card_tot_titulo.pack(anchor=tk.W, padx=15, pady=(10, 0))
        self.lbl_card_tot_valor = ctk.CTkLabel(self.card_total, text="Efectivo / Transferencia", font=("Segoe UI", 12, "bold"), text_color=rc(("#0F172A", "#F8FAFC")))
        self.lbl_card_tot_valor.pack(anchor=tk.W, padx=15, pady=(2, 0))
        self.lbl_card_tot_sub = ctk.CTkLabel(self.card_total, text="Efe: $0 | Transf: $0", font=("Segoe UI", 10), text_color=rc(("#475569", "#CBD5E1")))
        self.lbl_card_tot_sub.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Tarjeta 3: Utilidad Real (Ganancia Neta)
        self.card_utilidad = ctk.CTkFrame(frame_cards, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=8)
        self.card_utilidad.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.lbl_card_ut_titulo = ctk.CTkLabel(self.card_utilidad, text="Ganancia Neta (Utilidad)", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8")))
        self.lbl_card_ut_titulo.pack(anchor=tk.W, padx=15, pady=(10, 0))
        self.lbl_card_ut_valor = ctk.CTkLabel(self.card_utilidad, text="$0", font=("Segoe UI", 18, "bold"), text_color="#10B981")
        self.lbl_card_ut_valor.pack(anchor=tk.W, padx=15, pady=(2, 0))
        self.lbl_card_ut_sub = ctk.CTkLabel(self.card_utilidad, text="Ingreso - Costo Adquisición", font=("Segoe UI", 9), text_color="#059669")
        self.lbl_card_ut_sub.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Tarjeta 4: Top 3 Más Vendidos
        self.card_top = ctk.CTkFrame(frame_cards, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=8)
        self.card_top.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.lbl_card_top_titulo = ctk.CTkLabel(self.card_top, text="Top 3 Más Vendidos", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8")))
        self.lbl_card_top_titulo.pack(anchor=tk.W, padx=15, pady=(10, 0))
        self.lbl_card_top_valor = ctk.CTkLabel(self.card_top, text="Cargando...", font=("Segoe UI", 10, "bold"), text_color="#334155", justify=tk.LEFT)
        self.lbl_card_top_valor.pack(anchor=tk.W, padx=15, pady=(2, 10))

        # Grid de Reportes
        frame_reporte_grid = ctk.CTkFrame(self.tab, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=12)
        frame_reporte_grid.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header de controles (Filtro de fecha y botones de acción)
        frame_controles_rep = ctk.CTkFrame(frame_reporte_grid, fg_color="transparent")
        frame_controles_rep.pack(fill=tk.X, padx=15, pady=15)

        ctk.CTkLabel(frame_controles_rep, text="TRANSACCIONES REGISTRADAS", font=("Segoe UI", 11, "bold"), text_color=rc(("#0F172A", "#F8FAFC"))).pack(side=tk.LEFT)

        # Selector de Fecha
        ctk.CTkLabel(frame_controles_rep, text="Filtrar:", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8"))).pack(side=tk.LEFT, padx=(20, 5))
        self.combo_filtro_fecha = ctk.CTkComboBox(frame_controles_rep, values=["Todo", "Hoy", "Últimos 7 días", "Este Mes", "Elegir Día..."], font=("Segoe UI", 10), height=28, width=140, command=self._on_filtro_changed)
        self.combo_filtro_fecha.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_fecha.set("Todo")
        self._filtro_fecha_especifica = None  # Guarda la fecha seleccionada en formato YYYY-MM-DD

        # Botones de Acciones en Reportes
        btn_logout = ctk.CTkButton(frame_controles_rep, text="🚪 Cerrar Sesión", font=("Segoe UI", 10, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=28, width=105, corner_radius=6, command=self.app.cerrar_sesion)
        btn_logout.pack(side=tk.RIGHT, padx=3)

        btn_config = ctk.CTkButton(frame_controles_rep, text="⚙️ Configuración", font=("Segoe UI", 10, "bold"), fg_color=rc(("#475569", "#CBD5E1")), hover_color="#334155", text_color="white", height=28, width=105, corner_radius=6, command=self.app.mostrar_editar_configuracion)
        btn_config.pack(side=tk.RIGHT, padx=3)

        btn_usuarios = ctk.CTkButton(frame_controles_rep, text="👥 Usuarios", font=("Segoe UI", 10, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", text_color="white", height=28, width=90, corner_radius=6, command=self.app.mostrar_gestion_usuarios)
        btn_usuarios.pack(side=tk.RIGHT, padx=3)

        btn_reimprimir = ctk.CTkButton(frame_controles_rep, text="🖨️ Ver Ticket", font=("Segoe UI", 10, "bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", height=28, width=90, corner_radius=6, command=self.reimprimir_ticket_seleccionado)
        btn_reimprimir.pack(side=tk.RIGHT, padx=3)

        btn_anular = ctk.CTkButton(frame_controles_rep, text="Anular Venta", font=("Segoe UI", 10, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=28, width=90, corner_radius=6, command=self.anular_venta_seleccionada)
        btn_anular.pack(side=tk.RIGHT, padx=3)

        btn_devolucion = ctk.CTkButton(frame_controles_rep, text="Devolución Parcial", font=("Segoe UI", 10, "bold"), fg_color="#F43F5E", hover_color="#E11D48", text_color="white", height=28, width=120, corner_radius=6, command=self.devolver_venta_parcial)
        btn_devolucion.pack(side=tk.RIGHT, padx=3)

        btn_backup = ctk.CTkButton(frame_controles_rep, text="Respaldar DB", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#3730A3", text_color="white", height=28, width=95, corner_radius=6, command=self.app.respaldar_base_datos)
        btn_backup.pack(side=tk.RIGHT, padx=3)

        btn_corte = ctk.CTkButton(frame_controles_rep, text="Corte de Caja", font=("Segoe UI", 10, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=28, width=95, corner_radius=6, command=self.generar_corte_caja)
        btn_corte.pack(side=tk.RIGHT, padx=3)

        btn_exportar = ctk.CTkButton(frame_controles_rep, text="Exportar (CSV)", font=("Segoe UI", 10, "bold"), fg_color="#1E293B", hover_color=rc(("#0F172A", "#F8FAFC")), text_color="white", height=28, width=95, corner_radius=6, command=self.exportar_reporte_csv)
        btn_exportar.pack(side=tk.RIGHT, padx=3)

        btn_exportar_pdf = ctk.CTkButton(frame_controles_rep, text="Exportar (PDF)", font=("Segoe UI", 10, "bold"), fg_color="#0EA5E9", hover_color="#0284C7", text_color="white", height=28, width=95, corner_radius=6, command=self.exportar_reporte_pdf)
        btn_exportar_pdf.pack(side=tk.RIGHT, padx=3)

        # Tabla del reporte
        frame_tabla = ctk.CTkFrame(frame_reporte_grid, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columnas_rep = ("id", "codigo", "nombre", "cantidad", "precio", "descuento", "total", "fecha", "metodo_pago")
        self.tabla_reporte = ttk.Treeview(frame_tabla, columns=columnas_rep, show="headings")

        headers_rep = [("ID Venta", 60), ("Referencia", 100), ("Producto", 190), ("Cant.", 60), ("Precio Unit.", 90), ("Desc.", 70), ("Total Venta", 90), ("Fecha / Hora", 150), ("Método", 90)]
        for col, (texto, ancho) in zip(columnas_rep, headers_rep):
            self.tabla_reporte.heading(col, text=texto)
            self.tabla_reporte.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)

        self.tabla_reporte.pack(fill=tk.BOTH, expand=True)

    def _on_filtro_changed(self, seleccion):
        """Maneja el cambio de filtro. Si es 'Elegir Día...' abre el selector de fecha."""
        if seleccion == "Elegir Día...":
            self._abrir_selector_fecha()
        else:
            self._filtro_fecha_especifica = None
            self.reporte_actualizar_datos()

    def _abrir_selector_fecha(self):
        """Abre un calendario moderno interactivo para elegir un día específico."""
        def callback(fecha):
            self._filtro_fecha_especifica = fecha.strftime("%Y-%m-%d")
            self.combo_filtro_fecha.set(fecha.strftime("%d/%m/%Y"))
            self.reporte_actualizar_datos()

        def cancelar():
            self.combo_filtro_fecha.set("Todo")
            self._filtro_fecha_especifica = None
            self.reporte_actualizar_datos()

        CalendarDialog(self.app.root, callback, cancelar)

    def reporte_actualizar_datos(self):
        filtro = self.combo_filtro_fecha.get()
        fecha_especifica = self._filtro_fecha_especifica
        resumen = database.obtener_resumen_ventas(filtro, fecha_especifica=fecha_especifica)

        self.lbl_card_hoy_valor.configure(text=f"${resumen['total']:,.0f}")
        self.lbl_card_hoy_sub.configure(text=f"{resumen['cant']} transacciones")

        self.lbl_card_tot_sub.configure(
            text=f"Efe: ${resumen['efe']:,.0f}  |  Transf: ${resumen['tra']:,.0f}"
        )

        self.lbl_card_ut_valor.configure(text=f"${resumen['utilidad']:,.0f}")
        if resumen['utilidad'] >= 0:
            self.lbl_card_ut_valor.configure(text_color="#10B981")
        else:
            self.lbl_card_ut_valor.configure(text_color="#EF4444")

        top_prods = database.obtener_top_productos(filtro, fecha_especifica=fecha_especifica)
        if top_prods:
            top_texto = "\n".join([f"{i+1}. {p[0]} ({p[1]} uds)" for i, p in enumerate(top_prods)])
            self.lbl_card_top_valor.configure(text=top_texto)
        else:
            self.lbl_card_top_valor.configure(text="Sin ventas en el período")

        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)

        self.ventas_data = database.obtener_ventas_reporte(filtro, fecha_especifica=fecha_especifica)
        for v in self.ventas_data:
            precio_f = f"${v[4]:,.0f}"
            desc_f = f"${v[8]:,.0f}" if v[8] else "$0"
            total_f = f"${v[5]:,.0f}"
            valores = (v[0], v[1] or "---", v[2], v[3], precio_f, desc_f, total_f, v[6], v[7])
            self.tabla_reporte.insert("", tk.END, values=valores)

    def reimprimir_ticket_seleccionado(self):
        seleccion = self.tabla_reporte.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una transacción de la tabla para ver/imprimir su ticket.")
            return
            
        valores = self.tabla_reporte.item(seleccion[0])["values"]
        venta_id = int(valores[0])
        
        venta = next((v for v in self.ventas_data if v[0] == venta_id), None)
        if not venta:
            return
            
        texto_ticket = "==============================\n"
        texto_ticket += "    COPIA TICKET DE VENTA     \n"
        texto_ticket += "==============================\n"
        texto_ticket += f"Ticket #: {venta[0]}\n"
        texto_ticket += f"Fecha: {venta[6]}\n"
        if venta[9]:
            texto_ticket += f"Cliente: {venta[9]}\n"
            if venta[10]:
                texto_ticket += f"ID: {venta[10]}\n"
        texto_ticket += "------------------------------\n"
        texto_ticket += "CANT  PRODUCTO          PRECIO\n"
        texto_ticket += "------------------------------\n"
        
        nombre = venta[2][:15].ljust(15)
        precio_bruto = venta[3] * venta[4]
        texto_ticket += f"{venta[3]:<4} {nombre} ${precio_bruto:,.0f}\n"
        texto_ticket += "------------------------------\n"
        
        if venta[8] and venta[8] > 0:
            texto_ticket += f"Descuento:         -${venta[8]:,.0f}\n"
        if venta[11] and venta[11] > 0:
            texto_ticket += f"Subtotal:           ${venta[5] - venta[11]:,.0f}\n"
            texto_ticket += f"IVA:                ${venta[11]:,.0f}\n"
        
        texto_ticket += f"TOTAL:              ${venta[5]:,.0f}\n"
        texto_ticket += "------------------------------\n"
        texto_ticket += f"Método de Pago: {venta[7]}\n"
        
        if venta[14]:
            texto_ticket += "\n*** CORTESÍA ***\n"
            if venta[15]:
                texto_ticket += f"Autorizado por: {venta[15]}\n"
        
        if venta[12]:
            texto_ticket += f"\nFolio Fiscal:\n{venta[12]}\n"
        if venta[13]:
            texto_ticket += f"\nCódigo QR:\n{venta[13]}\n"
            
        texto_ticket += "\n    ¡Gracias por su compra!   \n"
        texto_ticket += "==============================\n"

        win = ctk.CTkToplevel(self.app.root)
        win.title(f"Ticket de Venta #{venta_id}")
        win.geometry("360x540")
        win.configure(fg_color=("#F8FAFC", "#0F172A"))
        win.grab_set()

        ctk.CTkLabel(win, text="Copia de Ticket", font=("Segoe UI", 12, "bold"), text_color=rc(("#0F172A", "#F8FAFC"))).pack(pady=10)

        txt = ctk.CTkTextbox(win, font=("Consolas", 11), height=340, width=320, border_color=("#D1D5DB", "#475569"), border_width=1, fg_color=("#FFFFFF", "#1E293B"), text_color="#334155")
        txt.pack(pady=5, padx=15)
        txt.insert(tk.END, texto_ticket)
        txt.configure(state="disabled")

        def imprimir():
            impresora = self.app.config.get("impresora_ticket", "")
            if not impresora:
                messagebox.showerror("Error", "No hay impresora configurada en Ajustes.", parent=win)
                return
            from utils.printer import enviar_impresion_directa
            exito, msg = enviar_impresion_directa(impresora, texto_ticket)
            if exito:
                messagebox.showinfo("Éxito", msg, parent=win)
            else:
                messagebox.showerror("Error de Impresión", msg, parent=win)

        btn_imprimir = ctk.CTkButton(win, text="🖨️ Imprimir Copia", font=("Segoe UI", 11, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=38, corner_radius=6, command=imprimir)
        btn_imprimir.pack(fill=tk.X, padx=15, pady=10)

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
            self.app.pos_actualizar_alertas_pestaña()
        else:
            messagebox.showerror("Error", msg)

    def devolver_venta_parcial(self):
        seleccion = self.tabla_reporte.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una transacción de la tabla para realizar una devolución parcial.")
            return

        valores = self.tabla_reporte.item(seleccion[0])["values"]
        venta_id = int(valores[0])
        producto_nombre = valores[2]
        cant_original = int(valores[3])
        
        if cant_original <= 1:
            messagebox.showinfo("Atención", "Esta venta solo tiene 1 unidad. Usa 'Anular Venta' para devolverla por completo.")
            return

        from tkinter import simpledialog
        cant_str = simpledialog.askstring("Devolución Parcial", f"¿Cuántas unidades de '{producto_nombre}' deseas devolver?\n(Máximo {cant_original - 1})")
        if not cant_str:
            return
            
        try:
            cant_devolver = int(cant_str)
        except ValueError:
            messagebox.showerror("Error", "Debes ingresar un número válido.")
            return
            
        exito, msg = database.devolucion_parcial(venta_id, cant_devolver)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.reporte_actualizar_datos()
        else:
            messagebox.showerror("Error", msg)

    def generar_corte_caja(self):
        fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
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

        win = ctk.CTkToplevel(self.app.root)
        win.title("Corte de Caja Diario")
        win.geometry("360x420")
        win.configure(fg_color=("#F8FAFC", "#0F172A"))
        win.grab_set()

        ctk.CTkLabel(win, text="Cierre de Caja del Día", font=("Segoe UI", 12, "bold"), text_color=rc(("#0F172A", "#F8FAFC"))).pack(pady=15)

        txt = ctk.CTkTextbox(win, font=("Consolas", 11), height=200, width=320, border_color=("#D1D5DB", "#475569"), border_width=1, fg_color=("#FFFFFF", "#1E293B"), text_color="#334155")
        txt.pack(pady=5, padx=15)
        txt.insert(tk.END, texto_corte)
        txt.configure(state="disabled")

        def copiar():
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(texto_corte)
            messagebox.showinfo("Copiado", "¡Corte de caja copiado al portapapeles!", parent=win)

        def imprimir():
            impresora = self.app.config.get("impresora_ticket", "")
            if not impresora:
                messagebox.showerror("Error", "No hay impresora configurada en Ajustes.", parent=win)
                return
            from utils.printer import enviar_impresion_directa
            exito, msg = enviar_impresion_directa(impresora, texto_corte)
            if exito:
                messagebox.showinfo("Éxito", msg, parent=win)
                win.destroy()
            else:
                messagebox.showerror("Error de Impresión", msg, parent=win)

        frame_btns = ctk.CTkFrame(win, fg_color="transparent")
        frame_btns.pack(fill=tk.X, padx=15, pady=10)

        btn_imprimir = ctk.CTkButton(frame_btns, text="🖨️ Imprimir Ticket", font=("Segoe UI", 10, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=35, corner_radius=6, command=imprimir)
        btn_imprimir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        btn_copiar = ctk.CTkButton(frame_btns, text="📋 Copiar y Cerrar", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#3730A3", text_color="white", height=35, corner_radius=6, command=copiar)
        btn_copiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

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

    def exportar_reporte_pdf(self):
        filtro = self.combo_filtro_fecha.get()
        ventas = database.obtener_ventas_reporte(filtro)
        if not ventas:
            messagebox.showinfo("Exportar", "No hay registros de ventas para exportar con el filtro actual.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte de Ventas PDF",
            initialfile=f"Reporte_Ventas_{filtro.replace(' ', '_')}.pdf"
        )
        if not ruta:
            return

        try:
            from utils.pdf_export import generar_reporte_pdf
            resumen = database.obtener_resumen_ventas(filtro)
            exito = generar_reporte_pdf(ruta, filtro, resumen, ventas)
            if exito:
                messagebox.showinfo("Exportación Exitosa", f"El archivo PDF ha sido guardado exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo generar el archivo PDF:\n{str(e)}")

    # ==========================================
    # PESTAÑA NUEVA: TABLERO DE ANALÍTICAS (MATPLOTLIB)
    # ==========================================
    def construir_tab_analiticas(self):
        # Panel superior de controles de analítica
        frame_controles = ctk.CTkFrame(self.tab_analiticas, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=8, height=60)
        frame_controles.pack(fill=tk.X, padx=15, pady=(15, 10))

        ctk.CTkLabel(frame_controles, text="📊 TABLERO ESTADÍSTICO DE TU NEGOCIO", font=("Segoe UI", 12, "bold"), text_color=rc(("#0F172A", "#F8FAFC"))).pack(side=tk.LEFT, padx=15, pady=15)

        # Combo para seleccionar rango en analíticas
        ctk.CTkLabel(frame_controles, text="Período:", font=("Segoe UI", 10, "bold"), text_color=rc(("#64748B", "#94A3B8"))).pack(side=tk.LEFT, padx=(20, 5))
        self.combo_filtro_analitica = ctk.CTkComboBox(frame_controles, values=["Todo", "Hoy", "Últimos 7 días", "Este Mes"], font=("Segoe UI", 10), height=28, width=120, command=lambda e: self.analitica_actualizar_datos())
        self.combo_filtro_analitica.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_analitica.set("Este Mes")

        # Contenedor para colocar los gráficos (Grid flexible)
        self.frame_graficos = ctk.CTkFrame(self.tab_analiticas, fg_color="transparent")
        self.frame_graficos.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Configurar grid de 2 columnas y 2 filas
        self.frame_graficos.columnconfigure(0, weight=1)
        self.frame_graficos.columnconfigure(1, weight=1)
        self.frame_graficos.rowconfigure(0, weight=1)

    def analitica_actualizar_datos(self):
        filtro = self.combo_filtro_analitica.get()

        # Limpiar widgets previos dentro del frame de gráficos
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        # Crear contenedores para los gráficos
        # Panel Izquierdo: Línea de Tendencia (Ventas a lo largo del tiempo)
        frame_izq = ctk.CTkFrame(self.frame_graficos, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=12)
        frame_izq.grid(row=0, column=0, padx=(0, 7), pady=5, sticky="nsew")
        
        # Panel Derecho Superior: Pie Chart (Método de Pago)
        frame_der_up = ctk.CTkFrame(self.frame_graficos, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=12)
        frame_der_up.grid(row=0, column=1, padx=(7, 0), pady=5, sticky="nsew")

        # Configurar filas extras para el gráfico de barras horizontales (Top Productos) en la fila inferior
        self.frame_graficos.rowconfigure(1, weight=1)
        frame_inf = ctk.CTkFrame(self.frame_graficos, fg_color=("#FFFFFF", "#1E293B"), border_color=rc(("#E2E8F0", "#334155")), border_width=1, corner_radius=12)
        frame_inf.grid(row=1, column=0, columnspan=2, padx=0, pady=(10, 5), sticky="nsew")

        # Consultar datos para graficar
        ventas = database.obtener_ventas_reporte(filtro)
        resumen = database.obtener_resumen_ventas(filtro)

        # ---------------------------------------------
        # 1. GRÁFICO 1: TENDENCIA DE VENTAS (Líneas)
        # ---------------------------------------------
        fig_tendencia = Figure(figsize=(5, 3), dpi=90)
        fig_tendencia.patch.set_facecolor(rc(("#FFFFFF", "#1E293B")))
        ax_tendencia = fig_tendencia.add_subplot(111)
        ax_tendencia.set_facecolor(rc(("#FFFFFF", "#1E293B")))
        
        # Agrupar ventas por fecha
        datos_tiempo = {}
        for v in reversed(ventas): # Invertir para orden cronológico
            fecha_str = v[6].split(" ")[0] # Tomar solo YYYY-MM-DD
            monto = v[5]
            datos_tiempo[fecha_str] = datos_tiempo.get(fecha_str, 0.0) + monto

        if datos_tiempo:
            fechas = list(datos_tiempo.keys())
            montos = list(datos_tiempo.values())
            # Tomar solo las últimas 10 fechas para no saturar
            fechas_plot = fechas[-10:]
            montos_plot = montos[-10:]
            
            # Formatear etiquetas de fecha cortas
            fechas_labels = [datetime.datetime.strptime(f, "%Y-%m-%d").strftime("%d/%m") if "-" in f else f for f in fechas_plot]

            ax_tendencia.plot(fechas_labels, montos_plot, marker='o', color='#4F46E5', linewidth=2.5, markersize=6)
            ax_tendencia.fill_between(fechas_labels, montos_plot, color='#4F46E5', alpha=0.1)
        else:
            ax_tendencia.text(0.5, 0.5, "Sin transacciones en este rango", ha='center', va='center', color=rc(("#64748B", "#94A3B8")))

        ax_tendencia.set_title("Evolución de Ingresos ($)", fontname="Segoe UI", fontsize=10, weight='bold', color=rc(("#0F172A", "#F8FAFC")), pad=10)
        ax_tendencia.spines['top'].set_visible(False)
        ax_tendencia.spines['right'].set_visible(False)
        ax_tendencia.spines['left'].set_color(rc(("#E2E8F0", "#334155")))
        ax_tendencia.spines['bottom'].set_color(rc(("#E2E8F0", "#334155")))
        ax_tendencia.tick_params(axis='both', colors=rc(("#475569", "#CBD5E1")), labelsize=8)
        ax_tendencia.grid(axis='y', linestyle='--', alpha=0.5, color=rc(("#E2E8F0", "#334155")))
        fig_tendencia.tight_layout()

        canvas_t = FigureCanvasTkAgg(fig_tendencia, master=frame_izq)
        canvas_t.draw()
        canvas_t.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ---------------------------------------------
        # 2. GRÁFICO 2: MÉTODOS DE PAGO (Circular)
        # ---------------------------------------------
        fig_pagos = Figure(figsize=(4.5, 3), dpi=90)
        fig_pagos.patch.set_facecolor(rc(("#FFFFFF", "#1E293B")))
        ax_pagos = fig_pagos.add_subplot(111)
        
        datos_pagos = {}
        for v in ventas:
            mp = v[7]
            monto = v[5]
            datos_pagos[mp] = datos_pagos.get(mp, 0.0) + monto

        if datos_pagos:
            labels = list(datos_pagos.keys())
            valores = list(datos_pagos.values())
            colores = ['#10B981', '#38BDF8', '#F59E0B', '#8B5CF6', '#EF4444', '#EC4899']
            
            # Dibujar gráfico de pastel plano y elegante
            wedges, texts, autotexts = ax_pagos.pie(
                valores, 
                labels=labels, 
                autopct='%1.0f%%', 
                startangle=90, 
                colors=colores[:len(labels)],
                textprops=dict(color="#1E293B", fontname="Segoe UI", fontsize=8),
                wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2) # Estilo Donut
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
        else:
            ax_pagos.text(0.5, 0.5, "Sin datos de cobros", ha='center', va='center', color=rc(("#64748B", "#94A3B8")))
            
        ax_pagos.set_title("Canales de Venta / Métodos de Pago", fontname="Segoe UI", fontsize=10, weight='bold', color=rc(("#0F172A", "#F8FAFC")), pad=10)
        fig_pagos.tight_layout()

        canvas_p = FigureCanvasTkAgg(fig_pagos, master=frame_der_up)
        canvas_p.draw()
        canvas_p.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ---------------------------------------------
        # 3. GRÁFICO 3: TOP 5 PRODUCTOS MÁS VENDIDOS (Barras Horizontales)
        # ---------------------------------------------
        fig_productos = Figure(figsize=(8, 2.5), dpi=90)
        fig_productos.patch.set_facecolor(rc(("#FFFFFF", "#1E293B")))
        ax_productos = fig_productos.add_subplot(111)
        ax_productos.set_facecolor(rc(("#FFFFFF", "#1E293B")))

        # Agrupar productos más vendidos
        datos_productos = {}
        for v in ventas:
            prod_nombre = v[2]
            cant = v[3]
            datos_productos[prod_nombre] = datos_productos.get(prod_nombre, 0) + cant

        if datos_productos:
            # Ordenar descendente y tomar los top 5
            productos_sorted = sorted(datos_productos.items(), key=lambda x: x[1], reverse=True)[:5]
            nombres_prod = [x[0] for x in productos_sorted]
            cants_prod = [x[1] for x in productos_sorted]

            # Invertir para que el mayor quede arriba
            nombres_prod.reverse()
            cants_prod.reverse()
            
            # Recortar nombres largos
            nombres_cortos = [n[:18] + ".." if len(n) > 20 else n for n in nombres_prod]

            bars = ax_productos.barh(nombres_cortos, cants_prod, color='#6366F1', height=0.6, edgecolor='none')
            
            # Mostrar números en el extremo de la barra
            for bar in bars:
                width = bar.get_width()
                ax_productos.text(
                    width + 0.1, 
                    bar.get_y() + bar.get_height()/2, 
                    f"{int(width)} uds", 
                    ha='left', 
                    va='center', 
                    color=rc(("#475569", "#CBD5E1")), 
                    fontname="Segoe UI", 
                    fontsize=8, 
                    weight='bold'
                )
        else:
            ax_productos.text(0.5, 0.5, "Sin productos vendidos en el rango", ha='center', va='center', color=rc(("#64748B", "#94A3B8")))

        ax_productos.set_title("Top 5 Productos con Mayor Rotación (Cantidad)", fontname="Segoe UI", fontsize=10, weight='bold', color=rc(("#0F172A", "#F8FAFC")), pad=10)
        ax_productos.spines['top'].set_visible(False)
        ax_productos.spines['right'].set_visible(False)
        ax_productos.spines['left'].set_color(rc(("#E2E8F0", "#334155")))
        ax_productos.spines['bottom'].set_color(rc(("#E2E8F0", "#334155")))
        ax_productos.tick_params(axis='both', colors=rc(("#475569", "#CBD5E1")), labelsize=8)
        fig_productos.tight_layout()

        canvas_pr = FigureCanvasTkAgg(fig_productos, master=frame_inf)
        canvas_pr.draw()
        canvas_pr.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
