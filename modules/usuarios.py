import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import database

def mostrar_gestion_usuarios(app):
    """Muestra la ventana de gestión de usuarios (CRUD básico)."""
    
    win = ctk.CTkToplevel(app.root)
    win.title("Gestión de Usuarios")
    win.geometry("500x500")
    win.configure(fg_color=("#F8FAFC", ("#0F172A", "#F8FAFC")))
    win.resizable(False, False)
    win.grab_set()

    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'+{x}+{y}')

    frame_header = ctk.CTkFrame(win, fg_color="#4F46E5", corner_radius=0, height=65)
    frame_header.pack(fill=tk.X)
    ctk.CTkLabel(frame_header, text="👥 GESTIÓN DE USUARIOS", font=("Segoe UI", 13, "bold"), text_color="white").pack(pady=18)

    # Contenedor principal
    frame_content = ctk.CTkFrame(win, fg_color=("#FFFFFF", "#1E293B"), border_color=("#E2E8F0", "#334155"), border_width=1, corner_radius=12)
    frame_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Tabla
    frame_tabla = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    columnas = ("id", "nombre", "usuario", "rol")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)
    
    headers = [("ID", 40), ("Nombre", 140), ("Usuario", 100), ("Rol", 100)]
    for col, (texto, ancho) in zip(columnas, headers):
        tabla.heading(col, text=texto)
        tabla.column(col, width=ancho, anchor=tk.CENTER if col == "id" else tk.W)
    
    tabla.pack(fill=tk.BOTH, expand=True)

    def actualizar_tabla():
        for item in tabla.get_children():
            tabla.delete(item)
        with database.sqlite3.connect(database.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios")
            for u in cursor.fetchall():
                tabla.insert("", tk.END, values=u)

    actualizar_tabla()

    # Controles
    frame_botones = ctk.CTkFrame(frame_content, fg_color="transparent")
    frame_botones.pack(fill=tk.X, padx=15, pady=15)

    def nuevo_usuario():
        win_nuevo = ctk.CTkToplevel(win)
        win_nuevo.title("Nuevo Usuario")
        win_nuevo.geometry("350x450")
        win_nuevo.configure(fg_color=("#F8FAFC", ("#0F172A", "#F8FAFC")))
        win_nuevo.grab_set()

        ctk.CTkLabel(win_nuevo, text="NUEVO USUARIO", font=("Segoe UI", 12, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(pady=15)
        
        frame_form = ctk.CTkFrame(win_nuevo, fg_color="transparent")
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20)

        ctk.CTkLabel(frame_form, text="Nombre Completo:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ent_nombre = ctk.CTkEntry(frame_form)
        ent_nombre.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(frame_form, text="Usuario (Login):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ent_usuario = ctk.CTkEntry(frame_form)
        ent_usuario.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(frame_form, text="Contraseña:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ent_pass = ctk.CTkEntry(frame_form, show="*")
        ent_pass.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(frame_form, text="Rol:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        combo_rol = ctk.CTkComboBox(frame_form, values=["Cajero", "Administrador"])
        combo_rol.pack(fill=tk.X, pady=(0, 20))
        combo_rol.set("Cajero")

        def guardar_usr():
            n = ent_nombre.get().strip()
            u = ent_usuario.get().strip()
            p = ent_pass.get().strip()
            r = combo_rol.get()
            if not n or not u or not p:
                messagebox.showerror("Error", "Todos los campos son obligatorios", parent=win_nuevo)
                return
            
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)", (n, u, database.hash_password(p), r))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Usuario creado correctamente.", parent=win_nuevo)
                    actualizar_tabla()
                    win_nuevo.destroy()
                except database.sqlite3.IntegrityError:
                    messagebox.showerror("Error", "El nombre de usuario ya existe.", parent=win_nuevo)
        
        ctk.CTkButton(win_nuevo, text="Guardar", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 10, "bold"), command=guardar_usr).pack(pady=15, padx=20, fill=tk.X)

    def eliminar_usuario():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un usuario de la lista.", parent=win)
            return
            
        item = tabla.item(sel[0])["values"]
        uid = int(item[0])
        urol = item[3]
        
        if uid == getattr(app, "usuario_actual_id", None):
            messagebox.showerror("Error", "No puedes eliminar tu propio usuario mientras estás en sesión.", parent=win)
            return
            
        if urol == "Administrador":
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'Administrador'")
                if cursor.fetchone()[0] <= 1:
                    messagebox.showerror("Error", "Debe existir al menos un administrador en el sistema.", parent=win)
                    return
                    
        conf = messagebox.askyesno("Eliminar", f"¿Estás seguro de eliminar al usuario '{item[2]}'?", parent=win)
        if conf:
            with database.sqlite3.connect(database.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
                conn.commit()
            actualizar_tabla()

    ctk.CTkButton(frame_botones, text="➕ Nuevo", font=("Segoe UI", 10, "bold"), fg_color="#4F46E5", hover_color="#4338CA", width=100, command=nuevo_usuario).pack(side=tk.LEFT, padx=5)
    ctk.CTkButton(frame_botones, text="🗑️ Eliminar", font=("Segoe UI", 10, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=100, command=eliminar_usuario).pack(side=tk.LEFT, padx=5)
