"""
Utilidades de impresión directa ESC/POS para impresoras térmicas.
Usa la API nativa de Windows winspool.drv via ctypes.
"""
import ctypes


def obtener_impresoras_sistema():
    """Devuelve una lista con los nombres de todas las impresoras instaladas en el sistema."""
    try:
        winspool = ctypes.WinDLL('winspool.drv')
        flags = 2 | 4  # PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS
        level = 4

        class PRINTER_INFO_4(ctypes.Structure):
            _fields_ = [
                ("pPrinterName", ctypes.c_wchar_p),
                ("pServerName", ctypes.c_wchar_p),
                ("Attributes", ctypes.c_uint32)
            ]

        needed = ctypes.c_ulong(0)
        returned = ctypes.c_ulong(0)

        winspool.EnumPrintersW(flags, None, level, None, 0, ctypes.byref(needed), ctypes.byref(returned))
        if needed.value == 0:
            return []

        buffer = ctypes.create_string_buffer(needed.value)
        if winspool.EnumPrintersW(flags, None, level, buffer, needed.value, ctypes.byref(needed), ctypes.byref(returned)):
            array_type = PRINTER_INFO_4 * returned.value
            printers = array_type.from_buffer(buffer)
            return [p.pPrinterName for p in printers]
    except Exception:
        pass
    return []


def enviar_impresion_directa(nombre_impresora, texto_ticket):
    """
    Envía texto raw directamente al spooler de la impresora.
    Incluye comandos ESC/POS: init, apertura de cajón, corte de papel.
    Retorna (exito: bool, mensaje: str).
    """
    try:
        winspool = ctypes.WinDLL('winspool.drv')

        hPrinter = ctypes.c_void_p()
        if not winspool.OpenPrinterW(nombre_impresora, ctypes.byref(hPrinter), None):
            raise Exception(f"No se pudo abrir la impresora '{nombre_impresora}'.")

        try:
            class DOC_INFO_1(ctypes.Structure):
                _fields_ = [
                    ("pDocName", ctypes.c_wchar_p),
                    ("pOutputFile", ctypes.c_wchar_p),
                    ("pDatatype", ctypes.c_wchar_p)
                ]

            doc_info = DOC_INFO_1()
            doc_info.pDocName = "Ticket de Venta POS"
            doc_info.pOutputFile = None
            doc_info.pDatatype = "RAW"

            doc_id = winspool.StartDocPrinterW(hPrinter, 1, ctypes.byref(doc_info))
            if doc_id <= 0:
                raise Exception("No se pudo iniciar el documento en el spooler.")

            try:
                if not winspool.StartPagePrinter(hPrinter):
                    raise Exception("No se pudo iniciar la página en el spooler.")

                try:
                    # Inicializar impresora (ESC @)
                    init_printer = b"\x1b\x40"
                    # Pulso de apertura cajón monedero
                    open_drawer = b"\x1b\x70\x00\x19\xfa"

                    # Codificar en cp1252 para conservar tildes/eñes
                    ticket_bytes = texto_ticket.encode('cp1252', errors='replace')

                    # Avance de líneas y corte de papel automático
                    feed_and_cut = b"\n\n\n\n\x1d\x56\x42\x00"

                    data_to_send = init_printer + open_drawer + ticket_bytes + feed_and_cut

                    bytes_written = ctypes.c_ulong(0)
                    if not winspool.WritePrinter(hPrinter, data_to_send, len(data_to_send), ctypes.byref(bytes_written)):
                        raise Exception("Error al escribir los bytes en el spooler.")
                finally:
                    winspool.EndPagePrinter(hPrinter)
            finally:
                winspool.EndDocPrinter(hPrinter)
        finally:
            winspool.ClosePrinter(hPrinter)
        return True, "Ticket enviado correctamente."
    except Exception as e:
        return False, str(e)
