import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import datetime

class ReportesTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_reportes
        self.construir_tab()

    def construir_tab(self):
        # Panel superior con 4 tarjetas de resumen financiero
        frame_cards = tk.Frame(self.tab, bg="#F8FAFC")
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
        frame_reporte_grid = tk.Frame(self.tab, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
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

        btn_backup = tk.Button(frame_controles_rep, text="Respaldar DB", font=("Segoe UI", 9, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=self.app.respaldar_base_datos)
        btn_backup.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_backup.bind("<Enter>", lambda e: btn_backup.config(bg="#3730A3"))
        btn_backup.bind("<Leave>", lambda e: btn_backup.config(bg="#4F46E5"))

        btn_anular = tk.Button(frame_controles_rep, text="Anular Venta", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.anular_venta_seleccionada)
        btn_anular.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_anular.bind("<Enter>", lambda e: btn_anular.config(bg="#DC2626"))
        btn_anular.bind("<Leave>", lambda e: btn_anular.config(bg="#EF4444"))

        btn_config = tk.Button(frame_controles_rep, text="⚙️ Configuración", font=("Segoe UI", 9, "bold"), bg="#475569", fg="white", bd=0, cursor="hand2", command=self.app.mostrar_editar_configuracion)
        btn_config.pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)
        btn_config.bind("<Enter>", lambda e: btn_config.config(bg="#334155"))
        btn_config.bind("<Leave>", lambda e: btn_config.config(bg="#475569"))

        btn_logout = tk.Button(frame_controles_rep, text="🚪 Cerrar Sesión", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.app.cerrar_sesion)
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

    def reporte_actualizar_datos(self):
        filtro = self.combo_filtro_fecha.get()
        resumen = database.obtener_resumen_ventas(filtro)

        self.lbl_card_hoy_valor.config(text=f"${resumen['total']:,.0f}")
        self.lbl_card_hoy_sub.config(text=f"{resumen['cant']} transacciones")

        self.lbl_card_tot_sub.config(
            text=f"Efe: ${resumen['efe']:,.0f}  |  Transf: ${resumen['tra']:,.0f}"
        )

        self.lbl_card_ut_valor.config(text=f"${resumen['utilidad']:,.0f}")
        if resumen['utilidad'] >= 0:
            self.lbl_card_ut_valor.config(fg="#10B981")
        else:
            self.lbl_card_ut_valor.config(fg="#EF4444")

        top_prods = database.obtener_top_productos(filtro)
        if top_prods:
            top_texto = "\n".join([f"{i+1}. {p[0]} ({p[1]} uds)" for i, p in enumerate(top_prods)])
            self.lbl_card_top_valor.config(text=top_texto)
        else:
            self.lbl_card_top_valor.config(text="Sin ventas en el período")

        for item in self.tabla_reporte.get_children():
            self.tabla_reporte.delete(item)

        ventas = database.obtener_ventas_reporte(filtro)
        for v in ventas:
            precio_f = f"${v[4]:,.0f}"
            total_f = f"${v[5]:,.0f}"
            valores = (v[0], v[1] or "---", v[2], v[3], precio_f, total_f, v[6], v[7])
            self.tabla_reporte.insert("", tk.END, values=valores)

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

        win = tk.Toplevel(self.app.root)
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
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(texto_corte)
            messagebox.showinfo("Copiado", "¡Corte de caja copiado al portapapeles!")
            win.destroy()

        btn_copiar = tk.Button(win, text="Copiar y Cerrar", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=copiar)
        btn_copiar.pack(fill=tk.X, padx=15, pady=15, ipady=6)

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
