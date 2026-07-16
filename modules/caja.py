import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import database

class CajaTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_caja
        self.turno_actual = None
        self.construir_tab()

    def construir_tab(self):
        # Frame Principal Izquierdo (Control)
        frame_control = ctk.CTkFrame(self.tab, width=320, fg_color=("#FFFFFF", "#1E293B"), border_color=("#E2E8F0", "#334155"), border_width=1, corner_radius=8)
        frame_control.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 10), pady=20)
        frame_control.pack_propagate(False)

        ctk.CTkLabel(frame_control, text="Caja Registradora", font=("Segoe UI", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(pady=(20, 5))
        
        # Tarjeta de Estado
        self.frame_estado = ctk.CTkFrame(frame_control, fg_color="#FEE2E2", corner_radius=8)
        self.frame_estado.pack(fill=tk.X, padx=20, pady=10)
        
        self.lbl_estado_titulo = ctk.CTkLabel(self.frame_estado, text="ESTADO DEL TURNO", font=("Segoe UI", 10, "bold"), text_color="#991B1B")
        self.lbl_estado_titulo.pack(pady=(10, 0))
        self.lbl_estado_valor = ctk.CTkLabel(self.frame_estado, text="CERRADO", font=("Segoe UI", 20, "bold"), text_color="#DC2626")
        self.lbl_estado_valor.pack(pady=(0, 10))

        # Controles
        ctk.CTkLabel(frame_control, text="Monto Base de Apertura ($)", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, padx=20, pady=(15, 5))
        self.entry_apertura = ctk.CTkEntry(frame_control, font=("Segoe UI", 12), height=40, corner_radius=6, justify="center")
        self.entry_apertura.pack(fill=tk.X, padx=20)
        self.entry_apertura.insert(0, "0")

        self.btn_abrir_turno = ctk.CTkButton(frame_control, text="🔓 Abrir Turno", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=45, corner_radius=6, command=self.abrir_turno)
        self.btn_abrir_turno.pack(fill=tk.X, padx=20, pady=(20, 10))

        self.btn_cerrar_turno = ctk.CTkButton(frame_control, text="🔒 Cerrar Turno", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=45, corner_radius=6, state=tk.DISABLED, command=self.cerrar_turno)
        self.btn_cerrar_turno.pack(fill=tk.X, padx=20, pady=5)
        
        # Resumen del turno actual
        self.frame_resumen = ctk.CTkFrame(frame_control, fg_color="transparent")
        self.frame_resumen.pack(fill=tk.X, padx=20, pady=20)
        
        self.lbl_resumen_ventas = ctk.CTkLabel(self.frame_resumen, text="Ventas del Turno: $0", font=("Segoe UI", 12), text_color=("#475569", "#CBD5E1"))
        self.lbl_resumen_ventas.pack(anchor=tk.W)
        self.lbl_resumen_efectivo = ctk.CTkLabel(self.frame_resumen, text="Ingresos en Efectivo: $0", font=("Segoe UI", 12, "bold"), text_color=("#0F172A", "#F8FAFC"))
        self.lbl_resumen_efectivo.pack(anchor=tk.W, pady=5)

        # Panel Derecho (Movimientos)
        frame_grid = ctk.CTkFrame(self.tab, fg_color=("#FFFFFF", "#1E293B"), border_color=("#E2E8F0", "#334155"), border_width=1, corner_radius=8)
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)

        ctk.CTkLabel(frame_grid, text="Movimientos del Turno", font=("Segoe UI", 12, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor=tk.W, padx=20, pady=(15, 10))

        # Tabla
        columnas = ("id", "fecha", "tipo", "monto", "descripcion")
        self.tabla = ttk.Treeview(frame_grid, columns=columnas, show="headings", height=15)
        headers = [("ID", 40), ("Fecha / Hora", 140), ("Tipo", 100), ("Monto ($)", 120), ("Descripción", 250)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col in ("id", "monto", "tipo") else tk.W)
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))



        self.verificar_estado()

    def verificar_estado(self):
        res = database.obtener_turno_abierto()
        if res:
            self.turno_actual = res[0]
            # Estado Abierto
            self.frame_estado.configure(fg_color="#D1FAE5")
            self.lbl_estado_titulo.configure(text_color="#065F46")
            self.lbl_estado_valor.configure(text="ABIERTO", text_color="#059669")
            
            self.btn_abrir_turno.configure(state=tk.DISABLED)
            self.btn_cerrar_turno.configure(state=tk.NORMAL)
            
            self.entry_apertura.delete(0, tk.END)
            self.entry_apertura.insert(0, f"{res[1]:.0f}")
            self.entry_apertura.configure(state=tk.DISABLED)
            
            # Actualizar resumen
            resumen = database.obtener_resumen_turno(self.turno_actual)
            self.lbl_resumen_ventas.configure(text=f"Ventas Totales: ${resumen['total_ventas']:,.0f}")
            self.lbl_resumen_efectivo.configure(text=f"Ventas Efectivo: ${resumen['efectivo']:,.0f}")
            
            self.cargar_movimientos()
        else:
            self.turno_actual = None
            # Estado Cerrado
            self.frame_estado.configure(fg_color="#FEE2E2")
            self.lbl_estado_titulo.configure(text_color="#991B1B")
            self.lbl_estado_valor.configure(text="CERRADO", text_color="#DC2626")
            
            self.btn_abrir_turno.configure(state=tk.NORMAL)
            self.btn_cerrar_turno.configure(state=tk.DISABLED)
            
            self.entry_apertura.configure(state=tk.NORMAL)
            self.entry_apertura.delete(0, tk.END)
            self.entry_apertura.insert(0, "0")
            
            self.lbl_resumen_ventas.configure(text="Ventas Totales: $0")
            self.lbl_resumen_efectivo.configure(text="Ventas Efectivo: $0")
            
            for item in self.tabla.get_children():
                self.tabla.delete(item)

    def abrir_turno(self):
        try:
            apertura = float(self.entry_apertura.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Monto de apertura inválido", parent=self.tab)
            return
            
        usuario_id = self.app.usuario_actual_id if hasattr(self.app, 'usuario_actual_id') else 1
        
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO turnos_caja (caja_id, usuario_id, monto_apertura, estado) 
                VALUES (1, ?, ?, 'Abierto')
            """, (usuario_id, apertura))
            turno_id = cursor.lastrowid
            
            if apertura > 0:
                cursor.execute("""
                    INSERT INTO movimientos_caja (turno_id, tipo, monto, descripcion) 
                    VALUES (?, 'Ingreso', ?, 'Monto base de apertura')
                """, (turno_id, apertura))
            conn.commit()
            
        messagebox.showinfo("Caja", "Turno abierto exitosamente.", parent=self.tab)
        self.verificar_estado()

    def cerrar_turno(self):
        if not self.turno_actual:
            return
            
        resumen = database.obtener_resumen_turno(self.turno_actual)
        apertura = float(self.entry_apertura.get() or 0)
        esperado = apertura + resumen['efectivo']
        
        dialog = ctk.CTkInputDialog(text=f"El sistema espera: ${esperado:,.0f} en EFECTIVO.\n\nIngresa el monto REAL (físico) en caja:", title="Cierre de Caja")
        monto_str = dialog.get_input()
        
        if monto_str is None:
            return # Cancelado
            
        try:
            cierre_real = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "Monto ingresado no es válido.", parent=self.tab)
            return
            
        exito, msg, calculado, diferencia = database.cerrar_turno_caja_mejorado(self.turno_actual, cierre_real)
        
        if exito:
            if diferencia < 0:
                det = f"Faltante de caja: ${abs(diferencia):,.0f}"
                messagebox.showwarning("Cierre con Faltante", f"{msg}\n\n{det}", parent=self.tab)
            elif diferencia > 0:
                det = f"Sobrante de caja: ${diferencia:,.0f}"
                messagebox.showinfo("Cierre con Sobrante", f"{msg}\n\n{det}", parent=self.tab)
            else:
                messagebox.showinfo("Cierre Cuadrado", f"{msg}\n\nCaja cuadrada perfectamente.", parent=self.tab)
            self.verificar_estado()
        else:
            messagebox.showerror("Error", msg, parent=self.tab)

    def cargar_movimientos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        if not self.turno_actual:
            return
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            # Cargar movimientos manuales
            cursor.execute("SELECT id, fecha, tipo, monto, descripcion FROM movimientos_caja WHERE turno_id = ? ORDER BY fecha DESC", (self.turno_actual,))
            for mov in cursor.fetchall():
                self.tabla.insert("", tk.END, values=(f"M{mov[0]}", mov[1], mov[2], f"${mov[3]:,.0f}", mov[4]))
            
            # Cargar ventas como ingresos
            cursor.execute("SELECT id, fecha, metodo_pago, total, cliente_nombre FROM ventas WHERE turno_id = ? ORDER BY fecha DESC", (self.turno_actual,))
            for v in cursor.fetchall():
                cliente = f" - {v[4]}" if v[4] else ""
                desc = f"Venta {v[2]}{cliente}"
                self.tabla.insert("", tk.END, values=(f"V{v[0]}", v[1], "Ingreso", f"${v[3]:,.0f}", desc))
