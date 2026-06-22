import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generar_reporte_pdf(ruta_archivo, filtro, resumen, ventas_data):
    """
    Genera un PDF con el reporte de ventas.
    """
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    elementos = []
    estilos = getSampleStyleSheet()
    
    # Título
    estilo_titulo = ParagraphStyle('Titulo', parent=estilos['Heading1'], alignment=1, fontSize=18, spaceAfter=20, textColor=colors.HexColor("#0F172A"))
    elementos.append(Paragraph("Reporte de Ventas", estilo_titulo))
    
    # Subtítulo (Filtro y Fecha)
    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], alignment=1, fontSize=11, spaceAfter=20, textColor=colors.HexColor("#475569"))
    elementos.append(Paragraph(f"Período: {filtro} | Generado el: {fecha_generacion}", estilo_sub))
    
    # Resumen (Tarjetas)
    datos_resumen = [
        ["Total Ingresos", "Transacciones", "Efectivo", "Transferencia", "Utilidad Est."],
        [f"${resumen['total']:,.0f}", str(resumen['cant']), f"${resumen['efe']:,.0f}", f"${resumen['tra']:,.0f}", f"${resumen['utilidad']:,.0f}"]
    ]
    
    tabla_resumen = Table(datos_resumen, colWidths=[1.3*inch]*5)
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor("#0F172A")),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
    ]))
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 30))
    
    # Título de Tabla
    elementos.append(Paragraph("Detalle de Transacciones", estilos['Heading3']))
    elementos.append(Spacer(1, 10))
    
    # Tabla de Ventas
    headers = ["ID", "Producto", "Cant.", "Precio Unit.", "Descuento", "Total", "Fecha", "Pago"]
    datos_ventas = [headers]
    
    for v in ventas_data:
        # v = (id, codigo, nombre, cantidad, precio, total, fecha, metodo, desc, cliente_nom, cliente_id, impuestos, folio, qr, cortesia, autoriza)
        desc_f = f"${v[8]:,.0f}" if v[8] else "$0"
        fila = [
            str(v[0]),
            (v[2][:20] + '..') if len(v[2]) > 20 else v[2],
            str(v[3]),
            f"${v[4]:,.0f}",
            desc_f,
            f"${v[5]:,.0f}",
            v[6].split(" ")[0], # Solo la fecha para ahorrar espacio
            v[7]
        ]
        datos_ventas.append(fila)
        
    if len(datos_ventas) == 1:
        datos_ventas.append(["No hay transacciones en este período.", "", "", "", "", "", "", ""])
        
    tabla_ventas = Table(datos_ventas, colWidths=[0.5*inch, 2.0*inch, 0.5*inch, 0.9*inch, 0.8*inch, 0.9*inch, 1.0*inch, 0.9*inch])
    tabla_ventas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Producto a la izq
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    
    elementos.append(tabla_ventas)
    
    doc.build(elementos)
    return True
