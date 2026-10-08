---
name: compartir-datos-personales-con-qr
description: Crear y actualizar una tarjeta digital con sitio móvil, QR, contacto vCard, firma de email y opción de agregarla a Apple Wallet en iPhone o Google Wallet en Android, con instructivos adaptados al usuario. Usar para QR de contacto, sitio de firma, tarjeta de presentación, página de enlaces, pases Wallet o kits como BeBlend y Surtank. Recopilar logo, foto, bio, WhatsApp, email, LinkedIn, web y materiales mediante una pregunta por vez; preparar la emisión y comprobar los requisitos de cada Wallet.
---

# Crear tarjeta digital, QR, firma de email y Wallet

## Entregables

Crear un conjunto coherente con la identidad de cada persona o marca:
1. Micro sitio móvil con datos, enlaces, materiales y botón «Guardar contacto».
2. QR real en PNG y SVG que abra la dirección estable del sitio.
3. Contacto descargable `.vcf` con todos los datos cargados.
4. Firma de email en HTML copiable y texto plano. Con identidad visual seleccionada. 
5. Instructivo de instalación para el servicio, aplicación y dispositivo declarados.
6. Opcional: pase de contacto para Apple Wallet (iOS) y/o Google Wallet (Android), botones para agregarlo desde el sitio e instructivo de instalación. Emitir el pase final cuando estén disponibles los requisitos de la plataforma; de lo contrario, entregar el diseño y la preparación con el requisito pendiente identificado.

Limitar el trabajo a los entregables solicitados si se pide solo una parte. Para cambios, preservar identidad, URL y QR existentes; no reconstruir el sitio por cambiar un teléfono o firma si no es necesario.

## 1. Recopilar mediante conversación

- Usar el idioma del usuario; español rioplatense por defecto.
- Preguntar **un dato o decisión por mensaje**. Registrar todos los datos cuando una respuesta incluya varios; no volver a pedirlos ni presentar un formulario completo.
- Si falta la identidad, comenzar: «¿Para qué persona o marca hacemos la tarjeta y qué nombre querés mostrar?».
- Seguir [references/intake.md](references/intake.md). Aceptar «saltear», «no tengo» y «usá tu criterio» en campos opcionales; retomar el siguiente dato pendiente.
- Si el usuario pide avanzar, producir lo posible con lo recibido y omitir campos opcionales ausentes. No bloquear por logo, foto, redes, bio o descargables.
- Ofrecer redactar la mini bio con hechos aportados. No inventar credenciales, contactos ni obras. 
- Distinguir servicio de correo, aplicación y dispositivo. Una cuenta Gmail puede usarse en Outlook. «Email corporativo» o su dominio no identifican el editor de firmas.
- Ofrecer la opción Wallet una vez: «¿Querés poder guardar la tarjeta en Apple Wallet, Google Wallet, ambas o ninguna?». Si ya se pidieron Android e iOS, registrar ambas sin volver a preguntar. Usar la misma identidad y URL del sitio; no repetir la entrevista para crear los pases.
- Si se mencionan otros trabajos anteriores, recuperar las referencias disponibles mediante herramientas de contexto, archivos o repositorio pertinentes. No afirmar que se vio un diseño sin leerlo. Si la semejanza exacta importa y falta la referencia, pedir su URL/captura; en otros casos continuar con la identidad aportada.
- Tratar marcas anteriores como ejemplos de flujo, sin copiar sus datos o activos a otra persona. No guardar datos de clientes en esta skill.

## 2. Preparar contenido e identidad

- Mantener un perfil por persona fuera del código público del sitio. Usar [references/profile.example.json](references/profile.example.json) como contrato de datos, reemplazando los valores ficticios. Omitir campos opcionales ausentes.
- Conservar el nombre tal como se solicite. No adivinar su separación en nombre/apellido; el generador admite el nombre completo.
- Pedir WhatsApp en formato internacional cuando sea ambiguo. No agregar/quitar prefijos locales por suposición. Generar `wa.me` con dígitos y codificar el mensaje opcional.
- Preguntar si tiene una guía de imgen de marca para que pueda subirla en varios formatos y basarse en esas referencias. Tambien ofrecer buscar estos lineamientos de marca en la web determinda. 
- Revisar contactos y URLs. Usar HTTPS estable para el sitio y los recursos públicos. No usar enlaces sandbox, URLs de sesión ni enlaces con vencimiento para el QR final o las imágenes de firma.
- Pedir y usar logo y retrato (foto personal) reales conservando proporción. Si faltan, usar una composición tipográfica. Respetar paleta de marca y contraste legible; separar color de marca del color de texto si hace falta.
- Distinguir «Leer artículo», «Descargar PDF» y «Comprar libro». Una página no equivale a una descarga. No publicar un libro completo solo porque se aportó como referencia; usar los materiales destinados a distribución.

