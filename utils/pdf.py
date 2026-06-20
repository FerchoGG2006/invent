"""
Generador de PDF básico sin dependencias externas.
Usa formato PDF crudo (PDF 1.4) con fuente Courier.
"""


def generar_pdf_ticket(lineas, ruta_pdf):
    """Genera un PDF básico del ticket sin dependencias externas usando formato PDF crudo."""
    font_size = 10
    line_height = 14
    margin_x = 40
    margin_top = 40
    page_width = 300
    page_height = margin_top + (len(lineas) + 2) * line_height + 40

    # Construir el contenido de texto PDF (stream)
    text_commands = ["BT", f"/F1 {font_size} Tf"]
    y_pos = page_height - margin_top

    for linea in lineas:
        # Escapar caracteres especiales de PDF
        linea_safe = linea.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        text_commands.append(f"1 0 0 1 {margin_x} {y_pos} Tm")
        text_commands.append(f"({linea_safe}) Tj")
        y_pos -= line_height

    text_commands.append("ET")
    stream_content = "\n".join(text_commands)
    stream_length = len(stream_content)

    # Construir los objetos PDF
    objects = []
    offsets = []

    pdf_header = "%PDF-1.4\n"
    current_pos = len(pdf_header)

    # Objeto 1: Catálogo
    offsets.append(current_pos)
    obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    objects.append(obj1)
    current_pos += len(obj1)

    # Objeto 2: Páginas
    offsets.append(current_pos)
    obj2 = "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    objects.append(obj2)
    current_pos += len(obj2)

    # Objeto 3: Página
    offsets.append(current_pos)
    obj3 = f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    objects.append(obj3)
    current_pos += len(obj3)

    # Objeto 4: Contenido (stream de texto)
    offsets.append(current_pos)
    obj4 = f"4 0 obj\n<< /Length {stream_length} >>\nstream\n{stream_content}\nendstream\nendobj\n"
    objects.append(obj4)
    current_pos += len(obj4)

    # Objeto 5: Fuente
    offsets.append(current_pos)
    obj5 = "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n"
    objects.append(obj5)
    current_pos += len(obj5)

    # Tabla de referencias cruzadas (xref)
    xref_pos = current_pos
    xref = "xref\n"
    xref += f"0 {len(objects) + 1}\n"
    xref += "0000000000 65535 f \n"
    for offset in offsets:
        xref += f"{offset:010d} 00000 n \n"

    # Trailer
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"

    # Escribir el PDF completo
    with open(ruta_pdf, "w", encoding="latin-1") as f:
        f.write(pdf_header)
        for obj in objects:
            f.write(obj)
        f.write(xref)
        f.write(trailer)
