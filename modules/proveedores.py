import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import database

class ProveedoresTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_proveedores
        
        self.inputs = {}
        self.editando_id = None  # Para saber si estamos editando un proveedor
        self.construir_tab()

    def construir_tab(self):
        # Panel Izquierdo (Formulario Proveedores)
        frame_form = ctk.CTkFrame(self.tab, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, width=340, corner_radius=12)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        frame_form.pack_propagate(False)

        self.lbl_titulo_form = ctk.CTkLabel(frame_form, text="NUEVO PROVEEDOR", font=("Segoe UI", 12, "bold"), text_color="#0F172A")
        self.lbl_titulo_form.pack(pady=(15, 5))

        grid_inputs = ctk.CTkFrame(frame_form, fg_color="transparent")
        grid_inputs.pack(fill=tk.X, padx=15, pady=5)

        campos = [
            ("Empresa / Nombre *", "nombre"),
            ("Contacto", "contacto"),
            ("Teléfono", "telefono"),
            ("Email", "email"),
            ("Dirección", "direccion"),
            ("Notas", "notas")
        ]

        self.inputs = {}
        for i, (label_text, key) in enumerate(campos):
            ctk.CTkLabel(grid_inputs, text=label_text, font=("Segoe UI", 8, "bold"), text_color="#64748B").pack(anchor=tk.W, pady=(5, 1))
            entry = ctk.CTkEntry(grid_inputs, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28, corner_radius=5)
            entry.pack(fill=tk.X, pady=1)
            self.inputs[key] = entry

        # Botones de acción del formulario
        frame_btns_form = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_btns_form.pack(fill=tk.X, padx=25, pady=(15, 5))

        self.btn_guardar = ctk.CTkButton(frame_btns_form, text="Guardar Proveedor", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=35, corner_radius=8, command=self.guardar_proveedor)
        self.btn_guardar.pack(fill=tk.X, pady=(0, 5))

        self.btn_cancelar_edicion = ctk.CTkButton(frame_btns_form, text="Cancelar Edición", font=("Segoe UI", 9, "bold"), fg_color="#94A3B8", hover_color="#64748B", text_color="white", height=30, corner_radius=8, command=self.cancelar_edicion)
        self.btn_cancelar_edicion.pack(fill=tk.X)
        self.btn_cancelar_edicion.pack_forget()  # Ocultar inicialmente

        # Panel Derecho (Tabla y Acciones)
        frame_grid = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        # Buscador y botones de acción
        frame_busca = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_busca.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(frame_busca, text="Buscar:", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(side=tk.LEFT, padx=(5, 10))

        self.entry_buscar = ctk.CTkEntry(frame_busca, font=("Segoe UI", 10), fg_color="#FFFFFF", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6)
        self.entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        btn_eliminar = ctk.CTkButton(frame_busca, text="Eliminar", font=("Segoe UI", 9, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=32, width=90, corner_radius=6, command=self.eliminar_proveedor)
        btn_eliminar.pack(side=tk.RIGHT, padx=5)

        btn_editar = ctk.CTkButton(frame_busca, text="Editar", font=("Segoe UI", 9, "bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", height=32, width=80, corner_radius=6, command=self.editar_proveedor)
        btn_editar.pack(side=tk.RIGHT, padx=5)

        btn_registrar_compra = ctk.CTkButton(frame_busca, text="Registrar Compra", font=("Segoe UI", 9, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=32, width=130, corner_radius=6, command=self.registrar_compra)
        btn_registrar_compra.pack(side=tk.RIGHT, padx=5)

        # Tabla Proveedores
        frame_tabla = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columnas = ("id", "nombre", "contacto", "telefono", "email", "direccion")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        headers = [("ID", 40), ("Nombre", 160), ("Contacto", 120), ("Teléfono", 100), ("Email", 140), ("Dirección", 140)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col == "id" else tk.W)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        # Doble clic para editar
        self.tabla.bind("<Double-1>", lambda e: self.editar_proveedor())

        self.cargar_datos()

        # Vincular Enter en los campos de entrada
        for entry in self.inputs.values():
            entry.bind("<Return>", lambda e: self.guardar_proveedor())

    def cargar_datos(self, filtro=""):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        proveedores = database.obtener_proveedores(filtro)
        for p in proveedores:
            # p = (id, nombre, contacto, telefono, email, direccion, notas)
            self.tabla.insert("", tk.END, values=(p[0], p[1], p[2] or "", p[3] or "", p[4] or "", p[5] or ""))

    def limpiar_formulario(self):
        for entry in self.inputs.values():
            entry.delete(0, tk.END)
        self.editando_id = None
        self.lbl_titulo_form.configure(text="NUEVO PROVEEDOR")
        self.btn_guardar.configure(text="Guardar Proveedor")
        self.btn_cancelar_edicion.pack_forget()

    def cancelar_edicion(self):
        self.limpiar_formulario()

    def guardar_proveedor(self):
        nombre = self.inputs["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        
        contacto = self.inputs["contacto"].get().strip()
        telefono = self.inputs["telefono"].get().strip()
        email = self.inputs["email"].get().strip()
        direccion = self.inputs["direccion"].get().strip()
        notas = self.inputs["notas"].get().strip()

        if self.editando_id:
            # Actualizar proveedor existente
            exito, msg = database.actualizar_proveedor(
                self.editando_id, nombre, contacto, telefono, email, direccion, notas
            )
            if exito:
                self.limpiar_formulario()
                self.cargar_datos(self.entry_buscar.get())
                # Actualizar combos de inventario para reflejar cambio de nombre
                if hasattr(self.app, 'inventario_controller'):
                    self.app.inventario_controller.actualizar_combos()
            else:
                messagebox.showerror("Error", msg)
        else:
            # Insertar nuevo proveedor
            exito, msg = database.insertar_proveedor(
                nombre, contacto, telefono, email, direccion, notas
            )
            if exito:
                self.limpiar_formulario()
                self.cargar_datos(self.entry_buscar.get())
                # Actualizar combos de inventario para que el nuevo proveedor aparezca
                if hasattr(self.app, 'inventario_controller'):
                    self.app.inventario_controller.actualizar_combos()
            else:
                messagebox.showerror("Error", msg)

    def editar_proveedor(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor para editar.")
            return
        
        valores = self.tabla.item(seleccion[0])["values"]
        prov_id = int(valores[0])
        
        # Obtener datos completos del proveedor (incluyendo notas)
        proveedores = database.obtener_proveedores()
        proveedor_data = None
        for p in proveedores:
            if p[0] == prov_id:
                proveedor_data = p
                break
        
        if not proveedor_data:
            return

        # Rellenar formulario con los datos del proveedor
        self.limpiar_formulario()
        self.editando_id = prov_id
        
        campos_map = {
            "nombre": proveedor_data[1] or "",
            "contacto": proveedor_data[2] or "",
            "telefono": proveedor_data[3] or "",
            "email": proveedor_data[4] or "",
            "direccion": proveedor_data[5] or "",
            "notas": proveedor_data[6] or ""
        }
        
        for key, valor in campos_map.items():
            self.inputs[key].insert(0, valor)
        
        self.lbl_titulo_form.configure(text="EDITAR PROVEEDOR")
        self.btn_guardar.configure(text="Actualizar Proveedor")
        self.btn_cancelar_edicion.pack(fill=tk.X)

    def eliminar_proveedor(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor para eliminar.")
            return
        
        prov_id = int(self.tabla.item(seleccion[0])["values"][0])
        prov_nombre = self.tabla.item(seleccion[0])["values"][1]
        
        if messagebox.askyesno("Eliminar Proveedor", f"¿Estás seguro de eliminar al proveedor '{prov_nombre}'?\n\nLos productos asociados a este proveedor NO se eliminarán, pero perderán la referencia al proveedor."):
            exito, msg = database.eliminar_proveedor(prov_id)
            if exito:
                self.limpiar_formulario()
                self.cargar_datos(self.entry_buscar.get())
                # Actualizar combos de inventario
                if hasattr(self.app, 'inventario_controller'):
                    self.app.inventario_controller.actualizar_combos()
            else:
                messagebox.showerror("Error", msg)

    def registrar_compra(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor para registrar su compra.")
            return
        prov_id = int(self.tabla.item(seleccion[0])["values"][0])
        prov_nombre = self.tabla.item(seleccion[0])["values"][1]

        productos = database.obtener_productos()
        if not productos:
            messagebox.showinfo("Sin Productos", "No hay productos registrados. Primero registra productos en el Inventario.")
            return
            
        win_compra = ctk.CTkToplevel(self.app.root)
        win_compra.title(f"Registrar Compra a: {prov_nombre}")
        win_compra.geometry("420x350")
        win_compra.grab_set()
        win_compra.resizable(False, False)

        ctk.CTkLabel(win_compra, text=f"Compra a: {prov_nombre}", font=("Segoe UI", 13, "bold"), text_color="#0F172A").pack(pady=(15, 10))

        frame_campos = ctk.CTkFrame(win_compra, fg_color="transparent")
        frame_campos.pack(fill=tk.X, padx=25, pady=5)

        ctk.CTkLabel(frame_campos, text="Producto:", font=("Segoe UI", 9, "bold"), text_color="#64748B").pack(anchor=tk.W, pady=(5, 2))
        combo_prod = ctk.CTkComboBox(frame_campos, values=[f"{p[0]} - {p[2]}" for p in productos], state="readonly", font=("Segoe UI", 10), height=32, corner_radius=6)
        combo_prod.pack(fill=tk.X)
        combo_prod.set("Seleccionar producto...")
        
        ctk.CTkLabel(frame_campos, text="Cantidad comprada:", font=("Segoe UI", 9, "bold"), text_color="#64748B").pack(anchor=tk.W, pady=(10, 2))
        ent_cant = ctk.CTkEntry(frame_campos, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="Ej: 50")
        ent_cant.pack(fill=tk.X)
        
        ctk.CTkLabel(frame_campos, text="Costo unitario ($):", font=("Segoe UI", 9, "bold"), text_color="#64748B").pack(anchor=tk.W, pady=(10, 2))
        ent_costo = ctk.CTkEntry(frame_campos, font=("Segoe UI", 10), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6, placeholder_text="Ej: 150.00")
        ent_costo.pack(fill=tk.X)

        def confirmar():
            try:
                sel = combo_prod.get()
                if not sel or "Seleccionar" in sel:
                    messagebox.showwarning("Atención", "Selecciona un producto.", parent=win_compra)
                    return
                cant = int(ent_cant.get())
                costo = float(ent_costo.get())
                p_id = int(sel.split(" - ")[0])
                total = cant * costo
                
                detalles = [{"id": p_id, "cantidad": cant, "precio_unitario": costo}]
                usuario_id = self.app.current_user["id"] if self.app.current_user else 1
                exito, msg = database.registrar_compra(prov_id, usuario_id, total, "Compra rápida", detalles)
                
                if exito:
                    messagebox.showinfo("Éxito", msg, parent=win_compra)
                    self.app.inventario_controller.cargar_datos(self.app.inventario_controller.entry_buscar.get())
                    win_compra.destroy()
                else:
                    messagebox.showerror("Error", msg, parent=win_compra)
            except ValueError:
                messagebox.showerror("Error", "Verifica que la cantidad y costo sean números válidos.", parent=win_compra)

        ctk.CTkButton(win_compra, text="Confirmar Compra", font=("Segoe UI", 10, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=38, corner_radius=8, command=confirmar).pack(fill=tk.X, padx=25, pady=(20, 15))