## 3. Construir y publicar el sitio

- Usar las skills de construcción/hosting disponibles. Preguntar donde quiere desplegar el sitio. Si no sabe o no tiene usar herramientas para explicarle el paso a paso y proponer despliegue automatico. Para un sitio existente, conservar proyecto y plataforma actuales; respetar la plataforma ya elegida.
- Crear una página con nombre, rol/empresa, logo/foto disponibles, mini bio, «Guardar contacto», WhatsApp, email, redes, web y materiales. Ocultar bloques vacíos; no dejar placeholders ni enlaces `#`.
- Usar HTML semántico, navegación por teclado, texto alternativo y botones cómodos. Revisar móvil de 360 px y escritorio sin desbordamiento.
- Servir `.vcf` y materiales autorizados en rutas estables. Para PDF externos sin descarga garantizada, rotular «Abrir PDF». Probar rutas desde una sesión pública sin login.
- No agregar captura de leads, pagos, analítica o protección de descargas por defecto. Si se piden, tratarlo como alcance adicional y verificarlo realmente.
- Preparar una vista previa concreta y publicar cuando esté autorizado por la solicitud o sesión. Si falta hosting/acceso, completar primero el sitio y la firma en vista previa, guardar el paquete y precisar lo que falta. No afirmar publicación sin URL comprobada.
- Resolver primero la URL final estable y después generar el QR definitivo. Nunca usar un preview temporal como destino final. Si el QR circula, conservar su ruta o configurar y verificar una redirección antes de cambiarla.
- Si se solicita Wallet, integrar sus botones oficiales siguiendo el paso 6. Mostrar cada botón operativo únicamente cuando exista un destino válido; no enlazar un QR PNG o una vCard como si fueran un pase Wallet.

## 4. Generar contacto, QR y firma

Ejecutar desde el directorio real de esta skill:

```bash
python3 scripts/build_assets.py --profile /ruta/perfil.json --output /ruta/entrega
```

Instalar `qrcode[pil]` en el entorno si falta. El script genera `contacto.vcf`, `firma-email.html`, `firma-email.txt` y, cuando hay `public_url`, `qr-contacto.png` y `qr-contacto.svg`. No construye ni publica el sitio ni emite pases Wallet: integrar estos archivos en la página creada y ejecutar el flujo Wallet del paso 6 si se solicitó. Sin URL estable, generar los otros archivos y dejar el QR pendiente. Usar una carpeta de salida nueva por versión para no confundir archivos anteriores.

- Generar QR con software, nunca con un modelo de imágenes. Mantener módulos nítidos, alto contraste y margen libre de cuatro módulos. No superponer logo por defecto; si se personaliza, volver a decodificar.
- Decodificar el PNG con una biblioteca independiente o lector disponible y comparar con la URL final exacta. Si falta decodificador, declarar pendiente la prueba de lectura; no reemplazarla por mirar la imagen. Revisar también el SVG.
- Comprobar UTF-8, tildes, nombre, teléfonos y URLs del `.vcf`. Probar importación cuando sea posible; no afirmar pruebas iOS/Android sin realizarlas.
- Diseñar la firma con tabla HTML, estilos inline y fuentes comunes. Mantener texto seleccionable y enlaces reales; no convertir toda la firma en una imagen.
- Usar imágenes PNG/JPEG con URL HTTPS pública estable y dimensiones proporcionadas. No usar SVG, base64 ni rutas locales en la firma. Conservar legibilidad con imágenes bloqueadas.
- Priorizar nombre, rol/empresa, teléfono/email y enlaces elegidos. Destacar como máximo un material; dejar el catálogo completo en el sitio. Incluir QR en firma solo si se pide.
- Entregar HTML renderizable y texto plano. Si faltan imágenes públicas, terminar versión de texto y estructura HTML; especificar esa limitación sin inventar imágenes alojadas.

