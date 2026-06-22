import os
import re

COLOR_MAP = {
    '("#FFFFFF", "#1E293B")': '(("#FFFFFF", "#1E293B"), "#1E293B")',  # Fondos principales
    '("#F8FAFC", ("#0F172A", "#F8FAFC"))': '(("#F8FAFC", ("#0F172A", "#F8FAFC")), ("#0F172A", "#F8FAFC"))',  # Fondos secundarios
    '("#0F172A", "#F8FAFC")': '(("#0F172A", "#F8FAFC"), ("#F8FAFC", ("#0F172A", "#F8FAFC")))',  # Texto principal oscuro -> Texto claro
    '("#475569", "#CBD5E1")': '(("#475569", "#CBD5E1"), "#CBD5E1")',  # Texto secundario oscuro -> Texto claro
    '("#64748B", "#94A3B8")': '(("#64748B", "#94A3B8"), "#94A3B8")',  # Texto gris
    '("#E2E8F0", "#334155")': '(("#E2E8F0", "#334155"), "#334155")',  # Bordes principales
    '("#D1D5DB", "#475569")': '(("#D1D5DB", "#475569"), ("#475569", "#CBD5E1"))',  # Bordes secundarios
}

def refactorizar_colores(directorio):
    archivos_modificados = 0
    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                for old_color, new_color in COLOR_MAP.items():
                    # Para atrapar casos con comillas simples o dobles
                    content = content.replace(old_color, new_color)
                    old_color_single = old_color.replace('"', "'")
                    content = content.replace(old_color_single, new_color)

                if content != original_content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Modificado: {path}")
                    archivos_modificados += 1
    print(f"Total de archivos modificados: {archivos_modificados}")

if __name__ == "__main__":
    refactorizar_colores(".")
