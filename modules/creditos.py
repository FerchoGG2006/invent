import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import database

class CreditosTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_creditos
        self.construir_tab()
        self.cargar_datos()

    def construir_tab(self):
        # Frame superior: Controles
        frame_controles = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(frame_controles, text="📓 CUENTAS POR COBRAR (FIADOS)", font=("Segoe UI", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side=tk.LEFT)

        self.btn_recargar = ctk.CTkButton(frame_controles, text="Recargar", width=80, command=self.cargar_datos)
        self.btn_recargar.pack(side=tk.RIGHT, padx=10)

        # Frame central: Tabla
        frame_tabla = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columnas = ("id", "cliente", "monto", "saldo", "estado", "fecha")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        headers = [("ID", 40), ("Cliente", 200), ("Monto Original", 120), ("Saldo Pendiente", 120), ("Estado", 100), ("Fecha", 140)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col != "cliente" else tk.W)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame inferior: Acciones
        frame_acciones = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_acciones.pack(fill=tk.X, padx=15, pady=10)

        btn_abonar = ctk.CTkButton(frame_acciones, text="💰 Registrar Abono", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 12, "bold"), command=self.registrar_abono)
        btn_abonar.pack(side=tk.RIGHT, padx=5)

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, cliente_nombre, monto_total, saldo_pendiente, estado, fecha_registro 
                    FROM cuentas_cobrar 
                    ORDER BY CASE WHEN estado = 'Pendiente' THEN 0 ELSE 1 END, fecha_registro DESC
                """)
                cuentas = cursor.fetchall()
                for c in cuentas:
                    self.tabla.insert("", tk.END, values=(c[0], c[1], f"${c[2]:,.0f}", f"${c[3]:,.0f}", c[4], c[5][:16]))
            except Exception as e:
                print(f"Error cargando creditos: {e}")

    def registrar_abono(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una cuenta para abonar.")
            return

        item_vals = self.tabla.item(seleccion[0])["values"]
        cuenta_id = item_vals[0]
        estado = item_vals[4]
        
        if estado == "Pagado":
            messagebox.showinfo("Atención", "Esta cuenta ya está totalmente pagada.")
            return

        # Pedir monto
        from tkinter import simpledialog
        monto_str = simpledialog.askstring("Abono", f"Ingrese el monto a abonar a la cuenta de {item_vals[1]}:")
        if not monto_str: return
        
        try:
            monto = float(monto_str)
            if monto <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
            return
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT saldo_pendiente FROM cuentas_cobrar WHERE id = ?", (cuenta_id,))
            res = cursor.fetchone()
            if not res: return
            saldo_actual = res[0]
            
            nuevo_saldo = saldo_actual - monto
            nuevo_estado = "Pagado" if nuevo_saldo <= 0 else "Pendiente"
            if nuevo_saldo < 0: nuevo_saldo = 0
            
            # Registrar abono
            cursor.execute("INSERT INTO abonos (cuenta_id, monto, metodo_pago) VALUES (?, ?, 'Efectivo')", (cuenta_id, monto))
            # Actualizar cuenta
            cursor.execute("UPDATE cuentas_cobrar SET saldo_pendiente = ?, estado = ? WHERE id = ?", (nuevo_saldo, nuevo_estado, cuenta_id))
            
            # Si hay un turno abierto, registrar el ingreso a caja (opcional, pero buena práctica)
            cursor.execute("SELECT id FROM turnos_caja WHERE estado = 'Abierto'")
            res_turno = cursor.fetchone()
            if res_turno:
                cursor.execute("INSERT INTO movimientos_caja (turno_id, tipo, monto, descripcion) VALUES (?, 'Ingreso', ?, ?)", 
                               (res_turno[0], monto, f"Abono de cuenta #{cuenta_id} ({item_vals[1]})"))
                               
            conn.commit()
            
        messagebox.showinfo("Éxito", f"Abono registrado. Nuevo saldo: ${nuevo_saldo:,.0f}")
        self.cargar_datos()