## 5. Crear instructivo de instalación

Leer [references/email-install.md](references/email-install.md). Verificar los pasos vigentes en documentación oficial de la aplicación y versión antes de redactarlos. No entregar una lista genérica de proveedores cuando se conoce el destino.

Crear `Instalar-firma-<aplicacion>.html` autocontenido, con: aplicación/dispositivo, archivo que abrir, qué copiar (firma renderizada cuando corresponda, no código fuente), pasos numerados, selección para mensajes nuevos/respuestas, guardado, comprobación visual y soluciones habituales. Incluir fuentes oficiales y fecha de consulta. Usar texto plano si el editor no admite HTML; no prometer paridad móvil/escritorio ni sincronización sin verificarla.

No instalar en una cuenta, reemplazar firmas existentes ni enviar correos de prueba por el solo pedido de crear el kit. Hacerlo si el usuario lo pide o ya está autorizado. En caso contrario, incluirlo como pasos del instructivo.

## 6. Agregar la opción Apple Wallet y Google Wallet

Leer [references/wallet.md](references/wallet.md) cuando se solicite esta opción. Preparar un pase de presentación con nombre, rol/marca, identidad visual y QR a la misma URL estable. Mantener WhatsApp, enlaces y descargables completos en el sitio y conservar «Guardar contacto» como una acción separada.

- Recopilar solo los requisitos que falten para la modalidad elegida, de a uno: emisión propia o proveedor existente, identificadores y acceso seguro a credenciales. No pedir claves privadas en el chat ni guardarlas en el perfil público.
- Para iPhone, generar y firmar un `.pkpass` válido; para Android, emitir un pase genérico de Google Wallet con enlace de guardado firmado. Seguir documentación oficial vigente o la integración de un proveedor ya autorizado.
- Si faltan certificados, cuenta emisora o acceso de publicación, completar diseño, datos del pase, integración preparada e instructivo de habilitación. Declarar qué falta; no llamar «instalable» a una plantilla sin firmar ni «público» a un pase de prueba.
- Reutilizar cuentas y servicios disponibles. Si se necesita contratar una suscripción o un servicio pago, preparar primero la alternativa y explicar su costo antes de solicitar esa contratación; no prometer gratuidad sin verificarla.
- Crear `Instalar-tarjeta-Wallet.html` con pasos para cada plataforma elegida, enlaces válidos de instalación, cómo abrir la tarjeta y mostrar el QR. No prometer NFC ni actualización automática del contenido del pase por actualizar el sitio.

## 7. Verificar, guardar y entregar

- Comprobar datos consistentes entre sitio, `.vcf` y firma; enlaces/descargas reales; lectura y destino del QR; recursos sin login; móvil y firma renderizada.
- Distinguir «generado», «publicado», «verificado» e «instalado». Una vista previa en navegador no certifica todos los clientes de email. No dar por probado un mensaje que no se envió.
- Para Wallet, verificar firma/emisor, apertura del flujo «Agregar», contenido visible y destino del QR; diferenciar validación técnica de instalación real en dispositivo. Informar por separado el estado de Apple y Google, y si el pase es de prueba o producción.
- Guardar archivos entregables mediante la skill Library, salvo código ya respaldado por el repositorio del proyecto. Mantener el perfil privado y credenciales fuera de assets públicos. Guardar esta skill con el mecanismo de skills, no Library.
- Entregar enlaces al sitio, QR PNG/SVG, `.vcf`, firma HTML/texto e instructivo. Usar enlaces locales absolutos donde corresponda. Agregar ZIP si se pide o facilita la entrega, sin reemplazar los enlaces principales.
- Si se eligió Wallet, entregar además `.pkpass` firmado y/o enlace de Google Wallet, instructivo y estado de validación. Si la emisión sigue pendiente, entregar únicamente la preparación claramente rotulada y el paso concreto para habilitarla.
- Cerrar brevemente con cómo usar el kit y bloqueos reales. No pedir confirmación adicional para guardar una entrega ya solicitada.
