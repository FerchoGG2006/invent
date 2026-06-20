import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import os
from PIL import Image, ImageTk
from utils.fiscal import calcular_impuestos, generar_codigo_fiscal, obtener_label_id_fiscal

class PosTab:
    def __init__(self, app):
        self.app = app
        self.tab = app.tab_pos
        self.construir_tab()

    def construir_tab(self):
        # Panel Izquierdo (Búsqueda de Productos para venta)
        frame_pos_left = tk.Frame(self.tab, bg="#FFFFFF", width=460, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_pos_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        frame_pos_header = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_pos_header.pack(fill=tk.X, pady=10, padx=15)
        tk.Label(frame_pos_header, text="SELECCIONAR PRODUCTO", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side=tk.LEFT)
        self.app.lbl_conexion_pos = tk.Label(frame_pos_header, text="🔍 Verificando red...", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B")
        self.app.lbl_conexion_pos.pack(side=tk.RIGHT)
        self.app.verificar_conexion_async()

        # Entrada de Búsqueda POS
        frame_busca_pos = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_busca_pos.pack(fill=tk.X, padx=15, pady=(0, 10))
        tk.Label(frame_busca_pos, text="Buscar:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=(5, 10))

        busca_pos_border = tk.Frame(frame_busca_pos, bg="#E2E8F0")
        busca_pos_border.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busca_pos = tk.Entry(busca_pos_border, font=("Segoe UI", 10), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0)
        self.entry_busca_pos.pack(fill=tk.X, padx=1, pady=1, ipady=5)
        self.entry_busca_pos.bind("<KeyRelease>", lambda e: self.pos_actualizar_lista_productos(self.entry_busca_pos.get()))
        self.entry_busca_pos.bind("<Return>", self.pos_on_busca_enter)

        # Tabla de Productos para POS
        columnas_prod = ("id", "codigo", "nombre", "precio", "stock")
        self.tabla_pos_prod = ttk.Treeview(frame_pos_left, columns=columnas_prod, show="headings")

        headers_prod = [("ID", 40), ("Referencia", 90), ("Nombre", 160), ("Precio", 85), ("Stock", 65)]
        for col, (texto, ancho) in zip(columnas_prod, headers_prod):
            self.tabla_pos_prod.heading(col, text=texto)
            self.tabla_pos_prod.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
        self.tabla_pos_prod.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Escuchar evento de selección
        self.tabla_pos_prod.bind("<<TreeviewSelect>>", self.pos_on_producto_select)

        # Control de Cantidad, Precio Venta y Agregar
        frame_control_add = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_control_add.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame_control_add, text="Cant:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=2)
        self.entry_cant_pos = tk.Entry(frame_control_add, font=("Segoe UI", 10, "bold"), width=5, bg="#F8FAFC", bd=1, relief=tk.SOLID, justify=tk.CENTER)
        self.entry_cant_pos.pack(side=tk.LEFT, padx=5, ipady=3)
        self.entry_cant_pos.insert(0, "1")
        self.entry_cant_pos.bind("<Return>", self.pos_on_cant_enter)

        tk.Label(frame_control_add, text="Precio Venta ($):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.LEFT, padx=(10, 2))
        self.entry_precio_pos = tk.Entry(frame_control_add, font=("Segoe UI", 10, "bold"), width=10, bg="#F8FAFC", bd=1, relief=tk.SOLID, justify=tk.CENTER)
        self.entry_precio_pos.pack(side=tk.LEFT, padx=5, ipady=3)
        self.entry_precio_pos.bind("<Return>", self.pos_on_precio_enter)

        btn_agregar_carro = tk.Button(frame_control_add, text="Agregar", font=("Segoe UI", 10, "bold"), bg="#4F46E5", fg="white", bd=0, cursor="hand2", command=self.pos_agregar_al_carrito)
        btn_agregar_carro.pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)
        btn_agregar_carro.bind("<Enter>", lambda e: btn_agregar_carro.config(bg="#4338CA"))
        btn_agregar_carro.bind("<Leave>", lambda e: btn_agregar_carro.config(bg="#4F46E5"))

        # Recuadro Imagen de Vista Previa POS
        frame_pos_preview = tk.Frame(frame_pos_left, bg="#FFFFFF")
        frame_pos_preview.pack(fill=tk.X, padx=15, pady=(5, 10))

        tk.Label(frame_pos_preview, text="Imagen del Producto:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#64748B").pack(side=tk.LEFT, padx=5, anchor=tk.N)
        frame_pos_img_container = tk.Frame(frame_pos_preview, bg="#F8FAFC", width=240, height=180, bd=1, relief=tk.SOLID)
        frame_pos_img_container.pack(side=tk.LEFT, padx=10)
        frame_pos_img_container.pack_propagate(False)
        self.lbl_pos_foto_preview = tk.Label(frame_pos_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_pos_foto_preview.pack(expand=True, fill=tk.BOTH)

        # Panel Derecho (Carrito de Compra)
        frame_pos_right = tk.Frame(self.tab, bg="#FFFFFF", width=540, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_pos_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)

        tk.Label(frame_pos_right, text="CARRITO DE VENTAS", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#0F172A").pack(pady=15)

        # Tabla Carrito
        columnas_carro = ("id", "codigo", "nombre", "precio", "cantidad", "total")
        self.tabla_carro = ttk.Treeview(frame_pos_right, columns=columnas_carro, show="headings")
        headers_carro = [("ID", 40), ("Referencia", 90), ("Nombre", 160), ("Precio", 80), ("Cant.", 60), ("Total", 90)]
        for col, (texto, ancho) in zip(columnas_carro, headers_carro):
            self.tabla_carro.heading(col, text=texto)
            self.tabla_carro.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
        self.tabla_carro.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Panel de Datos del Cliente
        frame_cliente = tk.LabelFrame(frame_pos_right, text=" Datos del Cliente / Facturación (Opcional) ", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#4F46E5", labelanchor="nw", highlightbackground="#E2E8F0", highlightthickness=1, bd=0, padx=10, pady=5)
        frame_cliente.pack(fill=tk.X, padx=15, pady=(5, 5))

        frame_cliente_grid = tk.Frame(frame_cliente, bg="#FFFFFF")
        frame_cliente_grid.pack(fill=tk.X, pady=3)
        frame_cliente_grid.columnconfigure(0, weight=1)
        frame_cliente_grid.columnconfigure(1, weight=1)

        cell_name = tk.Frame(frame_cliente_grid, bg="#FFFFFF")
        cell_name.grid(row=0, column=0, padx=5, sticky="ew")
        tk.Label(cell_name, text="Nombre / Razón Social", font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B").pack(anchor=tk.W)
        border_c_name = tk.Frame(cell_name, bg="#E2E8F0")
        border_c_name.pack(fill=tk.X, pady=1)
        self.app.entry_cliente_nombre = tk.Entry(border_c_name, font=("Segoe UI", 9), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0)
        self.app.entry_cliente_nombre.pack(fill=tk.X, padx=1, pady=1, ipady=3)

        cell_id = tk.Frame(frame_cliente_grid, bg="#FFFFFF")
        cell_id.grid(row=0, column=1, padx=5, sticky="ew")

        pais = self.app.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.app.config else "Otro"
        lbl_id_text = obtener_label_id_fiscal(pais)

        self.app.lbl_cliente_identificacion = tk.Label(cell_id, text=lbl_id_text, font=("Segoe UI", 8, "bold"), bg="#FFFFFF", fg="#64748B")
        self.app.lbl_cliente_identificacion.pack(anchor=tk.W)

        border_c_id = tk.Frame(cell_id, bg="#E2E8F0")
        border_c_id.pack(fill=tk.X, pady=1)
        self.app.entry_cliente_identificacion = tk.Entry(border_c_id, font=("Segoe UI", 9), bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, bd=0)
        self.app.entry_cliente_identificacion.pack(fill=tk.X, padx=1, pady=1, ipady=3)

        # Panel de cobro y total
        frame_total = tk.Frame(frame_pos_right, bg="#FFFFFF")
        frame_total.pack(fill=tk.X, padx=15, pady=15)

        self.lbl_total_pos = tk.Label(frame_total, text="TOTAL: $0", font=("Segoe UI", 15, "bold"), bg="#FFFFFF", fg="#0F172A")
        self.lbl_total_pos.pack(side=tk.LEFT, padx=5)

        btn_quitar = tk.Button(frame_total, text="Quitar", font=("Segoe UI", 9, "bold"), bg="#EF4444", fg="white", bd=0, cursor="hand2", command=self.pos_quitar_del_carrito)
        btn_quitar.pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)

        btn_registrar_venta = tk.Button(frame_total, text="Registrar Venta", font=("Segoe UI", 11, "bold"), bg="#10B981", fg="white", bd=0, cursor="hand2", command=self.pos_procesar_venta)
        btn_registrar_venta.pack(side=tk.RIGHT, padx=10, ipady=5, ipadx=15)
        btn_registrar_venta.bind("<Enter>", lambda e: btn_registrar_venta.config(bg="#059669"))
        btn_registrar_venta.bind("<Leave>", lambda e: btn_registrar_venta.config(bg="#10B981"))

        # Selector de Método de Pago
        tk.Label(frame_total, text="Pago:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#475569").pack(side=tk.RIGHT, padx=(10, 5))
        self.combo_pago = ttk.Combobox(frame_total, values=["Efectivo", "Transferencia"], state="readonly", width=12, font=("Segoe UI", 10))
        self.combo_pago.pack(side=tk.RIGHT, padx=5, ipady=2)
        self.combo_pago.set("Efectivo")

    def pos_actualizar_lista_productos(self, filtro=""):
        for item in self.tabla_pos_prod.get_children():
            self.tabla_pos_prod.delete(item)
        productos = database.obtener_productos(filtro)
        for p in productos:
            precio_f = f"${p[5]:,.0f}"
            self.tabla_pos_prod.insert("", tk.END, values=(p[0], p[1] or "---", p[2], precio_f, p[6]))

    def pos_on_producto_select(self, event):
        seleccion = self.tabla_pos_prod.selection()
        if not seleccion:
            self.lbl_pos_foto_preview.config(image="", text="Sin foto")
            self.lbl_pos_foto_preview.image = None
            return
        item = self.tabla_pos_prod.item(seleccion[0])["values"]
        p_id = int(item[0])

        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT precio_costo, precio_venta, imagen_ruta FROM productos WHERE id = ?", (p_id,))
            res = cursor.fetchone()
            if res:
                self.app.selected_cost_price = res[0]
                self.app.selected_sell_price = res[1]

                self.entry_precio_pos.delete(0, tk.END)
                self.entry_precio_pos.insert(0, f"{res[1]:.0f}")

                if res[2]:
                    self.app.actualizar_vista_previa_label(self.lbl_pos_foto_preview, res[2], (230, 170))
                else:
                    self.lbl_pos_foto_preview.config(image="", text="Sin foto")
                    self.lbl_pos_foto_preview.image = None

    def pos_agregar_al_carrito(self):
        seleccion = self.tabla_pos_prod.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto de la lista primero.")
            return

        try:
            cantidad = int(self.entry_cant_pos.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.")
            return

        try:
            precio_venta = float(self.entry_precio_pos.get())
            if precio_venta <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El precio de venta debe ser un número válido mayor a 0.")
            return

        if precio_venta < self.app.selected_cost_price:
            confirmar = messagebox.askyesno(
                "⚠️ Advertencia de Pérdidas",
                f"El precio ingresado (${precio_venta:,.0f}) es menor al precio de costo (${self.app.selected_cost_price:,.0f}).\n"
                "Esta transacción generará pérdidas directas.\n\n¿Estás seguro de que deseas continuar?"
            )
            if not confirmar:
                return

        item_seleccionado = self.tabla_pos_prod.item(seleccion[0])["values"]
        p_id = int(item_seleccionado[0])
        p_codigo = item_seleccionado[1]
        p_nombre = item_seleccionado[2]
        p_stock = int(item_seleccionado[4])

        carrito_item = next((item for item in self.app.carrito if item["id"] == p_id), None)
        nueva_cantidad = cantidad
        if carrito_item:
            nueva_cantidad += carrito_item["cantidad"]

        if nueva_cantidad > p_stock:
            messagebox.showwarning("Sin stock suficiente", f"No puedes agregar esa cantidad. Stock disponible: {p_stock}")
            return

        if carrito_item:
            carrito_item["cantidad"] = nueva_cantidad
            carrito_item["precio"] = precio_venta
        else:
            self.app.carrito.append({
                "id": p_id,
                "codigo": p_codigo,
                "nombre": p_nombre,
                "precio": precio_venta,
                "cantidad": cantidad
            })

        self.entry_cant_pos.delete(0, tk.END)
        self.entry_cant_pos.insert(0, "1")
        self.pos_actualizar_tabla_carrito()

    def pos_actualizar_tabla_carrito(self):
        for item in self.tabla_carro.get_children():
            self.tabla_carro.delete(item)

        total_acumulado = 0.0
        for item in self.app.carrito:
            total_item = item["precio"] * item["cantidad"]
            total_acumulado += total_item

            valores = (
                item["id"],
                item["codigo"],
                item["nombre"],
                f"${item['precio']:,.0f}",
                item["cantidad"],
                f"${total_item:,.0f}"
            )
            self.tabla_carro.insert("", tk.END, values=valores)

        self.lbl_total_pos.config(text=f"TOTAL: ${total_acumulado:,.0f}")

    def pos_quitar_del_carrito(self):
        seleccion = self.tabla_carro.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un artículo del carrito para quitarlo.")
            return

        item_id = int(self.tabla_carro.item(seleccion[0])["values"][0])
        self.app.carrito = [item for item in self.app.carrito if item["id"] != item_id]
        self.pos_actualizar_tabla_carrito()

    def pos_procesar_venta(self):
        if not self.app.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito para realizar una venta.")
            return

        metodo_pago = self.combo_pago.get()
        carrito_copia = list(self.app.carrito)

        cliente_nombre = self.app.entry_cliente_nombre.get().strip()
        cliente_identificacion = self.app.entry_cliente_identificacion.get().strip()

        total_acumulado = sum(item["precio"] * item["cantidad"] for item in self.app.carrito)
        pais = self.app.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.app.config else "Otro"

        _neto, iva_calculado, _tasa = calcular_impuestos(total_acumulado, pais)
        codigo_fiscal, fiscal_qr_url = generar_codigo_fiscal(pais, total_acumulado)

        errores = []
        for item in self.app.carrito:
            exito, msg = database.registrar_venta(
                item["id"], item["cantidad"], item["precio"], metodo_pago,
                cliente_nombre, cliente_identificacion, iva_calculado, codigo_fiscal, fiscal_qr_url
            )
            if not exito:
                errores.append(f"{item['nombre']}: {msg}")

        if errores:
            messagebox.showerror("Error al procesar ventas", "\n".join(errores))
        else:
            messagebox.showinfo("Venta exitosa", "¡La venta ha sido registrada con éxito!")
            self.app.carrito = []
            self.pos_actualizar_tabla_carrito()
            self.pos_actualizar_lista_productos(self.entry_busca_pos.get())
            self.app.pos_actualizar_alertas_pestaña()
            self.lbl_pos_foto_preview.config(image="", text="Sin foto")
            self.lbl_pos_foto_preview.image = None

            self.app.entry_cliente_nombre.delete(0, tk.END)
            self.app.entry_cliente_identificacion.delete(0, tk.END)

            self.app.pos_generar_ticket(carrito_copia, metodo_pago, cliente_nombre, cliente_identificacion, iva_calculado, codigo_fiscal, fiscal_qr_url)

    def pos_on_busca_enter(self, event):
        children = self.tabla_pos_prod.get_children()
        if children:
            first_item = children[0]
            self.tabla_pos_prod.selection_set(first_item)
            self.tabla_pos_prod.focus(first_item)
            self.pos_on_producto_select(None)

            self.entry_cant_pos.focus_set()
            self.entry_cant_pos.select_range(0, tk.END)
            self.entry_cant_pos.icursor(tk.END)

    def pos_on_cant_enter(self, event):
        self.entry_precio_pos.focus_set()
        self.entry_precio_pos.select_range(0, tk.END)
        self.entry_precio_pos.icursor(tk.END)

    def pos_on_precio_enter(self, event):
        self.pos_agregar_al_carrito()
        self.entry_busca_pos.delete(0, tk.END)
        self.pos_actualizar_lista_productos("")
        self.entry_busca_pos.focus_set()
