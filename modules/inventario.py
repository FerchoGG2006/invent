import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import os
import shutil

class InventarioTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_inventario
        self.inputs = {}
        
        self.construir_tab()

    def construir_tab(self):
        # Panel Izquierdo (Formulario)
        frame_form = tk.Frame(self.tab, bg="#FFFFFF", width=340, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)
        frame_form.pack_propagate(False)

        tk.Label(frame_form, text="REGISTRAR PRODUCTO", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=(10, 5))

        # Grid frame for compact 2-column inputs
        grid_inputs = tk.Frame(frame_form, bg="#FFFFFF")
        grid_inputs.pack(fill=tk.X, padx=15, pady=(5, 5))

        grid_inputs.columnconfigure(0, weight=1)
        grid_inputs.columnconfigure(1, weight=1)

        campos = [
            ("Referencia *", "codigo", 0, 0),
            ("Nombre *", "nombre", 0, 1),
            ("Precio Costo", "costo", 1, 0),
            ("Precio Venta", "venta", 1, 1),
            ("Stock Inicial", "stock", 2, 0),
            ("Stock Mínimo", "min_stock", 2, 1)
        ]

        self.inputs = {}
        for label_text, key, row, col in campos:
            cell = tk.Frame(grid_inputs, bg="#FFFFFF")
            cell.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")

            tk.Label(cell, text=label_text, font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W, pady=(0, 1))
            border_frame = tk.Frame(cell, bg="#E2E8F0")
            border_frame.pack(fill=tk.X)
            entry = tk.Entry(border_frame, font=("Segoe UI", 9), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
            entry.pack(fill=tk.X, padx=1, pady=1, ipady=3)
            self.inputs[key] = entry

        self.inputs["min_stock"].insert(0, "3")

        # Campo para Imagen (No obligatorio)
        tk.Label(frame_form, text="Imagen del Producto", font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W, padx=20, pady=(5, 1))
        frame_img_sel = tk.Frame(frame_form, bg="#FFFFFF")
        frame_img_sel.pack(fill=tk.X, padx=20, pady=2)

        self.btn_select_img = tk.Button(frame_img_sel, text="Seleccionar Foto", font=("Segoe UI", 8, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, cursor="hand2", command=self.pos_seleccionar_imagen)
        self.btn_select_img.pack(side=tk.LEFT, ipady=3, ipadx=8)
        self.btn_select_img.bind("<Enter>", lambda e: self.btn_select_img.config(bg="#CBD5E1"))
        self.btn_select_img.bind("<Leave>", lambda e: self.btn_select_img.config(bg="#E2E8F0"))

        self.lbl_img_path = tk.Label(frame_img_sel, text="Sin foto", font=("Segoe UI", 8), bg="#FFFFFF", fg="#94A3B8", anchor=tk.W)
        self.lbl_img_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Recuadro Vista Previa Formulario
        frame_form_img_container = tk.Frame(frame_form, bg="#F8FAFC", width=280, height=120, bd=1, relief=tk.SOLID)
        frame_form_img_container.pack(pady=5, padx=20, fill=tk.X)
        frame_form_img_container.pack_propagate(False)
        self.lbl_img_preview = tk.Label(frame_form_img_container, text="Sin vista previa", font=("Segoe UI", 8, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_img_preview.pack(expand=True, fill=tk.BOTH)

        btn_guardar = tk.Button(frame_form, text="Guardar Producto", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0,
                                activebackground="#3730A3", activeforeground="white", cursor="hand2", command=self.guardar_producto)
        btn_guardar.pack(fill=tk.X, padx=25, pady=(5, 2), ipady=7)
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg="#4338CA"))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg="#4F46E5"))

        # Botón de Vaciar Base de Datos (Mantenimiento de pruebas)
        btn_reset = tk.Button(frame_form, text="Vaciar Todo (Reiniciar)", font=("Segoe UI", 8, "bold"), bg="#FFF5F5", fg="#EF4444", bd=0, cursor="hand2", command=self.app.reiniciar_sistema)
        btn_reset.pack(fill=tk.X, padx=25, pady=(2, 5), ipady=3)

        # Panel Derecho (Tabla y Buscador)
        frame_grid = tk.Frame(self.tab, bg="#F8FAFC")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)

        # Buscador
        frame_busca = tk.Frame(frame_grid, bg="#F8FAFC")
        frame_busca.pack(fill=tk.X, pady=(0, 15))
        tk.Label(frame_busca, text="Buscar:", font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg="#475569").pack(side=tk.LEFT, padx=(5, 10))

        busca_border = tk.Frame(frame_busca, bg="#E2E8F0")
        busca_border.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar = tk.Entry(busca_border, font=("Segoe UI", 10), bg="#FFFFFF", fg="#0F172A", relief=tk.FLAT, bd=0, insertbackground="#0F172A")
        self.entry_buscar.pack(fill=tk.X, padx=1, pady=1, ipady=5)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        # Botones de ajuste de stock
        frame_botones = tk.Frame(frame_grid, bg="#F8FAFC")
        frame_botones.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        btn_mas = tk.Button(frame_botones, text="+", font=("Segoe UI", 14, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, width=3, cursor="hand2", command=lambda: self.ajustar_stock(1))
        btn_mas.pack(pady=5, ipady=6)

        # Tabla
        columnas = ("id", "codigo", "nombre", "costo", "venta", "stock", "min_stock")
        self.tabla = ttk.Treeview(frame_grid, columns=columnas, show="headings")

        headers = [("ID", 40), ("Referencia", 100), ("Nombre", 220), ("Costo", 90), ("Venta", 90), ("Stock", 70), ("Mínimo", 70)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)

        self.tabla.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tabla.tag_configure("alerta", background="#FEF2F2", foreground="#991B1B")

        # Enlazar selección
        self.tabla.bind("<<TreeviewSelect>>", self.inv_on_producto_select)
        btn_menos = tk.Button(frame_botones, text="-", font=("Segoe UI", 14, "bold"), bg="#E2E8F0", fg="#1E293B", activebackground="#CBD5E1", bd=0, width=3, cursor="hand2", command=lambda: self.ajustar_stock(-1))
        btn_menos.pack(pady=5, ipady=6)

        btn_mas.bind("<Enter>", lambda e: btn_mas.config(bg="#CBD5E1"))
        btn_mas.bind("<Leave>", lambda e: btn_mas.config(bg="#E2E8F0"))
        btn_menos.bind("<Enter>", lambda e: btn_menos.config(bg="#CBD5E1"))
        btn_menos.bind("<Leave>", lambda e: btn_menos.config(bg="#E2E8F0"))

        # Recuadro Imagen de Producto Seleccionado
        tk.Label(frame_botones, text="Foto:", font=("Segoe UI", 9, "bold"), bg="#F8FAFC", fg="#64748B").pack(pady=(15, 2))
        frame_inv_img_container = tk.Frame(frame_botones, bg="#FFFFFF", width=240, height=200, bd=1, relief=tk.SOLID)
        frame_inv_img_container.pack(pady=2, fill=tk.X)
        frame_inv_img_container.pack_propagate(False)
        self.lbl_inv_foto_preview = tk.Label(frame_inv_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#94A3B8", compound="center")
        self.lbl_inv_foto_preview.pack(expand=True, fill=tk.BOTH)

        # Setup keyboard shortcuts
        for entry in self.inputs.values():
            entry.bind("<Return>", lambda e: self.guardar_producto())

    def pos_seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen del Producto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.gif")]
        )
        if ruta:
            self.app.imagen_ruta_form = ruta
            nombre_archivo = ruta.split("/")[-1]
            self.lbl_img_path.config(text=nombre_archivo, fg="#0F172A")
            self.app.actualizar_vista_previa_label(self.lbl_img_preview, ruta, (270, 110))

    def inv_on_producto_select(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.lbl_inv_foto_preview.config(image="", text="Sin foto")
            self.lbl_inv_foto_preview.image = None
            return
        valores = self.tabla.item(seleccion[0])["values"]
        p_id = int(valores[0])

        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT imagen_ruta FROM productos WHERE id = ?", (p_id,))
            res = cursor.fetchone()
            if res and res[0]:
                self.app.actualizar_vista_previa_label(self.lbl_inv_foto_preview, res[0], (230, 190))
            else:
                self.lbl_inv_foto_preview.config(image="", text="Sin foto")
                self.lbl_inv_foto_preview.image = None

    def cargar_datos(self, filtro=""):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        productos = database.obtener_productos(filtro)
        for p in productos:
            costo_f = f"${p[4]:,.0f}"
            venta_f = f"${p[5]:,.0f}"
            valores = (p[0], p[1] or "---", p[2], costo_f, venta_f, p[6], p[7])
            tag = "alerta" if p[6] <= p[7] else ""
            self.tabla.insert("", tk.END, values=valores, tags=(tag,))
        self.app.pos_actualizar_alertas_pestaña()
        self.lbl_inv_foto_preview.config(image="", text="Sin foto")
        self.lbl_inv_foto_preview.image = None

    def guardar_producto(self):
        codigo = self.inputs["codigo"].get().strip()
        nombre = self.inputs["nombre"].get().strip()

        if not codigo:
            messagebox.showwarning("Falta información", "La Referencia del producto es obligatoria.")
            return
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre del producto es obligatorio.")
            return

        try:
            costo = float(self.inputs["costo"].get() or 0)
            venta = float(self.inputs["venta"].get() or 0)
            stock = int(self.inputs["stock"].get() or 0)
            min_stock = int(self.inputs["min_stock"].get() or 3)
        except ValueError:
            messagebox.showerror("Error de formato", "Los precios y el stock deben ser números válidos.")
            return

        # Copiar imagen a directorio local antes de guardar en DB
        imagen_destino = ""
        if self.app.imagen_ruta_form and os.path.exists(self.app.imagen_ruta_form):
            try:
                extension = os.path.splitext(self.app.imagen_ruta_form)[1]
                nombre_seguro = "".join([c for c in codigo if c.isalnum()])
                nombre_archivo = f"{nombre_seguro}{extension}"

                img_dir = self.app.obtener_ruta_imagenes()
                imagen_destino = os.path.join(img_dir, nombre_archivo)

                if os.path.abspath(self.app.imagen_ruta_form) != os.path.abspath(imagen_destino):
                    shutil.copy2(self.app.imagen_ruta_form, imagen_destino)
            except Exception:
                pass

        exito = database.insertar_producto(codigo, nombre, "", costo, venta, stock, min_stock, imagen_destino)
        if exito:
            self.cargar_datos(self.entry_buscar.get())
            for entry in self.inputs.values():
                entry.delete(0, tk.END)
            self.inputs["min_stock"].insert(0, "3")
            self.app.imagen_ruta_form = ""
            self.lbl_img_path.config(text="Sin foto", fg="#94A3B8")
            self.lbl_img_preview.config(image="", text="Sin vista previa")
            self.lbl_img_preview.image = None
            self.inputs["codigo"].focus()
        else:
            messagebox.showerror("Error", "La Referencia ya está registrada.")
        self.app.pos_actualizar_alertas_pestaña()

    def ajustar_stock(self, cantidad):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla primero.")
            return

        producto_id = self.tabla.item(seleccion[0])["values"][0]
        database.modificar_stock(producto_id, cantidad)
        self.cargar_datos(self.entry_buscar.get())
        self.app.pos_actualizar_alertas_pestaña()
