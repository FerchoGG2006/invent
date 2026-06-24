import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import database
from datetime import datetime

class CitasTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_citas
        self.construir_tab()
        self.cargar_datos()

    def construir_tab(self):
        # Frame superior: Controles
        frame_controles = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(frame_controles, text="📅 AGENDA DE CITAS", font=("Segoe UI", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side=tk.LEFT)

        btn_nueva = ctk.CTkButton(frame_controles, text="+ Nueva Cita", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 12, "bold"), command=self.modal_nueva_cita)
        btn_nueva.pack(side=tk.RIGHT, padx=5)

        self.btn_hoy = ctk.CTkButton(frame_controles, text="Hoy", fg_color="#4F46E5", width=80, command=self.cargar_datos)
        self.btn_hoy.pack(side=tk.RIGHT, padx=10)

        # Frame central: Tabla
        frame_tabla = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columnas = ("id", "hora", "cliente", "telefono", "servicio", "barbero", "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        headers = [("ID", 40), ("Hora", 120), ("Cliente", 180), ("Teléfono", 100), ("Servicio", 150), ("Barbero", 120), ("Estado", 100)]
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

        btn_completar = ctk.CTkButton(frame_acciones, text="Marcar Completada", fg_color="#10B981", hover_color="#059669", command=self.marcar_completada)
        btn_completar.pack(side=tk.LEFT, padx=5)

        btn_cancelar = ctk.CTkButton(frame_acciones, text="Cancelar Cita", fg_color="#EF4444", hover_color="#DC2626", command=self.cancelar_cita)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                # Filtrar citas de "hoy" en adelante por defecto, pero por ahora traeremos todas las recientes
                cursor.execute("""
                    SELECT id, fecha_cita, cliente_nombre, cliente_telefono, servicio, barbero, estado 
                    FROM citas 
                    ORDER BY fecha_cita ASC
                """)
                citas = cursor.fetchall()
                for c in citas:
                    # c[1] asume formato 'YYYY-MM-DD HH:MM'
                    self.tabla.insert("", tk.END, values=(c[0], c[1], c[2], c[3] or "", c[4] or "Corte", c[5] or "Cualquiera", c[6]))
            except Exception as e:
                print(f"Error cargando citas: {e}")

    def modal_nueva_cita(self):
        win = ctk.CTkToplevel(self.app.root)
        win.title("Agendar Cita")
        win.geometry("400x450")
        win.grab_set()

        ctk.CTkLabel(win, text="Nueva Cita", font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        frame_form = ctk.CTkFrame(win, fg_color="transparent")
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20)

        ctk.CTkLabel(frame_form, text="Nombre del Cliente:").pack(anchor=tk.W, pady=(5,0))
        entry_nombre = ctk.CTkEntry(frame_form, width=350)
        entry_nombre.pack(pady=(0,5))

        ctk.CTkLabel(frame_form, text="Teléfono:").pack(anchor=tk.W, pady=(5,0))
        entry_tel = ctk.CTkEntry(frame_form, width=350)
        entry_tel.pack(pady=(0,5))

        ctk.CTkLabel(frame_form, text="Fecha y Hora (Ej: 2026-06-25 14:30):").pack(anchor=tk.W, pady=(5,0))
        entry_fecha = ctk.CTkEntry(frame_form, width=350)
        entry_fecha.pack(pady=(0,5))
        entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d 12:00"))
        
        ctk.CTkLabel(frame_form, text="Servicio:").pack(anchor=tk.W, pady=(5,0))
        entry_servicio = ctk.CTkEntry(frame_form, width=350)
        entry_servicio.pack(pady=(0,5))
        entry_servicio.insert(0, "Corte clásico")

        ctk.CTkLabel(frame_form, text="Barbero (Opcional):").pack(anchor=tk.W, pady=(5,0))
        entry_barbero = ctk.CTkEntry(frame_form, width=350)
        entry_barbero.pack(pady=(0,15))

        def guardar():
            nom = entry_nombre.get().strip()
            fec = entry_fecha.get().strip()
            if not nom or not fec:
                messagebox.showwarning("Error", "El nombre y la fecha son obligatorios", parent=win)
                return
            
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO citas (cliente_nombre, cliente_telefono, fecha_cita, servicio, barbero, estado)
                    VALUES (?, ?, ?, ?, ?, 'Pendiente')
                """, (nom, entry_tel.get().strip(), fec, entry_servicio.get().strip(), entry_barbero.get().strip()))
                conn.commit()
            
            messagebox.showinfo("Éxito", "Cita agendada.", parent=win)
            self.cargar_datos()
            win.destroy()

        ctk.CTkButton(win, text="Agendar Cita", command=guardar, fg_color="#4F46E5").pack(pady=10)

    def cambiar_estado(self, nuevo_estado):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una cita primero.")
            return

        cita_id = self.tabla.item(seleccion[0])["values"][0]
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, cita_id))
            conn.commit()
        self.cargar_datos()

    def marcar_completada(self):
        self.cambiar_estado('Completada')

    def cancelar_cita(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas cancelar esta cita?"):
            self.cambiar_estado('Cancelada')
