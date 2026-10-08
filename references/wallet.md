# Tarjeta de contacto en Apple Wallet y Google Wallet

## Alcance y decisión

Usar un pase genérico de presentación con nombre, rol/empresa, logo, colores y QR a `public_url`. Reutilizar la URL estable y los datos aprobados; dejar bio larga, recursos y catálogo de enlaces en el sitio. Una vCard guarda el contacto en la agenda; un pase permite abrir y mostrar la tarjeta en Wallet. Mantener ambas acciones independientes.

Registrar `intake_only.wallet.targets` con `apple`, `google`, ambas o lista vacía. Usar `issuance_mode` como `own`, `provider` o `undecided`. Registrar por plataforma `not_requested`, `prepared`, `demo`, `issued` o `device_verified`, según la evidencia. Mantener claves privadas, contraseñas y tokens de servicios fuera de este JSON, la skill, archivos compartidos y frontend.

Reutilizar un emisor o proveedor ya autorizado. Si no existe, explicar la configuración necesaria con lenguaje sencillo y preparar primero los datos/diseño del pase. Ofrecer integración de un proveedor externo solo tras revisar compatibilidad, condiciones, costos y tratamiento de datos. No crear suscripciones ni aceptar pagos por el mero pedido de añadir Wallet a una tarjeta.

## Apple Wallet — iPhone

1. Verificar la cuenta emisora, Pass Type ID, Team ID y certificado de firma correspondiente, junto con su clave privada y certificado intermedio de Apple vigente. Acceder a secretos por mecanismos seguros disponibles; no pedir que se peguen en la conversación. Si se usa proveedor, utilizar su emisión autorizada.
2. Preparar un pase `generic` con `pass.json`, identificador/serial estable por tarjeta e imágenes en los tamaños exigidos por la documentación actual. Incluir nombre y rol al frente; información adicional y enlace del sitio en el reverso. Configurar el código de barras QR con la URL estable del sitio, no con un link de instalación Wallet.
3. Crear el manifiesto de los archivos, firmarlo con el certificado del Pass Type ID y empaquetar el contenido firmado como `.pkpass`. Usar el flujo documentado de Apple o una biblioteca mantenida; verificar formato, cadena de firma, correspondencia de identificadores y vigencia del certificado. Una carpeta o ZIP renombrado sin firma no es un pase instalable.
4. Servir por HTTPS con MIME `application/vnd.apple.pkpass`. Incorporar el distintivo oficial «Add to Apple Wallet» y comprobar que el enlace devuelve el pase, no una página de error.
5. Redactar el instructivo: abrir el enlace en iPhone, revisar la vista previa del pase, tocar «Agregar», abrir Wallet y seleccionar la tarjeta para mostrar el QR. Verificar el flujo real cuando haya acceso al dispositivo; en otro caso indicar «instalación en dispositivo pendiente».

## Google Wallet — Android

1. Verificar cuenta de emisor de Google Wallet, Wallet API habilitada y cuenta de servicio autorizada para ese emisor. Distinguir emisión propia de la integración de un proveedor existente. No exponer la clave de servicio en el navegador.
2. Preparar la clase y el objeto de pase genérico con IDs estables, identidad de marca, nombre/rol y QR a `public_url`. Validar los campos con el esquema vigente de GenericClass/GenericObject; añadir vínculos pertinentes mediante los módulos admitidos. No implementar pases de pago ni credenciales NFC para esta tarjeta.
3. Crear o referenciar clase/objeto según el flujo documentado y generar en un entorno seguro el JWT firmado de guardado con la cuenta de servicio. Emitir el enlace `https://pay.google.com/gp/v/save/<JWT_firmado>` y usar el botón oficial. Seguir la recomendación actual de longitud del enlace; si el contenido lo hace demasiado largo, crear el objeto y referenciar su ID. Nunca construir un botón con JWT ficticio, sin firmar o vencido.
4. Verificar el estado del emisor: en modo demo, limitar pruebas a los usuarios de prueba habilitados y rotularlo como tal. Comprobar acceso de publicación antes de ofrecer guardado al público. No describir una aprobación pendiente como obtenida.
5. Redactar el instructivo: abrir el botón en Android con la cuenta de Google elegida, revisar el pase, tocar «Agregar», abrir Google Wallet y mostrar la tarjeta. Adaptar a la disponibilidad de Wallet en el dispositivo/región; no prometer que cualquier app de billetera importará un `.pkpass`.

## Sitio, actualizaciones y verificación

- Agregar los botones oficiales para las plataformas habilitadas. Se puede priorizar el del dispositivo detectado conservando acceso a la otra opción. No habilitar botones que lleven a `#`, JSON sin firmar, un PNG o credenciales pendientes.
- Preparar primero todos los assets y configuración posibles si falta emisión. Entregar archivos de preparación rotulados, sin extensión `.pkpass` ficticia ni enlaces de guardado de ejemplo presentados como reales. Proporcionar el paso puntual para completar el alta o la firma.
- Mantener la dirección codificada en el QR: cambiar los contenidos del sitio no exige reimprimirlo. Diferenciar esto de actualizar nombre/foto/datos visibles en un pase ya guardado. Para esos cambios, implementar el mecanismo de actualización de la plataforma o explicar cómo volver a agregar la versión nueva; no prometer sincronización automática.
- Comprobar en cada plataforma disponible: emisión válida, apertura del flujo de guardado, datos visibles, QR legible desde otro dispositivo y destino idéntico al sitio. Registrar si la prueba fue técnica, en simulador o en un teléfono real.
- Entregar `Instalar-tarjeta-Wallet.html` con secciones únicamente para las plataformas elegidas, fecha de verificación y fuentes. Añadir un QR de instalación separado solo si ayuda a abrirlo desde escritorio, identificándolo claramente para no confundirlo con el QR de networking.

## Fuentes oficiales

Consultadas como base el 8 de octubre de 2026. Volver a comprobarlas al emitir, sin asumir que precios, programas, requisitos o menús siguen iguales.

- [Apple: identificadores y certificados Wallet](https://developer.apple.com/help/account/capabilities/create-wallet-identifiers-and-certificates/)
- [Apple: Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Apple: diseño y firma del pase, guía de referencia](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html)
- [Google: alta de emisores](https://developers.google.com/wallet/generic/getting-started/onboarding-guide)
- [Google: credenciales REST](https://developers.google.com/wallet/generic/getting-started/auth/rest)
- [Google: emisión desde web](https://developers.google.com/wallet/generic/web)
- [Google: JWT](https://developers.google.com/wallet/generic/use-cases/jwt)
- [Google: acceso de publicación](https://developers.google.com/wallet/generic/test-and-go-live/request-publishing-access)
