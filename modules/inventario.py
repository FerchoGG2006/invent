import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import customtkinter as ctk
import database
import os
import shutil

def rc(color_val):
    if isinstance(color_val, tuple):
        try:
            return color_val[1] if ctk.get_appearance_mode() == "Dark" else color_val[0]
        except Exception:
            return color_val[0]
    return color_val

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

            ctk.CTkLabel(cell, text=label_text, font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(0, 1))
            
            if key in ["categoria", "proveedor_id", "unidad_medida"]:
                combo = ctk.CTkComboBox(cell, font=("Segoe UI", 10), height=32, corner_radius=5, state="readonly")
                combo.pack(fill=tk.X, pady=1)
                self.inputs[key] = combo
            else:
                entry = ctk.CTkEntry(cell, font=("Segoe UI", 10), fg_color=("#F8FAFC", "#0F172A"), text_color=("#0F172A", "#F8FAFC"), border_color=("#D1D5DB", "#475569"), height=32, corner_radius=5)
                entry.pack(fill=tk.X, pady=1)
                self.inputs[key] = entry

        self.inputs["min_stock"].insert(0, "3")
        self.inputs["unidad_medida"].configure(values=["Unidad", "Kg", "Litro", "Metro", "Caja"])
        self.inputs["unidad_medida"].set("Unidad")
        self.inputs["categoria"].set("Seleccionar...")
        self.inputs["proveedor_id"].set("Seleccionar...")
        self.actualizar_combos()

        # Campo para Imagen (No obligatorio)
        ctk.CTkLabel(frame_form, text="Imagen del Producto", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, padx=20, pady=(5, 1))
        frame_img_sel = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_img_sel.pack(fill=tk.X, padx=20, pady=2)

        self.btn_select_img = ctk.CTkButton(frame_img_sel, text="Seleccionar Foto", font=("Segoe UI", 10, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1F2937", height=30, width=120, corner_radius=5, command=self.pos_seleccionar_imagen)
        self.btn_select_img.pack(side=tk.LEFT)

        self.lbl_img_path = ctk.CTkLabel(frame_img_sel, text="Sin foto", font=("Segoe UI", 10), text_color="#94A3B8", anchor=tk.W)
        self.lbl_img_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Recuadro Vista Previa Formulario
        frame_form_img_container = ctk.CTkFrame(frame_form, fg_color=("#F8FAFC", "#0F172A"), border_color=("#D1D5DB", "#475569"), border_width=1, height=90, corner_radius=6)
        frame_form_img_container.pack(pady=5, padx=20, fill=tk.X)
        frame_form_img_container.pack_propagate(False)
        self.lbl_img_preview = tk.Label(frame_form_img_container, text="Sin vista previa", font=("Segoe UI", 10, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_img_preview.pack(expand=True, fill=tk.BOTH)

        btn_guardar = ctk.CTkButton(frame_form, text="Guardar Producto", font=("Segoe UI", 12, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=38, corner_radius=8, command=self.guardar_producto)
        btn_guardar.pack(fill=tk.X, padx=25, pady=(5, 5))

        btn_combo = ctk.CTkButton(frame_form, text="📦 Crear Combo", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=38, corner_radius=8, command=self.modal_nuevo_combo)
        btn_combo.pack(fill=tk.X, padx=25, pady=(0, 10))

        # Panel Derecho (Tabla y Buscador)
        frame_grid = ctk.CTkFrame(self.tab, fg_color="transparent")
        frame_grid.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        # Buscador y botones de acción
        frame_busca = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_busca.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(frame_busca, text="🔍 Buscar:", font=("Segoe UI", 12, "bold"), text_color=("#475569", "#CBD5E1")).pack(side=tk.LEFT, padx=(5, 10))

        self.entry_buscar = ctk.CTkEntry(frame_busca, font=("Segoe UI", 12), fg_color=("#FFFFFF", "#1E293B"), text_color=("#0F172A", "#F8FAFC"), border_color=("#D1D5DB", "#475569"), height=36, corner_radius=6, placeholder_text="Nombre, código o categoría...")
        self.entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos(self.entry_buscar.get()))

        btn_eliminar = ctk.CTkButton(frame_busca, text="Eliminar", font=("Segoe UI", 10, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", height=36, width=100, corner_radius=6, command=self.eliminar_producto)
        btn_eliminar.pack(side=tk.RIGHT, padx=5)

        btn_merma = ctk.CTkButton(frame_busca, text="Merma", font=("Segoe UI", 10, "bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", height=36, width=85, corner_radius=6, command=self.registrar_merma)
        btn_merma.pack(side=tk.RIGHT, padx=5)

        btn_kardex = ctk.CTkButton(frame_busca, text="📊 Kardex", font=("Segoe UI", 10, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=36, width=95, corner_radius=6, command=self.mostrar_kardex_seleccionado)
        btn_kardex.pack(side=tk.RIGHT, padx=5)

        btn_etiqueta = ctk.CTkButton(frame_busca, text="🏷️ Etiqueta", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=36, width=100, corner_radius=6, command=self.imprimir_etiqueta)
        btn_etiqueta.pack(side=tk.RIGHT, padx=5)

        # Botones de ajuste de stock
        frame_botones = ctk.CTkFrame(frame_grid, fg_color="transparent")
        frame_botones.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        btn_mas = ctk.CTkButton(frame_botones, text="+", font=("Segoe UI", 12, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1E293B", width=40, height=40, corner_radius=6, command=lambda: self.ajustar_stock(1))
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
        
        btn_menos = ctk.CTkButton(frame_botones, text="-", font=("Segoe UI", 12, "bold"), fg_color="#E5E7EB", hover_color=("#D1D5DB", "#475569"), text_color="#1E293B", width=40, height=40, corner_radius=6, command=lambda: self.ajustar_stock(-1))
        btn_menos.pack(pady=5)

        # Recuadro Imagen de Producto Seleccionado
        ctk.CTkLabel(frame_botones, text="Foto:", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(pady=(15, 2))
        
        frame_inv_img_container = ctk.CTkFrame(frame_botones, fg_color=("#FFFFFF", "#1E293B"), border_color=("#D1D5DB", "#475569"), border_width=1, width=120, height=120, corner_radius=6)
        frame_inv_img_container.pack(pady=2, fill=tk.X)
        frame_inv_img_container.pack_propagate(False)
        
        self.lbl_inv_foto_preview = tk.Label(frame_inv_img_container, text="Sin foto", font=("Segoe UI", 10, "italic"), bg="#FFFFFF", fg="#94A3B8", compound="center")
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
            entry = ctk.CTkEntry(frame, font=("Segoe UI", 10), height=30, corner_radius=6)
            entry.pack(fill=tk.X, pady=(0, 5))
            entry.insert(0, str(default_val) if default_val is not None else "")
            return entry
            
        inputs["codigo"] = add_entry("Referencia / Código de Barras", producto[1])
        inputs["nombre"] = add_entry("Nombre del Producto *", producto[2])
        
        # Categoría
        ctk.CTkLabel(frame, text="Categoría", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_cat = ctk.CTkComboBox(frame, values=self.inputs["categoria"].cget("values"), font=("Segoe UI", 10), height=30, corner_radius=6)
        combo_cat.pack(fill=tk.X, pady=(0, 5))
        combo_cat.set(producto[3] if producto[3] else "Seleccionar...")
        inputs["categoria"] = combo_cat
        
        # Proveedor
        ctk.CTkLabel(frame, text="Proveedor", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_prov = ctk.CTkComboBox(frame, values=self.inputs["proveedor_id"].cget("values"), font=("Segoe UI", 10), height=30, corner_radius=6)
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
        inputs["costo"] = ctk.CTkEntry(f1, font=("Segoe UI", 10), height=30, corner_radius=6)
        inputs["costo"].pack(fill=tk.X); inputs["costo"].insert(0, str(producto[4]))
        
        f2 = ctk.CTkFrame(frame_precios, fg_color="transparent"); f2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ctk.CTkLabel(f2, text="Venta ($) *", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["venta"] = ctk.CTkEntry(f2, font=("Segoe UI", 10), height=30, corner_radius=6)
        inputs["venta"].pack(fill=tk.X); inputs["venta"].insert(0, str(producto[5]))
        
        # Stock
        frame_stock = ctk.CTkFrame(frame, fg_color="transparent")
        frame_stock.pack(fill=tk.X, pady=5)
        
        f3 = ctk.CTkFrame(frame_stock, fg_color="transparent"); f3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ctk.CTkLabel(f3, text="Stock Actual", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["stock"] = ctk.CTkEntry(f3, font=("Segoe UI", 10), height=30, corner_radius=6)
        inputs["stock"].pack(fill=tk.X); inputs["stock"].insert(0, str(producto[6]))
        
        f4 = ctk.CTkFrame(frame_stock, fg_color="transparent"); f4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ctk.CTkLabel(f4, text="Stock Mín.", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W)
        inputs["min_stock"] = ctk.CTkEntry(f4, font=("Segoe UI", 10), height=30, corner_radius=6)
        inputs["min_stock"].pack(fill=tk.X); inputs["min_stock"].insert(0, str(producto[7]))
        
        # Unidad de medida
        ctk.CTkLabel(frame, text="Unidad de Medida", font=("Segoe UI", 10, "bold"), text_color=("#64748B", "#94A3B8")).pack(anchor=tk.W, pady=(5, 0))
        combo_uni = ctk.CTkComboBox(frame, values=["Unidad", "Kg", "Litro", "Metro", "Caja", "Paquete", "Servicio"], font=("Segoe UI", 10), height=30, corner_radius=6)
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
        lbl_img_status = ctk.CTkLabel(frame_img, text="Mantener actual", font=("Segoe UI", 10), text_color="#94A3B8")
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
                
        btn_guardar = ctk.CTkButton(frame, text="Guardar Cambios", font=("Segoe UI", 10, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", height=35, corner_radius=6, command=guardar_cambios)
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

    def mostrar_kardex_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla primero.")
            return
            
        valores = self.tabla.item(seleccion[0])["values"]
        p_id = int(valores[0])
        p_ref = valores[1]
        p_nombre = valores[2]
        
        KardexDialog(self.app.root, p_id, p_nombre, p_ref)

    def ajustar_stock(self, cantidad):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla primero.")
            return

        producto_id = self.tabla.item(seleccion[0])["values"][0]
        database.modificar_stock(producto_id, cantidad)
        self.cargar_datos(self.entry_buscar.get())

    def modal_nuevo_combo(self):
        win = ctk.CTkToplevel(self.app.root)
        win.title("Nuevo Combo / Paquete")
        win.geometry("500x500")
        win.grab_set()

        ctk.CTkLabel(win, text="📦 Crear Nuevo Combo", font=("Segoe UI", 16, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(win, text="El combo se venderá como un producto único,\npero descontará stock de los productos que selecciones.", font=("Segoe UI", 10), text_color="#64748B").pack(pady=(0, 15))

        frame_top = ctk.CTkFrame(win, fg_color="transparent")
        frame_top.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(frame_top, text="Nombre del Combo:").grid(row=0, column=0, sticky="w", pady=5)
        entry_nombre = ctk.CTkEntry(frame_top, width=200)
        entry_nombre.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(frame_top, text="Precio de Venta ($):").grid(row=1, column=0, sticky="w", pady=5)
        entry_precio = ctk.CTkEntry(frame_top, width=200)
        entry_precio.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(win, text="Productos Incluidos:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, padx=20, pady=(15, 5))

        frame_prods = ctk.CTkScrollableFrame(win, height=200)
        frame_prods.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        productos = database.obtener_productos("")
        vars_productos = {}
        for p in productos:
            if not p[11]: # No mostrar otros combos (p[11] = es_combo)
                var = tk.IntVar(value=0)
                vars_productos[p[0]] = var
                check = ctk.CTkCheckBox(frame_prods, text=f"{p[2]} (${p[5]:,.0f})", variable=var)
                check.pack(anchor=tk.W, pady=2)

        def guardar_combo():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio.", parent=win)
                return
            try:
                precio = float(entry_precio.get())
            except ValueError:
                messagebox.showerror("Error", "Precio inválido.", parent=win)
                return

            seleccionados = [pid for pid, var in vars_productos.items() if var.get() == 1]
            if not seleccionados:
                messagebox.showerror("Error", "Selecciona al menos un producto.", parent=win)
                return

            import sqlite3
            with sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                # Insertar como producto pero con es_combo = 1, stock infinito (9999), no tiene costo
                codigo = f"C-{int(tk.Tcl().eval('clock seconds'))}"
                cursor.execute("""
                    INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, unidad_medida, es_combo)
                    VALUES (?, ?, 'Combos', 0, ?, 9999, 0, 'Servicio', 1)
                """, (codigo, nombre, precio))
                combo_id = cursor.lastrowid
                
                for pid in seleccionados:
                    cursor.execute("INSERT INTO combos_detalle (combo_id, producto_id, cantidad) VALUES (?, ?, 1)", (combo_id, pid))
                conn.commit()
                
            messagebox.showinfo("Éxito", "Combo creado con éxito.", parent=win)
            self.cargar_datos(self.entry_buscar.get())
            win.destroy()

        ctk.CTkButton(win, text="Crear Combo", command=guardar_combo, fg_color="#4F46E5").pack(pady=15)

    def imprimir_etiqueta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto para generar la etiqueta.")
            return
            
        valores = self.tabla.item(seleccion[0])["values"]
        codigo = valores[1]
        nombre = valores[2]
        precio = valores[5]
        
        if not codigo or codigo == "---":
            # Autogenerar un código basado en el ID si no tiene
            codigo = f"PROD-{valores[0]}"
            database.modificar_codigo_producto(valores[0], codigo)
            self.cargar_datos(self.entry_buscar.get())
            
        import tempfile
        import webbrowser
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Etiqueta - {nombre}</title>
    <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; text-align: center; margin: 0; padding: 10px; background: #fff; }}
        .label-container {{ display: inline-block; border: 1px dashed #ccc; padding: 15px; border-radius: 8px; width: 50mm; height: auto; }}
        .nombre {{ font-size: 14px; font-weight: bold; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }}
        .precio {{ font-size: 18px; font-weight: bold; margin-top: 5px; }}
        svg {{ max-width: 100%; height: auto; }}
        @media print {{
            body {{ padding: 0; }}
            .label-container {{ border: none; padding: 0; margin: 0; width: 100%; height: 100%; }}
            @page {{ margin: 0; size: 58mm auto; }}
        }}
    </style>
</head>
<body onload="window.print()">
    <div class="label-container">
        <div class="nombre">{nombre}</div>
        <svg id="barcode"></svg>
        <div class="precio">{precio}</div>
    </div>
    <script>
        JsBarcode("#barcode", "{codigo}", {{
            format: "CODE128",
            width: 2,
            height: 50,
            displayValue: true,
            fontSize: 14
        }});
    </script>
</body>
</html>'''

        fd, temp_path = tempfile.mkstemp(suffix=".html", text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        webbrowser.open('file://' + os.path.abspath(temp_path))


class KardexDialog(ctk.CTkToplevel):
    def __init__(self, parent, producto_id, producto_nombre, producto_codigo):
        super().__init__(parent)
        self.producto_id = producto_id
        self.producto_nombre = producto_nombre
        self.producto_codigo = producto_codigo
        
        self.title(f"Kardex: {self.producto_nombre} ({self.producto_codigo})")
        self.grab_set()
        
        # Ventana más grande y centrada
        width = 1000
        height = 600
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.minsize(800, 450)
        
        self._configurar_estilo_kardex()
        self.crear_interfaz()
        self.cargar_datos()

    def _configurar_estilo_kardex(self):
        """Crea un estilo dedicado para el Treeview del Kardex."""
        style = ttk.Style()
        is_dark = ctk.get_appearance_mode() == "Dark"

        if is_dark:
            bg = "#1E293B"
            fg = "#F1F5F9"
            heading_bg = "#0F172A"
            heading_fg = "#E2E8F0"
            sel_bg = "#475569"
            sel_fg = "#FFFFFF"
        else:
            bg = "#FFFFFF"
            fg = "#1E293B"
            heading_bg = "#F1F5F9"
            heading_fg = "#334155"
            sel_bg = "#E0E7FF"
            sel_fg = "#312E81"

        style.configure("Kardex.Treeview",
                        background=bg,
                        foreground=fg,
                        fieldbackground=bg,
                        font=("Segoe UI", 10),
                        rowheight=30)
        style.configure("Kardex.Treeview.Heading",
                        background=heading_bg,
                        foreground=heading_fg,
                        font=("Segoe UI", 10, "bold"))
        style.map("Kardex.Treeview",
                  background=[('selected', sel_bg)],
                  foreground=[('selected', sel_fg)])

    def crear_interfaz(self):
        is_dark = ctk.get_appearance_mode() == "Dark"

        # Cabecera con fondo de color
        frame_header = ctk.CTkFrame(self, fg_color=("#EEF2FF", "#1E293B"), corner_radius=10)
        frame_header.pack(fill=tk.X, padx=16, pady=(16, 8))

        ctk.CTkLabel(
            frame_header, text="📊  KARDEX DE MOVIMIENTOS",
            font=("Segoe UI", 18, "bold"),
            text_color=rc(("#1E293B", "#F8FAFC"))
        ).pack(anchor=tk.W, padx=16, pady=(12, 2))

        ctk.CTkLabel(
            frame_header,
            text=f"Producto: {self.producto_nombre}   |   Código: {self.producto_codigo}",
            font=("Segoe UI", 12),
            text_color=rc(("#475569", "#94A3B8"))
        ).pack(anchor=tk.W, padx=16, pady=(0, 12))

        # Barra de estadísticas rápidas
        self.frame_stats = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self.frame_stats.pack(fill=tk.X, padx=16, pady=(0, 6))

        self.lbl_total_movs = ctk.CTkLabel(self.frame_stats, text="", font=("Segoe UI", 10, "bold"), text_color=rc(("#475569", "#94A3B8")))
        self.lbl_total_movs.pack(side=tk.LEFT, padx=(4, 16))

        self.lbl_entradas = ctk.CTkLabel(self.frame_stats, text="", font=("Segoe UI", 10, "bold"), text_color="#16A34A")
        self.lbl_entradas.pack(side=tk.LEFT, padx=(0, 16))

        self.lbl_salidas = ctk.CTkLabel(self.frame_stats, text="", font=("Segoe UI", 10, "bold"), text_color="#DC2626")
        self.lbl_salidas.pack(side=tk.LEFT, padx=(0, 16))

        # Contenedor Tabla
        frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        columnas = ("fecha", "tipo", "cantidad", "stock_anterior", "stock_nuevo", "motivo", "usuario")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style="Kardex.Treeview")

        headers = [
            ("Fecha / Hora", 160),
            ("Tipo", 90),
            ("Cantidad", 85),
            ("Stock Ant.", 90),
            ("Stock Nuevo", 95),
            ("Detalle / Motivo", 300),
            ("Usuario", 100)
        ]

        for col, (texto, ancho) in zip(columnas, headers):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, minwidth=50, anchor=tk.CENTER if col in ["tipo", "cantidad", "stock_anterior", "stock_nuevo", "usuario"] else tk.W)

        self.tabla.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Colores de tags (con contraste explícito según modo)
        if is_dark:
            self.tabla.tag_configure("entrada", background="#064E3B", foreground="#6EE7B7")
            self.tabla.tag_configure("salida", background="#4C0519", foreground="#FCA5A5")
            self.tabla.tag_configure("ajuste", background="#0C4A6E", foreground="#7DD3FC")
        else:
            self.tabla.tag_configure("entrada", background="#F0FDF4", foreground="#166534")
            self.tabla.tag_configure("salida", background="#FEF2F2", foreground="#991B1B")
            self.tabla.tag_configure("ajuste", background="#EFF6FF", foreground="#1E40AF")

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        movs = database.obtener_kardex_producto(self.producto_id)

        total_entradas = 0
        total_salidas = 0

        for m in movs:
            fecha, tipo, cant, stock_ant, stock_nue, motivo, usuario = m

            cant_str = f"+{cant}" if cant > 0 else f"{cant}"

            if "Ajuste" in motivo or "Migración" in motivo or "Inicial" in motivo:
                tag = "ajuste"
            elif tipo == "Entrada":
                tag = "entrada"
                total_entradas += abs(cant)
            else:
                tag = "salida"
                total_salidas += abs(cant)

            self.tabla.insert("", tk.END, values=(fecha, tipo, cant_str, stock_ant, stock_nue, motivo, usuario), tags=(tag,))

        # Actualizar estadísticas
        total = len(movs)
        self.lbl_total_movs.configure(text=f"Total: {total} movimientos")
        self.lbl_entradas.configure(text=f"▲ Entradas: {total_entradas} uds")
        self.lbl_salidas.configure(text=f"▼ Salidas: {total_salidas} uds")

