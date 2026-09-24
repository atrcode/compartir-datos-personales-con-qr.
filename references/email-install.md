# Firma e instructivo por aplicación

Distinguir cuenta/proveedor de aplicación. Adaptar al editor real, idioma, sistema y versión. Consultar fuentes oficiales en cada ejecución porque cambian los menús. Redactar pasos propios y enlazar documentación, sin copiar extensos fragmentos.

## Fuentes de partida

Comprobar vigencia y seleccionar la versión/pestaña pertinente.

| Destino | Fuente oficial |
| --- | --- |
| Gmail web / Google Workspace | https://support.google.com/mail/answer/8395?hl=es-419 |
| Outlook / Microsoft 365 / Outlook.com | https://support.microsoft.com/es-es/outlook/mail/how-to-add-and-change-an-email-signature-in-outlook |
| Apple Mail en Mac | https://support.apple.com/guide/mail/mail11943/mac |
| iCloud Mail web | Buscar «email signature» en https://support.apple.com/icloud |
| Thunderbird | Buscar «Signatures» en https://support.mozilla.org/products/thunderbird |
| Yahoo Mail | Buscar «signature» en https://help.yahoo.com/ |
| Zoho Mail | Buscar «signature» en https://www.zoho.com/mail/help/ |
| Otra aplicación/webmail/móvil | Consultar soporte oficial del proveedor y sistema. |

No atribuir capacidades de Apple Mail a iCloud web, de Outlook clásico al nuevo, ni de Gmail web a su app móvil. Si se usan dos aplicaciones, preparar dos secciones o instructivos.

## Estructura del instructivo entregable

1. Identificar destino exacto y variante de firma compatible.
2. Enlazar `firma-email.html` y `.txt` con rutas relativas correctas. Explicar cómo abrir HTML en navegador y copiar solo la firma visible. No pegar etiquetas en un editor que no procesa código.
3. Mostrar ruta de configuración vigente y creación de una firma nueva con nombre reconocible.
4. Detallar pegado/importación, asignación a cuenta y preferencias para nuevos mensajes, respuestas y reenvíos según admita el cliente.
5. Indicar cómo guardar y revisar en la ventana de composición.
6. Proponer que el usuario se envíe un mensaje de prueba y lo revise en móvil/escritorio; no enviarlo automáticamente sin autorización.
7. Resolver imágenes bloqueadas, pérdida de formato, tamaño incorrecto y enlaces sin acción. No garantizar diseño idéntico en todos los clientes.
8. Incluir fecha de consulta y fuentes oficiales. Si no se pudo consultar documentación, marcar pasos sin verificar y pedir la mínima captura necesaria para guiar.

## Diseño

- Tabla HTML liviana, estilos inline, texto seleccionable y una imagen opcional pequeña; nunca toda la firma en una imagen.
- Imágenes PNG/JPEG desde HTTPS público duradero: verificar acceso sin sesión, contenido y proporciones. Un link a vista previa de Drive no es imagen directa.
- Conservar significado con imágenes deshabilitadas y enlaces reconocibles sin depender del color.
- Excluir trackers, scripts, formularios, fuentes externas y datos que el usuario no quiso publicar.
- Tratar el HTML del script como base para revisar, sin certificar automáticamente que el cliente conserva el formato.
