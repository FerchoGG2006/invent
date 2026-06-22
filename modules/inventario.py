import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import customtkinter as ctk
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
        frame_form = ctk.CTkFrame(self.tab, fg_color=("#FFFFFF", "#1E293B"), border_color=("#E2E8F0", "#334155"), border_width=1, width=340, corner_radius=12)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        frame_form.pack_propagate(False)

        ctk.CTkLabel(frame_form, text="REGISTRAR PRODUCTO", font=("Segoe UI", 12, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(pady=(15, 5))

        # Grid frame for compact 2-column inputs
        grid_inputs = ctk.CTkFrame(frame_form, fg_color="transparent")
        grid_inputs.pack(fill=tk.X, padx=15, pady=(5, 5))

        grid_inputs.columnconfigure(0, weight=1)
        grid_inputs.columnconfigure(1, weight=1)

        campos = [
            ("Referencia *", "codigo", 0, 0),
            ("Nombre *", "nombre", 0, 1),
            ("Categoría", "categoria", 1, 0),
            ("Proveedor", "proveedor_id", 1, 1),
            ("Precio Costo", "costo", 2, 0),
            ("Precio Venta", "venta", 2, 1),
            ("Stock Inicial", "stock", 3, 0),
            ("Stock Mínimo", "min_stock", 3, 1),
            ("Unidad Medida", "unidad_medida", 4, 0)
        ]

        self.inputs = {}
        for label_text, key, row, col in campos:
            cell = ctk.CTkFrame(grid_inputs, fg_color="transparent")
            cell.grid(row=row, column=col, padx=4, pady=3, sticky="nsew")

            ctk.CTkLabel(cell, text=label_text, font=("Segoe UI", 8, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(0, 1))
            
            if key in ["categoria", "proveedor_id", "unidad_medida"]:
                combo = ctk.CTkComboBox(cell, font=("Segoe UI", 9), height=28, corner_radius=5, state="readonly")
                combo.pack(fill=tk.X, pady=1)
                self.inputs[key] = combo
            else:
                entry = ctk.CTkEntry(cell, font=("Segoe UI", 10), fg_color=("#F8FAFC", ("#0F172A", "#F8FAFC")), text_color=("#0F172A", "#F8FAFC"), border_color=("#D1D5DB", "#475569"), height=28, corner_radius=5)
                entry.pack(fill=tk.X, pady=1)
                self.inputs[key] = entry

        self.inputs["min_stock"].insert(0, "3")
        self.inputs["unidad_medida"].configure(values=["Unidad", "Kg", "Litro", "Metro", "Caja"])
        self.inputs["unidad_medida"].set("Unidad")
        self.inputs["categoria"].set("Seleccionar...")
        self.inputs["proveedor_id"].set("Seleccionar...")
        self.actualizar_combos()

        # Campo para Imagen (No obligatorio)
        ctk.CTkLabel(frame_form, text="Imagen del Producto", font=("Segoe UI", 8, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, padx=20, pady=(5, 1))
        frame_img_sel = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_img_sel.pack(fill=tk.X, padx=20, pady=2)

        self.btn_select_img = ctk.CTkButton(frame_img_sel, text="Seleccionar Foto", font=("Segoe UI", 8, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1F2937", height=26, width=110, corner_radius=5, command=self.pos_seleccionar_imagen)
        self.btn_select_img.pack(side=tk.LEFT)

        self.lbl_img_path = ctk.CTkLabel(frame_img_sel, text="Sin foto", font=("Segoe UI", 8), text_color="#94A3B8", anchor=tk.W)
        self.lbl_img_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Recuadro Vista Previa Formulario
        frame_form_img_container = ctk.CTkFrame(frame_form, fg_color=("#F8FAFC", ("#0F172A", "#F8FAFC")), border_color=("#D1D5DB", "#475569"), border_width=1, height=90, corner_radius=6)
        frame_form_img_container.pack(pady=5, padx=20, fill=tk.X)
        frame_form_img_container.pack_propagate(False)
        self.lbl_img_preview = tk.Label(frame_form_img_container, text="Sin vista previa", font=("Segoe UI", 8, "italic"), bg=("#F8FAFC", ("#0F172A", "#F8FAFC")), fg="#94A3B8", compound="center")
        self.lbl_img_preview.pack(expand=True, fill=tk.BOTH)

        btn_guardar = ctk.CTkButton(frame_form, text="Guardar Producto", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=35, corner_radius=8, command=self.guardar_producto)
        btn_guardar.pack(fill=tk.X, padx=25, pady=(5, 10))

        # Panel Derecho (Tabla y Buscador)
        frame_grid = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        # Buscador y botones de acción
        frame_busca = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_busca.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(frame_busca, text="Buscar:", font=("Segoe UI", 10, "bold"), text_color=("#475569", "#CBD5E1")).pack(side=tk.LEFT, padx=(5, 10))

        self.entry_buscar = ctk.CTkEntry(frame_busca, font=("Segoe UI", 10), fg_color=("#FFFFFF", "#1E293B"), text_color=("#0F172A", "#F8FAFC"), border_color=("#D1D5DB", "#475569"), height=32, corner_radius=6)
        self.entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        btn_eliminar = ctk.CTkButton(frame_busca, text="Eliminar Producto", font=("Segoe UI", 9, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=32, width=120, corner_radius=6, command=self.eliminar_producto)
        btn_eliminar.pack(side=tk.RIGHT, padx=5)

        btn_merma = ctk.CTkButton(frame_busca, text="Registrar Merma", font=("Segoe UI", 9, "bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", height=32, width=110, corner_radius=6, command=self.registrar_merma)
        btn_merma.pack(side=tk.RIGHT, padx=5)

        # Botones de ajuste de stock
        frame_botones = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_botones.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        btn_mas = ctk.CTkButton(frame_botones, text="+", font=("Segoe UI", 14, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1E293B", width=40, height=40, corner_radius=6, command=lambda: self.ajustar_stock(1))
        btn_mas.pack(pady=5)

        # Tabla (Treeview dentro del frame)
        frame_tabla = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        columnas = ("id", "codigo", "nombre", "categoria", "costo", "venta", "margen", "stock", "min_stock", "unidad")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        headers = [("ID", 30), ("Ref", 70), ("Nombre", 160), ("Categoría", 90), ("Costo", 60), ("Venta", 60), ("Margen %", 70), ("Stock", 50), ("Mínimo", 50), ("Unidad", 60)]
        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)

        self.tabla.pack(fill=tk.BOTH, expand=True)
        self.tabla.tag_configure("alerta", background="#FEF2F2", foreground="#991B1B")

        self.tabla.bind("<<TreeviewSelect>>", self.inv_on_producto_select)
        self.tabla.bind("<Double-1>", self.inv_on_double_click)
        
        btn_menos = ctk.CTkButton(frame_botones, text="-", font=("Segoe UI", 14, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1E293B", width=40, height=40, corner_radius=6, command=lambda: self.ajustar_stock(-1))
        btn_menos.pack(pady=5)

        # Recuadro Imagen de Producto Seleccionado
        ctk.CTkLabel(frame_botones, text="Foto:", font=("Segoe UI", 9, "bold"), text_color=("#64748B", "#94A3B8")).pack(pady=(15, 2))
        
        frame_inv_img_container = ctk.CTkFrame(frame_botones, fg_color=("#FFFFFF", "#1E293B"), border_color=("#D1D5DB", "#475569"), border_width=1, width=120, height=120, corner_radius=6)
        frame_inv_img_container.pack(pady=2, fill=tk.X)
        frame_inv_img_container.pack_propagate(False)
        
        self.lbl_inv_foto_preview = tk.Label(frame_inv_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg=("#FFFFFF", "#1E293B"), fg="#94A3B8", compound="center")
        self.lbl_inv_foto_preview.pack(expand=True, fill=tk.BOTH)

        for entry in self.inputs.values():
            if not isinstance(entry, ctk.CTkComboBox):
                entry.bind("<Return>", lambda e: self.guardar_producto())

    def actualizar_combos(self):
        cat = database.obtener_categorias()
        prov = database.obtener_proveedores()
        
        categorias_nombres = [c[1] for c in cat]
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT categoria FROM productos WHERE categoria IS NOT NULL AND categoria != ''")
            for row in cursor.fetchall():
                if row[0] not in categorias_nombres:
                    categorias_nombres.append(row[0])
                    
        self.inputs["categoria"].configure(values=sorted(categorias_nombres))
        self.inputs["proveedor_id"].configure(values=[f"{p[0]} - {p[1]}" for p in prov] if prov else ["Sin proveedores"])

    def pos_seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen del Producto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.gif")]
        )
        if ruta:
            self.app.imagen_ruta_form = ruta
            nombre_archivo = ruta.split("/")[-1]
            self.lbl_img_path.configure(text=nombre_archivo, text_color=("#0F172A", "#F8FAFC"))
            self.app.actualizar_vista_previa_label(self.lbl_img_preview, ruta, (270, 85))

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
                self.app.actualizar_vista_previa_label(self.lbl_inv_foto_preview, res[0], (110, 110))
            else:
                self.lbl_inv_foto_preview.config(image="", text="Sin foto")
                self.lbl_inv_foto_preview.image = None

    def inv_on_double_click(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        p_id = int(self.tabla.item(seleccion[0])["values"][0])
        
        producto = database.obtener_producto_por_id(p_id)
        if not producto:
            messagebox.showerror("Error", "No se encontró el producto en la base de datos.")
            return
            
        # producto = (id, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, imagen_ruta, unidad_medida, proveedor_id, margen_utilidad)
        
        win = ctk.CTkToplevel(self.app.root)
        win.title(f"Editar Producto: {producto[2]}")
        win.geometry("500x550")
        win.grab_set()
        
        # Centrar
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (550 // 2)
        win.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkScrollableFrame(win, fg_color="transparent")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="✏️ Editar Producto", font=("Segoe UI", 16, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(pady=(0, 15))
        
        # Entradas
        inputs = {}
        
        def add_entry(label_text, default_val):
            ctk.CTkLabel(frame, text=label_text, font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
            entry = ctk.CTkEntry(frame, font=("Segoe UI", 11), height=30, corner_radius=6)
            entry.pack(fill=tk.X, pady=(0, 5))
            entry.insert(0, str(default_val) if default_val is not None else "")
            return entry
            
        inputs["codigo"] = add_entry("Referencia / Código de Barras", producto[1])
        inputs["nombre"] = add_entry("Nombre del Producto *", producto[2])
        
        # Categoría
        ctk.CTkLabel(frame, text="Categoría", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_cat = ctk.CTkComboBox(frame, values=self.inputs["categoria"].cget("values"), font=("Segoe UI", 11), height=30, corner_radius=6)
        combo_cat.pack(fill=tk.X, pady=(0, 5))
        combo_cat.set(producto[3] if producto[3] else "Seleccionar...")
        inputs["categoria"] = combo_cat
        
        # Proveedor
        ctk.CTkLabel(frame, text="Proveedor", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_prov = ctk.CTkComboBox(frame, values=self.inputs["proveedor_id"].cget("values"), font=("Segoe UI", 11), height=30, corner_radius=6)
        combo_prov.pack(fill=tk.X, pady=(0, 5))
        
        prov_val = "Seleccionar..."
        if producto[10]: # proveedor_id
            for p_opt in combo_prov.cget("values"):
                if str(p_opt).startswith(f"{producto[10]} -"):
                    prov_val = p_opt
                    break
        combo_prov.set(prov_val)
        inputs["proveedor"] = combo_prov
        
        # Precios
        frame_precios = ctk.CTkFrame(frame, fg_color="transparent")
        frame_precios.pack(fill=tk.X, pady=5)
        
        f1 = ctk.CTkFrame(frame_precios, fg_color="transparent"); f1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkLabel(f1, text="Costo ($)", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["costo"] = ctk.CTkEntry(f1, font=("Segoe UI", 11), height=30, corner_radius=6)
        inputs["costo"].pack(fill=tk.X); inputs["costo"].insert(0, str(producto[4]))
        
        f2 = ctk.CTkFrame(frame_precios, fg_color="transparent"); f2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ctk.CTkLabel(f2, text="Venta ($) *", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["venta"] = ctk.CTkEntry(f2, font=("Segoe UI", 11), height=30, corner_radius=6)
        inputs["venta"].pack(fill=tk.X); inputs["venta"].insert(0, str(producto[5]))
        
        # Stock
        frame_stock = ctk.CTkFrame(frame, fg_color="transparent")
        frame_stock.pack(fill=tk.X, pady=5)
        
        f3 = ctk.CTkFrame(frame_stock, fg_color="transparent"); f3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkLabel(f3, text="Stock Actual", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["stock"] = ctk.CTkEntry(f3, font=("Segoe UI", 11), height=30, corner_radius=6)
        inputs["stock"].pack(fill=tk.X); inputs["stock"].insert(0, str(producto[6]))
        
        f4 = ctk.CTkFrame(frame_stock, fg_color="transparent"); f4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ctk.CTkLabel(f4, text="Stock Mín.", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["min_stock"] = ctk.CTkEntry(f4, font=("Segoe UI", 11), height=30, corner_radius=6)
        inputs["min_stock"].pack(fill=tk.X); inputs["min_stock"].insert(0, str(producto[7]))
        
        # Unidad de medida
        ctk.CTkLabel(frame, text="Unidad de Medida", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_uni = ctk.CTkComboBox(frame, values=["Unidad", "Kg", "Litro", "Metro", "Caja", "Paquete", "Servicio"], font=("Segoe UI", 11), height=30, corner_radius=6)
        combo_uni.pack(fill=tk.X, pady=(0, 5))
        combo_uni.set(producto[9] if producto[9] else "Unidad")
        inputs["unidad"] = combo_uni
        
        # Imagen
        self.ruta_img_edit = None
        def seleccionar_img_edit():
            ruta = filedialog.askopenfilename(title="Seleccionar Imagen", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.gif")], parent=win)
            if ruta:
                self.ruta_img_edit = ruta
                lbl_img_status.configure(text=ruta.split("/")[-1], text_color="#10B981")
                
        frame_img = ctk.CTkFrame(frame, fg_color="transparent")
        frame_img.pack(fill=tk.X, pady=(10, 20))
        btn_img = ctk.CTkButton(frame_img, text="🖼️ Cambiar Imagen", command=seleccionar_img_edit, fg_color="#F1F5F9", text_color=("#475569", "#CBD5E1"), hover_color=("#E2E8F0", "#334155"))
        btn_img.pack(side=tk.LEFT)
        lbl_img_status = ctk.CTkLabel(frame_img, text="Mantener actual", font=("Segoe UI", 9), text_color="#94A3B8")
        lbl_img_status.pack(side=tk.LEFT, padx=10)
        
        def guardar_cambios():
            codigo = inputs["codigo"].get().strip()
            nombre = inputs["nombre"].get().strip()
            categoria = inputs["categoria"].get().strip()
            if categoria == "Seleccionar...": categoria = ""
            proveedor_sel = inputs["proveedor"].get().strip()
            unidad = inputs["unidad"].get().strip()
            
            if not nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.", parent=win)
                return
                
            prov_id = None
            if proveedor_sel and " - " in proveedor_sel:
                prov_id = int(proveedor_sel.split(" - ")[0])
                
            try:
                costo = float(inputs["costo"].get() or 0)
                venta = float(inputs["venta"].get() or 0)
                stock = int(inputs["stock"].get() or 0)
                min_s = int(inputs["min_stock"].get() or 0)
            except ValueError:
                messagebox.showerror("Error", "Precios y stock deben ser numéricos.", parent=win)
                return
                
            imagen_destino = None
            if self.ruta_img_edit and os.path.exists(self.ruta_img_edit):
                try:
                    import shutil
                    extension = os.path.splitext(self.ruta_img_edit)[1]
                    nombre_seguro = "".join([c for c in (codigo or nombre) if c.isalnum()])
                    nombre_archivo = f"{nombre_seguro}_edit{extension}"
                    img_dir = self.app.obtener_ruta_imagenes()
                    imagen_destino = os.path.join(img_dir, nombre_archivo)
                    if os.path.abspath(self.ruta_img_edit) != os.path.abspath(imagen_destino):
                        shutil.copy2(self.ruta_img_edit, imagen_destino)
                except Exception:
                    pass
            
            exito, msg = database.actualizar_producto_completo(p_id, codigo, nombre, categoria, costo, venta, stock, min_s, imagen_destino, unidad, prov_id)
            if exito:
                messagebox.showinfo("Éxito", "Producto actualizado.", parent=win)
                self.cargar_datos(self.entry_buscar.get())
                win.destroy()
            else:
                messagebox.showerror("Error", msg, parent=win)
                
        btn_guardar = ctk.CTkButton(frame, text="Guardar Cambios", font=("Segoe UI", 11, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=35, corner_radius=6, command=guardar_cambios)
        btn_guardar.pack(fill=tk.X, pady=10)

    def cargar_datos(self, filtro=""):
        self.actualizar_combos()
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        productos = database.obtener_productos(filtro)
        for p in productos:
            margen_str = f"{p[8]:.1f}%" if p[8] else "0.0%"
            costo_f = f"${p[4]:,.0f}"
            venta_f = f"${p[5]:,.0f}"
            valores = (p[0], p[1] or "---", p[2], p[3] or "", costo_f, venta_f, margen_str, p[6], p[7], p[9] or "Unidad")
            tag = "alerta" if p[6] <= p[7] else ""
            self.tabla.insert("", tk.END, values=valores, tags=(tag,))
        self.lbl_inv_foto_preview.config(image="", text="Sin foto")
        self.lbl_inv_foto_preview.image = None

    def guardar_producto(self):
        codigo = self.inputs["codigo"].get().strip()
        nombre = self.inputs["nombre"].get().strip()
        categoria = self.inputs["categoria"].get().strip()
        if categoria == "Seleccionar...":
            categoria = ""
        proveedor_sel = self.inputs["proveedor_id"].get().strip()
        unidad_medida = self.inputs["unidad_medida"].get().strip()

        if not codigo or not nombre:
            messagebox.showwarning("Falta información", "La Referencia y Nombre son obligatorios.")
            return

        proveedor_id = None
        if proveedor_sel and " - " in proveedor_sel:
            proveedor_id = int(proveedor_sel.split(" - ")[0])

        try:
            costo = float(self.inputs["costo"].get() or 0)
            venta = float(self.inputs["venta"].get() or 0)
            stock = int(self.inputs["stock"].get() or 0)
            min_stock = int(self.inputs["min_stock"].get() or 3)
        except ValueError:
            messagebox.showerror("Error", "Los precios y stock deben ser números válidos.")
            return

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

        exito = database.insertar_producto(codigo, nombre, categoria, costo, venta, stock, min_stock, imagen_destino, unidad_medida, proveedor_id)
        if exito:
            self.cargar_datos(self.entry_buscar.get())
            for key, entry in self.inputs.items():
                if not isinstance(entry, ctk.CTkComboBox):
                    entry.delete(0, tk.END)
                else:
                    if key == "unidad_medida":
                        entry.set("Unidad")
                    else:
                        entry.set("Seleccionar...")
            self.inputs["min_stock"].insert(0, "3")
            self.app.imagen_ruta_form = ""
            self.lbl_img_path.configure(text="Sin foto", text_color="#94A3B8")
            self.lbl_img_preview.config(image="", text="Sin vista previa")
            self.lbl_img_preview.image = None
            self.inputs["codigo"].focus()
        else:
            messagebox.showerror("Error", "La Referencia ya está registrada.")

    def eliminar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto a eliminar.")
            return
        
        p_id = int(self.tabla.item(seleccion[0])["values"][0])
        p_nombre = self.tabla.item(seleccion[0])["values"][2]
        
        if messagebox.askyesno("Eliminar", f"¿Estás seguro de eliminar '{p_nombre}'?"):
            exito, msg = database.eliminar_producto(p_id)
            if exito:
                self.cargar_datos(self.entry_buscar.get())
            else:
                messagebox.showerror("Error", msg)

    def registrar_merma(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto para registrar merma.")
            return
        
        p_id = int(self.tabla.item(seleccion[0])["values"][0])
        p_nombre = self.tabla.item(seleccion[0])["values"][2]
        
        cant = simpledialog.askinteger("Merma", f"Cantidad a descontar de '{p_nombre}' por merma:")
        if cant and cant > 0:
            motivo = simpledialog.askstring("Merma", "Motivo de la merma:")
            if motivo:
                exito, msg = database.registrar_merma(p_id, cant, motivo, 1)
                if exito:
                    messagebox.showinfo("Éxito", msg)
                    self.cargar_datos(self.entry_buscar.get())
                else:
                    messagebox.showerror("Error", msg)

    def ajustar_stock(self, cantidad):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla primero.")
            return

        producto_id = self.tabla.item(seleccion[0])["values"][0]
        database.modificar_stock(producto_id, cantidad)
        self.cargar_datos(self.entry_buscar.get())
