import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import customtkinter as ctk
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
        frame_pos_left = ctk.CTkFrame(self.tab, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
        frame_pos_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        frame_pos_header = ctk.CTkFrame(frame_pos_left, fg_color="transparent")
        frame_pos_header.pack(fill=tk.X, pady=(15, 10), padx=15)
        
        ctk.CTkLabel(frame_pos_header, text="SELECCIONAR PRODUCTO", font=("Segoe UI", 12, "bold"), text_color="#0F172A").pack(side=tk.LEFT)
        
        # Indicador de estado de la nube
        self.lbl_estado_nube = ctk.CTkLabel(frame_pos_header, text="☁️ Sincronizando...", font=("Segoe UI", 10, "bold"), text_color="#64748B")
        self.lbl_estado_nube.pack(side=tk.RIGHT, padx=(10, 0))
        self.actualizar_estado_nube()
        
        self.app.lbl_conexion_pos = ctk.CTkLabel(frame_pos_header, text="🔍 Verificando red...", font=("Segoe UI", 10, "bold"), text_color="#64748B")
        self.app.lbl_conexion_pos.pack(side=tk.RIGHT, padx=10)
        self.app.verificar_conexion_async()

        # Entrada de Búsqueda POS
        frame_busca_pos = ctk.CTkFrame(frame_pos_left, fg_color="transparent")
        frame_busca_pos.pack(fill=tk.X, padx=15, pady=(0, 5))
        ctk.CTkLabel(frame_busca_pos, text="Buscar:", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(side=tk.LEFT, padx=(5, 10))

        self.entry_busca_pos = ctk.CTkEntry(frame_busca_pos, font=("Segoe UI", 11), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=32, corner_radius=6)
        self.entry_busca_pos.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busca_pos.bind("<KeyRelease>", lambda e: self.pos_actualizar_lista_productos(self.entry_busca_pos.get()))
        self.entry_busca_pos.bind("<Return>", self.pos_on_busca_enter)

        # Tabla de Productos para POS (ttk Treeview colocado dentro del CTkFrame)
        frame_tabla_prod = ctk.CTkFrame(frame_pos_left, fg_color="transparent")
        frame_tabla_prod.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        columnas_prod = ("id", "codigo", "nombre", "precio", "stock")
        self.tabla_pos_prod = ttk.Treeview(frame_tabla_prod, columns=columnas_prod, show="headings")

        headers_prod = [("ID", 40), ("Referencia", 90), ("Nombre", 160), ("Precio", 85), ("Stock", 65)]
        for col, (texto, ancho) in zip(columnas_prod, headers_prod):
            self.tabla_pos_prod.heading(col, text=texto)
            self.tabla_pos_prod.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre"] else tk.W)
        self.tabla_pos_prod.pack(fill=tk.BOTH, expand=True)
        self.tabla_pos_prod.bind("<<TreeviewSelect>>", self.pos_on_producto_select)

        # Control de Cantidad, Precio Venta, Nota y Agregar
        frame_control_add = ctk.CTkFrame(frame_pos_left, fg_color="transparent")
        frame_control_add.pack(fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(frame_control_add, text="Cant:", font=("Segoe UI", 9, "bold"), text_color="#475569").grid(row=0, column=0, padx=2, sticky=tk.W)
        self.entry_cant_pos = ctk.CTkEntry(frame_control_add, font=("Segoe UI", 10, "bold"), width=60, fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28, justify=tk.CENTER)
        self.entry_cant_pos.grid(row=0, column=1, padx=5, pady=2)
        self.entry_cant_pos.insert(0, "1")
        self.entry_cant_pos.bind("<Return>", self.pos_on_cant_enter)

        ctk.CTkLabel(frame_control_add, text="Precio ($):", font=("Segoe UI", 9, "bold"), text_color="#475569").grid(row=0, column=2, padx=2, sticky=tk.W)
        self.entry_precio_pos = ctk.CTkEntry(frame_control_add, font=("Segoe UI", 10, "bold"), width=90, fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28, justify=tk.CENTER)
        self.entry_precio_pos.grid(row=0, column=3, padx=5, pady=2)
        self.entry_precio_pos.bind("<Return>", self.pos_on_precio_enter)
        
        ctk.CTkLabel(frame_control_add, text="Nota:", font=("Segoe UI", 9, "bold"), text_color="#475569").grid(row=1, column=0, padx=2, sticky=tk.W)
        self.entry_nota_pos = ctk.CTkEntry(frame_control_add, font=("Segoe UI", 9), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28)
        self.entry_nota_pos.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=2)
        self.entry_nota_pos.bind("<Return>", self.pos_on_precio_enter)

        btn_agregar_carro = ctk.CTkButton(frame_control_add, text="Agregar", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#4338CA", text_color="white", height=32, corner_radius=6, command=self.pos_agregar_al_carrito)
        btn_agregar_carro.grid(row=0, column=4, rowspan=2, padx=10, sticky=tk.NS)

        # Recuadro Imagen de Vista Previa POS
        frame_pos_preview = ctk.CTkFrame(frame_pos_left, fg_color="transparent")
        frame_pos_preview.pack(fill=tk.X, padx=15, pady=(5, 15))

        ctk.CTkLabel(frame_pos_preview, text="Imagen del Producto:", font=("Segoe UI", 9, "bold"), text_color="#64748B").pack(side=tk.LEFT, padx=5, anchor=tk.N)
        
        frame_pos_img_container = ctk.CTkFrame(frame_pos_preview, fg_color="#F8FAFC", border_color="#D1D5DB", border_width=1, width=220, height=140, corner_radius=6)
        frame_pos_img_container.pack(side=tk.LEFT, padx=10)
        frame_pos_img_container.pack_propagate(False)
        
        self.lbl_pos_foto_preview = tk.Label(frame_pos_img_container, text="Sin foto", font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#94A3B8", compound="center")
        self.lbl_pos_foto_preview.pack(expand=True, fill=tk.BOTH)

        # Panel Derecho (Carrito de Compra)
        frame_pos_right = ctk.CTkFrame(self.tab, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=12)
        frame_pos_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        ctk.CTkLabel(frame_pos_right, text="CARRITO DE VENTAS", font=("Segoe UI", 12, "bold"), text_color="#0F172A").pack(pady=(15, 5))

        # Tabla Carrito
        frame_tabla_carro = ctk.CTkFrame(frame_pos_right, fg_color="transparent")
        frame_tabla_carro.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        columnas_carro = ("id", "codigo", "nombre", "precio", "cantidad", "total", "nota")
        self.tabla_carro = ttk.Treeview(frame_tabla_carro, columns=columnas_carro, show="headings")
        headers_carro = [("ID", 40), ("Ref", 70), ("Nombre", 140), ("Precio", 70), ("Cant.", 50), ("Total", 80), ("Nota", 80)]
        for col, (texto, ancho) in zip(columnas_carro, headers_carro):
            self.tabla_carro.heading(col, text=texto)
            self.tabla_carro.column(col, width=ancho, anchor=tk.CENTER if col not in ["nombre", "nota"] else tk.W)
        self.tabla_carro.pack(fill=tk.BOTH, expand=True)

        # Panel de Datos del Cliente
        frame_cliente = ctk.CTkFrame(frame_pos_right, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=8)
        frame_cliente.pack(fill=tk.X, padx=15, pady=5)
        
        ctk.CTkLabel(frame_cliente, text="Datos del Cliente / Facturación (Opcional)", font=("Segoe UI", 9, "bold"), text_color="#4F46E5").pack(anchor=tk.W, padx=15, pady=(5, 2))

        frame_cliente_grid = ctk.CTkFrame(frame_cliente, fg_color="transparent")
        frame_cliente_grid.pack(fill=tk.X, pady=3, padx=10)
        frame_cliente_grid.columnconfigure(0, weight=1)
        frame_cliente_grid.columnconfigure(1, weight=1)

        cell_name = ctk.CTkFrame(frame_cliente_grid, fg_color="transparent")
        cell_name.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(cell_name, text="Nombre / Razón Social", font=("Segoe UI", 8, "bold"), text_color="#64748B").pack(anchor=tk.W)
        self.app.entry_cliente_nombre = ctk.CTkEntry(cell_name, font=("Segoe UI", 9), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28, corner_radius=5)
        self.app.entry_cliente_nombre.pack(fill=tk.X, pady=1)

        cell_id = ctk.CTkFrame(frame_cliente_grid, fg_color="transparent")
        cell_id.grid(row=0, column=1, padx=5, sticky="ew")

        pais = self.app.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.app.config else "Otro"
        lbl_id_text = obtener_label_id_fiscal(pais)

        self.app.lbl_cliente_identificacion = ctk.CTkLabel(cell_id, text=lbl_id_text, font=("Segoe UI", 8, "bold"), text_color="#64748B")
        self.app.lbl_cliente_identificacion.pack(anchor=tk.W)

        self.app.entry_cliente_identificacion = ctk.CTkEntry(cell_id, font=("Segoe UI", 9), fg_color="#F8FAFC", text_color="#0F172A", border_color="#D1D5DB", height=28, corner_radius=5)
        self.app.entry_cliente_identificacion.pack(fill=tk.X, pady=1)

        # Panel de cobro, total, descuentos y propinas
        frame_total = ctk.CTkFrame(frame_pos_right, fg_color="transparent")
        frame_total.pack(fill=tk.X, padx=15, pady=10)

        # Campos de descuentos y propinas
        frame_extras = ctk.CTkFrame(frame_total, fg_color="transparent")
        frame_extras.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(frame_extras, text="Descuento ($):", font=("Segoe UI", 9), text_color="#1E293B").pack(side=tk.LEFT)
        self.entry_descuento = ctk.CTkEntry(frame_extras, width=70, font=("Segoe UI", 9), height=26, corner_radius=4)
        self.entry_descuento.pack(side=tk.LEFT, padx=5)
        self.entry_descuento.insert(0, "0")
        self.entry_descuento.bind("<KeyRelease>", lambda e: self.pos_actualizar_tabla_carrito())

        ctk.CTkLabel(frame_extras, text="Propina ($):", font=("Segoe UI", 9), text_color="#1E293B").pack(side=tk.LEFT, padx=(10,0))
        self.entry_propina = ctk.CTkEntry(frame_extras, width=70, font=("Segoe UI", 9), height=26, corner_radius=4)
        self.entry_propina.pack(side=tk.LEFT, padx=5)
        self.entry_propina.insert(0, "0")
        self.entry_propina.bind("<KeyRelease>", lambda e: self.pos_actualizar_tabla_carrito())

        # Fila del Total y Botones
        frame_total_botones = ctk.CTkFrame(frame_total, fg_color="transparent")
        frame_total_botones.pack(side=tk.TOP, fill=tk.X)

        self.lbl_total_pos = ctk.CTkLabel(frame_total_botones, text="TOTAL: $0", font=("Segoe UI", 15, "bold"), text_color="#0F172A")
        self.lbl_total_pos.pack(side=tk.LEFT, padx=5)

        btn_dividir = ctk.CTkButton(frame_total_botones, text="Dividir", font=("Segoe UI", 9, "bold"), fg_color="#38BDF8", hover_color="#0EA5E9", text_color="white", width=65, height=30, corner_radius=6, command=self.pos_dividir_cuenta)
        btn_dividir.pack(side=tk.LEFT, padx=8)

        btn_cortesia = ctk.CTkButton(frame_total_botones, text="Cortesía", font=("Segoe UI", 9, "bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", width=70, height=30, corner_radius=6, command=self.pos_registrar_cortesia)
        btn_cortesia.pack(side=tk.LEFT, padx=5)

        btn_quitar = ctk.CTkButton(frame_total_botones, text="Quitar", font=("Segoe UI", 9, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", width=65, height=32, corner_radius=6, command=self.pos_quitar_del_carrito)
        btn_quitar.pack(side=tk.RIGHT, padx=5)

        btn_registrar_venta = ctk.CTkButton(frame_total_botones, text="Registrar", font=("Segoe UI", 11, "bold"), fg_color="#10B981", hover_color="#059669", text_color="white", width=80, height=32, corner_radius=6, command=self.pos_procesar_venta)
        btn_registrar_venta.pack(side=tk.RIGHT, padx=5)

        # Selector de Método de Pago
        ctk.CTkLabel(frame_total_botones, text="Pago:", font=("Segoe UI", 9, "bold"), text_color="#475569").pack(side=tk.RIGHT, padx=(5, 2))
        metodos = ["Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito", "Billetera Virtual", "Mixto"]
        
        self.combo_pago = ctk.CTkComboBox(frame_total_botones, values=metodos, font=("Segoe UI", 9), height=28, width=110, corner_radius=6)
        self.combo_pago.pack(side=tk.RIGHT, padx=2)
        self.combo_pago.set("Efectivo")

    def actualizar_estado_nube(self):
        from utils import sync
        estado = sync.estado_sincronizacion
        if estado == "Sincronizado":
            self.lbl_estado_nube.configure(text=f"☁️ Nube OK ({sync.ultimo_intento})", text_color="#10B981")
        elif estado == "Sincronizando...":
            self.lbl_estado_nube.configure(text="☁️ Sincronizando...", text_color="#F59E0B")
        elif estado == "Error de conexión":
            self.lbl_estado_nube.configure(text="☁️ Error Nube", text_color="#EF4444")
        else:
            self.lbl_estado_nube.configure(text="☁️ Nube deshabilitada", text_color="#94A3B8")
        self.app.root.after(5000, self.actualizar_estado_nube)

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
                
                self.entry_nota_pos.delete(0, tk.END)

                if res[2]:
                    self.app.actualizar_vista_previa_label(self.lbl_pos_foto_preview, res[2], (210, 130))
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

        nota = self.entry_nota_pos.get().strip()

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

        carrito_item = next((item for item in self.app.carrito if item["id"] == p_id and item.get("nota", "") == nota), None)
        nueva_cantidad = cantidad
        if carrito_item:
            nueva_cantidad += carrito_item["cantidad"]

        # Calcular stock total en carrito para este producto (independiente de la nota)
        stock_en_carrito = sum(item["cantidad"] for item in self.app.carrito if item["id"] == p_id)
        if stock_en_carrito + cantidad > p_stock:
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
                "cantidad": cantidad,
                "nota": nota
            })

        self.entry_cant_pos.delete(0, tk.END)
        self.entry_cant_pos.insert(0, "1")
        self.entry_nota_pos.delete(0, tk.END)
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
                f"${total_item:,.0f}",
                item.get("nota", "")
            )
            self.tabla_carro.insert("", tk.END, values=valores)

        try:
            desc = float(self.entry_descuento.get() or "0")
            prop = float(self.entry_propina.get() or "0")
        except ValueError:
            desc = 0.0
            prop = 0.0

        total_final = max(0, total_acumulado - desc) + prop
        self.lbl_total_pos.configure(text=f"TOTAL: ${total_final:,.0f}")
        return total_final

    def pos_quitar_del_carrito(self):
        seleccion = self.tabla_carro.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un artículo del carrito para quitarlo.")
            return

        item_id = int(self.tabla_carro.item(seleccion[0])["values"][0])
        item_nota = self.tabla_carro.item(seleccion[0])["values"][6]
        
        for idx, item in enumerate(self.app.carrito):
            if item["id"] == item_id and item.get("nota", "") == item_nota:
                self.app.carrito.pop(idx)
                break
        
        self.pos_actualizar_tabla_carrito()

    def pos_dividir_cuenta(self):
        total = self.pos_actualizar_tabla_carrito()
        if total <= 0:
            return
        
        personas = simpledialog.askinteger("Dividir Cuenta", "¿Entre cuántas personas se dividirá la cuenta?", minvalue=2, maxvalue=50, parent=self.tab)
        if personas:
            por_persona = total / personas
            messagebox.showinfo("División de Cuenta", f"Total: ${total:,.0f}\nDividido entre {personas} personas:\n\nCada uno debe pagar: ${por_persona:,.0f}")

    def pos_registrar_cortesia(self):
        if not self.app.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos para registrar cortesía.")
            return

        admin_user = simpledialog.askstring("Autorización Requerida", "Usuario administrador:", parent=self.tab)
        admin_pass = simpledialog.askstring("Autorización Requerida", "Contraseña administrador:", show="*", parent=self.tab)
        
        if not admin_user or not admin_pass:
            return
            
        usuario = database.verificar_usuario(admin_user, admin_pass)
        if not usuario or usuario["rol"] != "Administrador":
            messagebox.showerror("No Autorizado", "Credenciales incorrectas o el usuario no es Administrador.")
            return

        # Cambiamos precio a 0 y guardamos como cortesía
        for item in self.app.carrito:
            item["precio"] = 0
            
        self.entry_descuento.delete(0, tk.END)
        self.entry_descuento.insert(0, "0")
        self.entry_propina.delete(0, tk.END)
        self.entry_propina.insert(0, "0")
        self.pos_actualizar_tabla_carrito()
        
        # Procesar de inmediato
        self.pos_procesar_venta(es_cortesia=1, autorizado_por=admin_user)

    def pos_procesar_venta(self, es_cortesia=0, autorizado_por=""):
        if not self.app.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito para realizar una venta.")
            return

        total_final = self.pos_actualizar_tabla_carrito()
        metodo_pago = self.combo_pago.get()
        pagos_mixtos = []

        if metodo_pago == "Mixto":
            win_mixto = ctk.CTkToplevel(self.app.root)
            win_mixto.title("Pago Mixto")
            win_mixto.geometry("340x380")
            win_mixto.grab_set()

            ctk.CTkLabel(win_mixto, text=f"Total a Pagar: ${total_final:,.0f}", font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            entries_pagos = {}
            for m in ["Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito", "Billetera Virtual"]:
                frame_m = ctk.CTkFrame(win_mixto, fg_color="transparent")
                frame_m.pack(fill=tk.X, padx=25, pady=5)
                ctk.CTkLabel(frame_m, text=f"{m}:", width=110, anchor="w").pack(side=tk.LEFT)
                ent = ctk.CTkEntry(frame_m, width=90, justify="right")
                ent.pack(side=tk.RIGHT)
                ent.insert(0, "0")
                entries_pagos[m] = ent

            resultado_mixto = {"exito": False}
            
            def confirmar_mixto():
                suma = 0
                for m, ent in entries_pagos.items():
                    try:
                        val = float(ent.get() or "0")
                        suma += val
                        if val > 0:
                            pagos_mixtos.append((m, val))
                    except ValueError:
                        pass
                
                if abs(suma - total_final) > 0.01:
                    messagebox.showerror("Error", f"La suma de los pagos (${suma:,.0f}) no coincide con el total (${total_final:,.0f}).", parent=win_mixto)
                    pagos_mixtos.clear()
                    return
                resultado_mixto["exito"] = True
                win_mixto.destroy()

            ctk.CTkButton(win_mixto, text="Confirmar Pago", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 10, "bold"), command=confirmar_mixto).pack(pady=20)
            self.app.root.wait_window(win_mixto)

            if not resultado_mixto["exito"]:
                return

        try:
            descuento = float(self.entry_descuento.get() or "0")
            propina = float(self.entry_propina.get() or "0")
        except ValueError:
            descuento = 0.0
            propina = 0.0

        carrito_copia = list(self.app.carrito)

        cliente_nombre = self.app.entry_cliente_nombre.get().strip()
        cliente_identificacion = self.app.entry_cliente_identificacion.get().strip()

        pais = self.app.config.get("pais_operacion", "Otro / Ninguno (Solo local)") if self.app.config else "Otro"
        _neto, iva_calculado, _tasa = calcular_impuestos(total_final, pais)
        codigo_fiscal, fiscal_qr_url = generar_codigo_fiscal(pais, total_final)

        errores = []
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            for item in self.app.carrito:
                try:
                    cursor.execute("SELECT stock, precio_costo FROM productos WHERE id = ?", (item["id"],))
                    res = cursor.fetchone()
                    if not res:
                        errores.append(f"{item['nombre']}: Producto no encontrado.")
                        continue
                    stock_actual, precio_costo_actual = res
                    if stock_actual < item["cantidad"]:
                        errores.append(f"{item['nombre']}: Stock insuficiente.")
                        continue
                    
                    proporcion = (item["precio"] * item["cantidad"]) / (total_final + descuento - propina) if (total_final + descuento - propina) > 0 else 0
                    desc_item = descuento * proporcion
                    prop_item = propina * proporcion

                    cursor.execute("""
                        INSERT INTO ventas (producto_id, cantidad, precio_unitario, precio_costo_unitario, total, metodo_pago, cliente_nombre, cliente_identificacion, impuestos, codigo_fiscal, fiscal_qr_url, descuento, propina, es_cortesia, autorizado_por, sincronizado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (item["id"], item["cantidad"], item["precio"], precio_costo_actual, item["precio"] * item["cantidad"], metodo_pago, cliente_nombre, cliente_identificacion, iva_calculado * proporcion, codigo_fiscal, fiscal_qr_url, desc_item, prop_item, es_cortesia, autorizado_por))
                    
                    venta_id = cursor.lastrowid

                    if item.get("nota"):
                        cursor.execute("INSERT INTO notas_producto (venta_id, nota_texto) VALUES (?, ?)", (venta_id, item["nota"]))
                    
                    if metodo_pago == "Mixto":
                        for mpago, monto in pagos_mixtos:
                            monto_item = monto * proporcion
                            cursor.execute("INSERT INTO ventas_pagos (venta_id, metodo_pago, monto) VALUES (?, ?, ?)", (venta_id, mpago, monto_item))

                    cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item["cantidad"], item["id"]))

                except Exception as e:
                    errores.append(f"{item['nombre']}: {str(e)}")

            if not errores:
                conn.commit()

        if errores:
            messagebox.showerror("Error al procesar ventas", "\n".join(errores))
        else:
            msg_exito = "¡Cortesía registrada con éxito!" if es_cortesia else "¡Venta registrada con éxito!"
            messagebox.showinfo("Venta Exitosa", msg_exito)
            
            # Limpiar campos y actualizar vistas
            self.app.carrito = []
            self.entry_descuento.delete(0, tk.END)
            self.entry_descuento.insert(0, "0")
            self.entry_propina.delete(0, tk.END)
            self.entry_propina.insert(0, "0")
            self.combo_pago.set("Efectivo")
            self.pos_actualizar_tabla_carrito()
            self.pos_actualizar_lista_productos(self.entry_busca_pos.get())
            self.app.pos_actualizar_alertas_pestaña()
            self.lbl_pos_foto_preview.config(image="", text="Sin foto")
            self.lbl_pos_foto_preview.image = None

            self.app.entry_cliente_nombre.delete(0, tk.END)
            self.app.entry_cliente_identificacion.delete(0, tk.END)

            self.pos_generar_ticket(carrito_copia, metodo_pago, cliente_nombre, cliente_identificacion, iva_calculado, codigo_fiscal, fiscal_qr_url)

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

    def pos_generar_ticket(self, carrito_copia, metodo_pago, cliente_nombre, cliente_identificacion, iva_calculado, codigo_fiscal, fiscal_qr_url):
        impresora = self.app.config.get("impresora_ticket", "")
        if not impresora:
            return

        import datetime
        from utils.printer import enviar_impresion_directa
        
        texto_ticket = "==============================\n"
        texto_ticket += "        TICKET DE VENTA       \n"
        texto_ticket += "==============================\n"
        texto_ticket += f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        if cliente_nombre:
            texto_ticket += f"Cliente: {cliente_nombre}\n"
            if cliente_identificacion:
                texto_ticket += f"ID: {cliente_identificacion}\n"
        texto_ticket += "------------------------------\n"
        texto_ticket += "CANT  PRODUCTO          PRECIO\n"
        texto_ticket += "------------------------------\n"
        
        total = 0
        for item in carrito_copia:
            nombre = item['nombre'][:15].ljust(15)
            precio_total = item['cantidad'] * item['precio']
            total += precio_total
            texto_ticket += f"{item['cantidad']:<4} {nombre} ${precio_total:,.0f}\n"
            
        texto_ticket += "------------------------------\n"
        if iva_calculado > 0:
            texto_ticket += f"Subtotal:           ${total - iva_calculado:,.0f}\n"
            texto_ticket += f"IVA:                ${iva_calculado:,.0f}\n"
        texto_ticket += f"TOTAL:              ${total:,.0f}\n"
        texto_ticket += "------------------------------\n"
        texto_ticket += f"Método de Pago: {metodo_pago}\n"
        
        if codigo_fiscal:
            texto_ticket += f"\nFolio Fiscal:\n{codigo_fiscal}\n"
        if fiscal_qr_url:
            texto_ticket += f"\nCódigo QR:\n{fiscal_qr_url}\n"
            
        texto_ticket += "\n    ¡Gracias por su compra!   \n"
        texto_ticket += "==============================\n"

        enviar_impresion_directa(impresora, texto_ticket)

        self.entry_busca_pos.delete(0, tk.END)
        self.pos_actualizar_lista_productos("")
        self.entry_busca_pos.focus_set()
