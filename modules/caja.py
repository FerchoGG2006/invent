import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database

class CajaTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_caja
        
        self.construir_tab()

    def construir_tab(self):
        # Panel Izquierdo (Control de Caja)
        frame_control = tk.Frame(self.tab, bg="#FFFFFF", width=340, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_control.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        frame_control.pack_propagate(False)

        tk.Label(frame_control, text="CONTROL DE CAJA", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=(10, 5))

        self.lbl_estado_turno = tk.Label(frame_control, text="Estado: CERRADO", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#EF4444")
        self.lbl_estado_turno.pack(pady=5)

        self.btn_abrir_turno = tk.Button(frame_control, text="Abrir Turno", font=("Segoe UI", 10, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=self.abrir_turno)
        self.btn_abrir_turno.pack(fill=tk.X, padx=25, pady=10, ipady=5)

        self.btn_cerrar_turno = tk.Button(frame_control, text="Cerrar Turno", font=("Segoe UI", 10, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.cerrar_turno, state=tk.DISABLED)
        self.btn_cerrar_turno.pack(fill=tk.X, padx=25, pady=10, ipady=5)

        tk.Frame(frame_control, bg="#E2E8F0", height=1).pack(fill=tk.X, padx=15, pady=15)

        tk.Label(frame_control, text="Monto Base Apertura ($):", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").pack()
        self.entry_apertura = tk.Entry(frame_control, font=("Segoe UI", 10), justify="center")
        self.entry_apertura.pack(pady=5)
        self.entry_apertura.insert(0, "0")

        # Panel Derecho (Resumen y Movimientos)
        frame_grid = tk.Frame(self.tab, bg="#F8FAFC")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=10)

        tk.Label(frame_grid, text="Movimientos del Turno Actual", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=(0, 10))

        # Tabla Movimientos (Simplificada para el ejemplo)
        columnas = ("id", "fecha", "tipo", "monto", "descripcion")
        self.tabla = ttk.Treeview(frame_grid, columns=columnas, show="headings")
        headers = [("ID", 40), ("Fecha", 140), ("Tipo", 100), ("Monto", 100), ("Descripción", 200)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        self.verificar_estado()

    def verificar_estado(self):
        # Verifica si hay un turno abierto
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, monto_apertura FROM turnos_caja WHERE estado = 'Abierto'")
            res = cursor.fetchone()
            if res:
                self.turno_actual = res[0]
                self.lbl_estado_turno.config(text=f"Estado: ABIERTO (ID: {self.turno_actual})", fg="#10B981")
                self.btn_abrir_turno.config(state=tk.DISABLED)
                self.btn_cerrar_turno.config(state=tk.NORMAL)
                self.entry_apertura.delete(0, tk.END)
                self.entry_apertura.insert(0, str(res[1]))
                self.entry_apertura.config(state=tk.DISABLED)
                self.cargar_movimientos()
            else:
                self.turno_actual = None
                self.lbl_estado_turno.config(text="Estado: CERRADO", fg="#EF4444")
                self.btn_abrir_turno.config(state=tk.NORMAL)
                self.btn_cerrar_turno.config(state=tk.DISABLED)
                self.entry_apertura.config(state=tk.NORMAL)
                for item in self.tabla.get_children():
                    self.tabla.delete(item)

    def abrir_turno(self):
        try:
            apertura = float(self.entry_apertura.get())
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
            return
            
        exito, msg = database.abrir_turno_caja(1, apertura) # User 1 para simplificar
        if exito:
            messagebox.showinfo("Caja", msg)
            self.verificar_estado()
        else:
            messagebox.showerror("Error", msg)

    def cerrar_turno(self):
        if not self.turno_actual:
            return
            
        cierre_real = simpledialog.askfloat("Cierre de Caja", "Ingresa el monto total en caja (Efectivo):")
        if cierre_real is not None:
            exito, msg = database.cerrar_turno_caja(self.turno_actual, cierre_real)
            if exito:
                messagebox.showinfo("Caja", msg)
                self.verificar_estado()
            else:
                messagebox.showerror("Error", msg)

    def cargar_movimientos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        if not self.turno_actual:
            return
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fecha, tipo, monto, descripcion FROM movimientos_caja WHERE turno_id = ? ORDER BY fecha DESC", (self.turno_actual,))
            for mov in cursor.fetchall():
                self.tabla.insert("", tk.END, values=(mov[0], mov[1], mov[2], f"${mov[3]:,.0f}", mov[4]))
