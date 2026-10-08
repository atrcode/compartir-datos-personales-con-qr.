# Pruebas en teléfonos

**Todavía no se ejecutaron pruebas de radio.** Completar modelos, versiones, commit instalado y evidencia antes de marcar una fila como aprobada.

| Transporte | Emisor | Receptor | URL corta / 384 bytes | Resultado |
| --- | --- | --- | --- | --- |
| BLE | Android | Android | Pendiente | Pendiente |
| BLE | Android | iPhone | Pendiente | Pendiente |
| BLE | iPhone | Android | Pendiente | Pendiente |
| BLE | iPhone | iPhone | Pendiente | Pendiente |
| NFC HCE | Android | Android | Pendiente | Pendiente |
| NFC HCE | Android | iPhone | Pendiente | Pendiente |
| NFC físico | Etiqueta | Android | Según capacidad | Pendiente |
| NFC físico | Etiqueta | iPhone | Según capacidad | Pendiente |

Para cada fila: fecha, modelo/OS de ambos, commit/build, enlace exacto enviado y recibido, duración, captura o video del resultado y decisión del receptor de abrir. Usar solo enlaces públicos.

También probar:

- Permiso Bluetooth denegado y luego habilitado; radio apagada; equipo sin advertising.
- Salir al inicio/bloquear pantalla durante anuncio, escaneo y conexión. Confirmar que ya no entregue el enlace tras detenerlo.
- Caducidad de envío de 2 minutos; recepción que vence sin encontrar emisores; nuevo intento posterior.
- Dos o más emisores cerca: elección explícita y validación del enlace.
- Retirar NFC a mitad de lectura y reintentar; otra app que registre el mismo AID.
- URL inválida recibida: nunca abrirla; URL de 384 bytes: recibirla completa.
- BLE desconectado mientras se lee; reiniciar Bluetooth y repetir sin reinstalar.
- NFC físico: verificar capacidad, contenido previo y lectura exacta después de grabar.

iPhone como emisor NFC sin accesorio no figura como prueba implementada. La ausencia de esa fila no significa compatibilidad.
