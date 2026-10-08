# Actualizaciones · 2026-10-08

## Micrositio y kit offline

Se conserva el micrositio como presentación completa online y se agrega contacto/QR guardado para el intercambio sin conexión. El QR de datos transporta nombre, organización, teléfono, email y URL, sin foto. El VCF con foto incorpora JPEG local, con opción de descargar una versión sin foto.

El sitio ofrece archivo HTML autocontenido, descarga de QR, compartir VCF mediante el menú nativo y preparación de caché. Si la API del navegador no admite el archivo, indica descargarlo y compartir desde Archivos/Contactos. El receptor no necesita instalar una app del proyecto. La caché se confirma solo cuando los archivos están presentes; puede eliminarse por el navegador, por eso se ofrecen archivos descargables como respaldo.

Se agrega generador `build_offline.py`, versiones estáticas español/inglés y documentación en ambos idiomas. La integración offline requiere origen dedicado `/`; rechaza subdirectorios en vez de producir rutas incorrectas. Wallet sigue sujeto a emisión válida; no se habilitan botones ficticios ni NFC universal.

## Proyectos actualizados

| Micrositio | Dirección conservada | Imágenes antes | Imágenes optimizadas | Reducción |
| --- | --- | ---: | ---: | ---: |
| Paula Luiggi | https://paula-luiggi.ideal-clove-2036.chatgpt.site | 3.61 MB | 0.21 MB | 94.1 % |
| Carolina Dalul | https://carolina-dalul.ideal-clove-2036.chatgpt.site | 3.32 MB | 0.20 MB | 94.0 % |
| Leandro · SURTANK | https://tarjeta.mocchegiani.com.ar | 1.23 MB | 0.09 MB | 92.8 % |

Las cifras corresponden a bytes de imágenes referenciadas en pantalla, con MB decimales; no son tiempo de carga ni puntuación Lighthouse. Se conservan originales. Las páginas inglesas usan `/en.html`. Las biografías, ayudas y botones están traducidos; libros y PDF mantienen sus versiones existentes.

## Verificación y límites

- 10 pruebas Python: generación, URLs, NDEF, QR sin URL, foto/HTML offline e integración repetida.
- 5 pruebas Node: compartir archivo, falta de soporte, cancelación/error, caché completa/incompleta y respuesta desde caché sin red.
- QR de las tres tarjetas decodificados con lector independiente; vCards y JPEG embebidos parseados.
- Comprobación de rutas de caché, HTML autocontenido e idioma; JS validado sintácticamente.
- Prueba independiente de la skill con persona ficticia y archivos aislados.

Pendientes de prueba real: render móvil/escritorio, preparación y recarga en navegador real, apertura del HTML en visores móviles, conservación de foto en agendas y transferencia AirDrop/Quick Share/NFC entre teléfonos. Los tests de código no certifican compatibilidad universal.

## English summary

The updated kit combines the full online microsite with locally saved contact files, embedded contact photos, a basic offline contact QR and self-contained HTML cards. Static Spanish/English pages retain the existing URLs and branding. Referenced image bytes dropped by 92.8–94.1%; these are size measurements, not Lighthouse scores. Native sharing depends on the device/browser, with download and QR fallbacks. Real browser rendering, contact-photo imports and phone radio transfers remain unverified.

Las fuentes de SURTANK se alojan localmente con sus licencias abiertas y se incorporan al HTML offline para conservar la tipografía sin depender de Google Fonts. Los HTML autocontenidos resultantes pesan aproximadamente 0.40–0.43 MB; se recomienda guardar también VCF y QR por separado.
