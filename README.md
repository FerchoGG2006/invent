# 📦 Sistema POS - Control de Inventario y Ventas

¡Bienvenido al manual de uso de tu nuevo sistema de ventas e inventario! Este programa ha sido diseñado para que sea súper fácil de usar, rápido y muy seguro. No necesitas saber nada de programación ni tecnicismos para operarlo.

Aquí tienes una guía sencilla para que empieces a sacarle el máximo provecho en tu negocio.

---

## 🚀 ¿Cómo empezar a usar el programa?

Solo necesitas hacer doble clic en el archivo **`InventarioPOS.exe`** en tu computadora. 

> 💡 **Nota sobre actualizaciones**: Cada vez que se abra el programa y tengas conexión a internet, el sistema buscará si hay una versión más nueva. Si existe, te aparecerá un aviso en pantalla y podrás actualizar el programa a la última versión con un solo clic. ¡Sin complicaciones!

---

## 🛠️ Guía Paso a Paso para el Día a Día

### 1. Configuración Inicial (Solo la primera vez)
Al abrir el programa por primera vez, el sistema te pedirá los datos de tu negocio:
* Nombre del negocio, teléfono, dirección y un mensaje bonito que saldrá en la parte inferior de tus recibos/tickets.
* Selecciona tu país para ajustar la configuración de impuestos local.
* Crea tu primer usuario **Administrador** y escribe una contraseña segura que recuerdes. ¡No la compartas!

---

### 2. Configurar tu Inventario (Tus Productos)
Antes de vender, debes registrar los productos que tienes disponibles.
1. Ve a la pestaña **📦 Inventario**.
2. Haz clic en **Agregar Producto** (o en el botón con el ícono correspondiente).
3. Llena los datos básicos:
   * **Código**: Puede ser un código de barras (usando tu lector) o uno corto inventado por ti (ej: `SHAMP01`).
   * **Nombre**: El nombre del producto o servicio (ej: `Corte de Cabello`, `Cera para Barba`).
   * **Precios**: Escribe cuánto te cuesta a ti comprarlo (**Costo**) y a cuánto lo vendes al público (**Venta**). El programa calculará automáticamente tu porcentaje de ganancia.
   * **Stock (Cantidad)**: Cuántas unidades tienes físicamente en este momento.
   * **Stock Mínimo (Alerta)**: Si configuras esto en `3`, el sistema te avisará con una alerta visual cuando te queden 3 unidades o menos de ese producto para que no te quedes desabastecido.
   * **Imagen**: Puedes subir una foto del producto para identificarlo visualmente.

---

### 3. Abrir Caja (Al iniciar tu jornada)
Es importante que el sistema sepa cuánto dinero tienes al abrir el negocio para dar el cambio (sencillo).
1. Ve a la pestaña **💵 Caja**.
2. Registra el **Monto de Apertura** (por ejemplo, si empiezas el día con `$50,000` en efectivo para dar cambio).
3. A partir de ese momento, todas las ventas en efectivo se sumarán automáticamente a tu caja.
4. Si necesitas sacar dinero para pagar algo (ej: comprar bolsas o papelería), usa el botón **Registrar Salida de Dinero** para mantener tus cuentas claras.

---

### 4. Realizar una Venta (Punto de Venta / POS)
¡La parte principal! Cuando llegue un cliente a pagar:
1. Ve a la pestaña **🛒 Punto de Venta**.
2. Busca el producto escribiendo su nombre o pasando el lector por el código de barras.
3. Haz doble clic sobre el producto o presiona "Agregar" para sumarlo al carrito.
4. En el carrito puedes:
   * Cambiar la cantidad de unidades.
   * Aplicar un **Descuento** en dinero si quieres hacer una oferta.
   * Marcarlo como **Cortesía** (el precio será $0 y te pedirá escribir quién autorizó el regalo).
5. Escribe el nombre del cliente si deseas que su nombre aparezca en el ticket.
6. Elige cómo te va a pagar: **Efectivo** o **Transferencia**.
7. Haz clic en **Cobrar y Generar Ticket**. El sistema:
   * Descontará automáticamente los productos vendidos de tu inventario.
   * Abrirá el cajón monedero (si tienes uno conectado).
   * Imprimirá el ticket térmico en tu impresora configurada.

---

### 5. Reportes y Cierre de Caja (Al finalizar el día)
Para saber cómo va tu negocio y retirar las ganancias de forma segura:
1. Ve a la pestaña **📊 Historial de Ventas**.
2. **Corte de Caja**: Haz clic en este botón para ver un resumen rápido de cuánto se vendió hoy en efectivo, cuánto en transferencia y cuál fue tu **Ganancia Real (Utilidad)** restando lo que te costaron los productos. Puedes imprimir este reporte o copiarlo al portapapeles.
3. **Anular Ventas**: Si te equivocaste en una venta, puedes seleccionarla en la lista y hacer clic en **Anular Venta**. El dinero se restará del reporte y los productos volverán automáticamente al inventario.
4. **Ver Copia de Ticket**: Si un cliente te pide copia de su recibo anterior, búscalo en la lista y presiona **Ver/Imprimir Ticket**.
5. **Respaldar DB**: ¡Súper Importante! Haz clic en este botón al menos una vez a la semana para guardar una copia de seguridad de toda tu información en una memoria USB o en otra carpeta. Si tu computadora se daña, no perderás tus datos.

---

## ❓ Preguntas Frecuentes (FAQ)

#### ¿Qué hago si me sale un aviso de "Alerta de Stock"?
Significa que algunos de tus productos se están agotando. Ve a la pestaña de inventario, busca los que tienen el aviso rojo 🚨 y haz un pedido a tus proveedores para reabastecerlos.

#### ¿Cómo cambio los datos de mi negocio o la impresora?
En la pestaña de **Historial de Ventas**, haz clic en el botón de **⚙️ Configuración**. Allí podrás modificar el nombre, dirección, mensaje de pie de página y seleccionar cuál de las impresoras conectadas a tu computadora imprimirá los tickets de venta.

#### ¿Puedo borrar todos los datos de prueba que ingresé?
Sí. En la pestaña de **Historial de Ventas** tienes un botón llamado **Vaciar Sistema**. Te pedirá confirmación de seguridad y borrará las ventas y productos de prueba para que dejes el sistema limpio y listo para trabajar en serio.

---
*Manual actualizado para la versión 1.0.0. Desarrollado con 💙 para facilitarte el control de tu negocio.*
