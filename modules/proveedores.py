import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database

class ProveedoresTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_proveedores
        
        self.inputs = {}
        self.construir_tab()

    def construir_tab(self):
        # Panel Izquierdo (Formulario Proveedores)
        frame_form = tk.Frame(self.tab, bg="#FFFFFF", width=340, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        frame_form.pack_propagate(False)

        tk.Label(frame_form, text="NUEVO PROVEEDOR", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=(10, 5))

        grid_inputs = tk.Frame(frame_form, bg="#FFFFFF")
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
            tk.Label(grid_inputs, text=label_text, font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W, pady=(5, 1))
            border = tk.Frame(grid_inputs, bg="#E2E8F0")
            border.pack(fill=tk.X)
            entry = tk.Entry(border, font=("Segoe UI", 9), bg="#F8FAFC", relief=tk.FLAT, bd=0)
            entry.pack(fill=tk.X, padx=1, pady=1, ipady=3)
            self.inputs[key] = entry

        btn_guardar = tk.Button(frame_form, text="Guardar Proveedor", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=self.guardar_proveedor)
        btn_guardar.pack(fill=tk.X, padx=25, pady=20, ipady=7)

        # Panel Derecho (Tabla y Compras)
        frame_grid = tk.Frame(self.tab, bg="#F8FAFC")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=10)

        # Buscador
        frame_busca = tk.Frame(frame_grid, bg="#F8FAFC")
        frame_busca.pack(fill=tk.X, pady=(0, 10))
        tk.Label(frame_busca, text="Buscar:", font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg="#475569").pack(side=tk.LEFT, padx=(5, 10))
        self.entry_buscar = tk.Entry(frame_busca, font=("Segoe UI", 10))
        self.entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        btn_registrar_compra = tk.Button(frame_busca, text="Registrar Compra (Inventario)", font=("Segoe UI", 9, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=self.registrar_compra)
        btn_registrar_compra.pack(side=tk.RIGHT, padx=10, ipady=4, ipadx=10)

        # Tabla Proveedores
        columnas = ("id", "nombre", "contacto", "telefono", "email")
        self.tabla = ttk.Treeview(frame_grid, columns=columnas, show="headings")
        headers = [("ID", 40), ("Nombre", 180), ("Contacto", 120), ("Teléfono", 100), ("Email", 140)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill=tk.BOTH, expand=True)

        self.cargar_datos()

    def cargar_datos(self, filtro=""):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        proveedores = database.obtener_proveedores(filtro)
        for p in proveedores:
            self.tabla.insert("", tk.END, values=(p[0], p[1], p[2], p[3], p[4]))

    def guardar_proveedor(self):
        nombre = self.inputs["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        
        exito, msg = database.insertar_proveedor(
            nombre, self.inputs["contacto"].get(), self.inputs["telefono"].get(),
            self.inputs["email"].get(), self.inputs["direccion"].get(), self.inputs["notas"].get()
        )
        if exito:
            for entry in self.inputs.values():
                entry.delete(0, tk.END)
            self.cargar_datos(self.entry_buscar.get())
        else:
            messagebox.showerror("Error", msg)

    def registrar_compra(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor para registrar su compra.")
            return
        prov_id = int(self.tabla.item(seleccion[0])["values"][0])
        prov_nombre = self.tabla.item(seleccion[0])["values"][1]

        # Interfaz simplificada para comprar (se asume 1 producto por simplicidad o un form avanzado)
        # En una versión completa esto abriría una ventana grande de carrito de compras
        # Aquí pedimos producto y cantidad
        productos = database.obtener_productos()
        if not productos:
            return
            
        win_compra = tk.Toplevel(self.app.root)
        win_compra.title(f"Registrar Compra a: {prov_nombre}")
        win_compra.geometry("400x300")
        win_compra.grab_set()

        tk.Label(win_compra, text="Seleccionar Producto:").pack(pady=5)
        combo_prod = ttk.Combobox(win_compra, values=[f"{p[0]} - {p[2]}" for p in productos], state="readonly")
        combo_prod.pack(fill=tk.X, padx=20)
        
        tk.Label(win_compra, text="Cantidad comprada:").pack(pady=5)
        ent_cant = tk.Entry(win_compra)
        ent_cant.pack()
        
        tk.Label(win_compra, text="Costo unitario ($):").pack(pady=5)
        ent_costo = tk.Entry(win_compra)
        ent_costo.pack()

        def confirmar():
            try:
                cant = int(ent_cant.get())
                costo = float(ent_costo.get())
                p_id = int(combo_prod.get().split(" - ")[0])
                total = cant * costo
                
                detalles = [{"id": p_id, "cantidad": cant, "precio_unitario": costo}]
                exito, msg = database.registrar_compra(prov_id, 1, total, "Compra rápida", detalles) # Asume usuario_id=1
                
                if exito:
                    messagebox.showinfo("Éxito", msg)
                    self.app.inventario_controller.cargar_datos() # Actualiza stock visual
                    win_compra.destroy()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", "Verifica los datos ingresados.")

        tk.Button(win_compra, text="Confirmar Compra", bg="#10B981", fg="white", command=confirmar).pack(pady=20)
