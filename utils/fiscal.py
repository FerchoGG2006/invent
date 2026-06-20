"""
Lógica de facturación electrónica simulada y cálculo de impuestos por país.
"""
import uuid
import datetime
import random


# Tasas de IVA por país
TASAS_IVA = {
    "Chile": 0.19,
    "Colombia": 0.19,
    "México": 0.16,
    "Argentina": 0.21,
}

# Etiquetas de identificación fiscal por país
LABELS_ID_FISCAL = {
    "Chile": "RUT del Cliente",
    "Colombia": "NIT del Cliente",
    "México": "RFC del Cliente",
    "Argentina": "CUIT del Cliente",
}

LABELS_ID_CORTO = {
    "Chile": "RUT",
    "Colombia": "NIT",
    "México": "RFC",
    "Argentina": "CUIT",
}

LABELS_IVA_TICKET = {
    "Chile": "IVA (19%)",
    "Colombia": "IVA (19%)",
    "México": "IVA (16%)",
    "Argentina": "IVA (21%)",
}


def calcular_impuestos(total, pais):
    """
    Calcula el IVA incluido en el total según el país.
    Retorna (neto, iva_calculado, tasa_iva).
    """
    tasa = TASAS_IVA.get(pais, 0.0)
    if tasa > 0:
        neto = total / (1 + tasa)
        iva = total - neto
        return neto, iva, tasa
    return total, 0.0, 0.0


def generar_codigo_fiscal(pais, total):
    """
    Genera un código fiscal simulado y URL de verificación.
    Retorna (codigo_fiscal: str, fiscal_qr_url: str).
    """
    if pais == "Chile":
        folio = random.randint(100000, 999999)
        codigo = f"Folio Autorizado SII: {folio}\nTimbre Electrónico SII"
        url = f"https://www.sii.cl/verificar?folio={folio}&monto={total:.0f}"
    elif pais == "Colombia":
        cufe = uuid.uuid4().hex.upper()
        codigo = f"CUFE: {cufe[:36]}"
        url = f"https://catalogo-vpfe.dian.gov.co/document/search?cufe={cufe}"
    elif pais == "México":
        uid = str(uuid.uuid4()).upper()
        codigo = f"CFDI UUID: {uid}"
        url = f"https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id={uid}&re=EMISOR&rr=RECEPTOR&tt={total:.2f}"
    elif pais == "Argentina":
        cae = "".join([str(random.randint(0, 9)) for _ in range(14)])
        vto = (datetime.datetime.now() + datetime.timedelta(days=10)).strftime("%d/%m/%Y")
        codigo = f"CAE: {cae}\nVto CAE: {vto}"
        url = f"https://www.afip.gob.ar/fe/qr/?cae={cae}&vto={vto}&total={total:.2f}"
    else:
        codigo = "Comprobante Comercial Local"
        url = f"https://sistema-pos-local/ticket?total={total:.2f}"

    return codigo, url


def obtener_label_id_fiscal(pais):
    """Retorna la etiqueta del campo de identificación fiscal según el país."""
    return LABELS_ID_FISCAL.get(pais, "Identificación Fiscal")


def obtener_label_id_corto(pais):
    """Retorna la etiqueta corta del ID fiscal (para tickets)."""
    return LABELS_ID_CORTO.get(pais, "ID Fiscal")


def obtener_label_iva_ticket(pais):
    """Retorna la etiqueta del IVA para el ticket."""
    return LABELS_IVA_TICKET.get(pais, "IVA")
