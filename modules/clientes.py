import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import database
from datetime import datetime

class ClientesTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_clientes
        self.construir_tab()
        self.cargar_datos()

    def construir_tab(self):
        # Frame superior: Controles
        frame_controles = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(frame_controles, text="👥 GESTIÓN DE CLIENTES", font=("Segoe UI", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(side=tk.LEFT)

        btn_nuevo = ctk.CTkButton(frame_controles, text="+ Nuevo Cliente", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 12, "bold"), command=self.modal_nuevo_cliente)
        btn_nuevo.pack(side=tk.RIGHT, padx=5)

        self.entry_buscar = ctk.CTkEntry(frame_controles, placeholder_text="Buscar cliente por nombre o teléfono...", width=250)
        self.entry_buscar.pack(side=tk.RIGHT, padx=10)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_clientes)

        # Frame central: Tabla
        frame_tabla = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columnas = ("id", "nombre", "telefono", "email", "puntos", "registro")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        headers = [("ID", 40), ("Nombre", 200), ("Teléfono", 120), ("Email", 180), ("Puntos", 80), ("Registro", 120)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col != "nombre" else tk.W)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame inferior: Botones de acción
        frame_acciones = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_acciones.pack(fill=tk.X, padx=15, pady=10)

        btn_eliminar = ctk.CTkButton(frame_acciones, text="Eliminar", fg_color="#EF4444", hover_color="#DC2626", command=self.eliminar_cliente)
        btn_eliminar.pack(side=tk.RIGHT)

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                # Intentamos usar la tabla nueva de Fase 4/5 si existe, o manejar la estructura correcta
                # La estructura creada en database.py (Fase 5) era: 
                # id, nombre, identificacion, telefono, email, direccion, notas, fecha_registro
                cursor.execute("SELECT id, nombre, telefono, email, identificacion, fecha_registro FROM clientes ORDER BY nombre ASC")
                clientes = cursor.fetchall()
                for c in clientes:
                    self.tabla.insert("", tk.END, values=(c[0], c[1], c[2] or "N/A", c[3] or "N/A", "0", c[5][:10] if c[5] else "N/A"))
            except Exception as e:
                print(f"Error cargando clientes: {e}")

    def buscar_clientes(self, event=None):
        filtro = self.entry_buscar.get().lower()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, telefono, email, identificacion, fecha_registro FROM clientes WHERE LOWER(nombre) LIKE ? OR telefono LIKE ? ORDER BY nombre ASC", (f"%{filtro}%", f"%{filtro}%"))
            clientes = cursor.fetchall()
            for c in clientes:
                self.tabla.insert("", tk.END, values=(c[0], c[1], c[2] or "N/A", c[3] or "N/A", "0", c[5][:10] if c[5] else "N/A"))

    def modal_nuevo_cliente(self):
        win = ctk.CTkToplevel(self.app.root)
        win.title("Nuevo Cliente")
        win.geometry("400x350")
        win.grab_set()

        ctk.CTkLabel(win, text="Datos del Cliente", font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        frame_form = ctk.CTkFrame(win, fg_color="transparent")
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20)

        ctk.CTkLabel(frame_form, text="Nombre completo:").pack(anchor=tk.W, pady=(5,0))
        entry_nombre = ctk.CTkEntry(frame_form, width=350)
        entry_nombre.pack(pady=(0,5))

        ctk.CTkLabel(frame_form, text="Teléfono:").pack(anchor=tk.W, pady=(5,0))
        entry_tel = ctk.CTkEntry(frame_form, width=350)
        entry_tel.pack(pady=(0,5))

        ctk.CTkLabel(frame_form, text="Email:").pack(anchor=tk.W, pady=(5,0))
        entry_email = ctk.CTkEntry(frame_form, width=350)
        entry_email.pack(pady=(0,5))
        
        ctk.CTkLabel(frame_form, text="Identificación (Opcional):").pack(anchor=tk.W, pady=(5,0))
        entry_id = ctk.CTkEntry(frame_form, width=350)
        entry_id.pack(pady=(0,15))

        def guardar():
            nom = entry_nombre.get().strip()
            if not nom:
                messagebox.showwarning("Error", "El nombre es obligatorio", parent=win)
                return
            
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clientes (nombre, telefono, email, identificacion)
                    VALUES (?, ?, ?, ?)
                """, (nom, entry_tel.get().strip(), entry_email.get().strip(), entry_id.get().strip()))
                conn.commit()
            
            messagebox.showinfo("Éxito", "Cliente guardado.", parent=win)
            self.cargar_datos()
            win.destroy()

        ctk.CTkButton(win, text="Guardar Cliente", command=guardar, fg_color="#4F46E5").pack(pady=10)

    def eliminar_cliente(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un cliente para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este cliente? No podrás deshacerlo."):
            cliente_id = self.tabla.item(seleccion[0])["values"][0]
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                conn.commit()
            self.cargar_datos()
