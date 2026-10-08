# Micrositio y kit sin Internet

## Entrega

Mantener micrositio, identidad, recursos y URL. Agregar contactos con y sin foto. Incorporar el retrato como JPEG embebido en la vCard; no como URL. No prometer que todas las agendas conservan la foto sin prueba de importación real.

Separar QR al micrositio (el receptor necesita conexión para abrirlo) y QR de datos (nombre, empresa, teléfono, email, URL; sin foto). La cámara puede no reconocer vCard: probar modelos o informar la limitación. No incrustar fotos en el QR ni usar enlaces temporales.

Entregar HTML offline autocontenido con identidad, fotos, datos, QR y contacto embebidos. Guardarlo previamente en Archivos y comprobar apertura en el dispositivo; los visores móviles pueden limitar descargas desde data URI. Guardar también VCF y QR separados. La preparación inicial necesita Internet; mostrar datos guardados no. Libros, PDF, redes y WhatsApp requieren su conexión/servicio. Un recurso solo viaja offline si fue descargado y transferido como archivo.

## Integrar en un sitio estático

Crear `index.html`, `styles.css`, `script.js`, contacto vCard 3.0, retrato y opcional `en.html`. Usar recursos locales con rutas desde `/`. Este generador exige origen dedicado en `/`; rechaza URL con subdirectorio para evitar un despliegue roto. Para subdirectorios, adaptar las rutas y alcance del service worker antes de publicar.

```bash
python3 scripts/build_offline.py --site-dir /ruta/dist \
  --contact contacto.vcf --photo /ruta/retrato.jpg \
  --public-url https://example.org/ --name "Ana Pérez"
```

Conserva la ruta de contacto y la convierte en contacto con foto. Genera variantes, QR de datos y micrositio, HTML autocontenido ES/EN, controles de descarga/compartir y `sw.js`. Usar `--crop left,top,right,bottom` en coordenadas normalizadas para el encuadre. Revisar antes de publicar. No emite Wallet.

«Preparar para usar sin Internet» registra el service worker y verifica los archivos guardados. No afirmar disponibilidad hasta su confirmación. El navegador puede eliminar la caché; HTML/VCF/QR descargados son el respaldo. No pedir al receptor que instale la PWA.

Web Share prepara el archivo antes del gesto. Si el navegador no admite VCF, ofrecer descarga y compartir desde Archivos/Contactos. No presentar una descarga como transferencia confirmada.

## Situaciones

| Conexión | Alternativa |
| --- | --- |
| Ambos online | QR o enlace al micrositio; contacto con/sin foto |
| Emisor offline, receptor online | QR del enlace guardado; conexión del receptor |
| Receptor offline | QR de datos o VCF local por transporte compatible |
| Ambos offline | QR de datos; VCF con foto por AirDrop/Quick Share compatible |
| Equipos incompatibles | QR; foto disponible después desde el micrositio |
| Recursos offline | Solo archivos descargados y transferidos previamente |

Consultar `nearby.md` para plataformas y Wallet.

## Verificar

- Decodificar ambos QR y comparar cargas exactas.
- Parsear VCF/JPEG embebido, comprobar tildes y tamaño moderado (<256 KB como objetivo).
- Revisar HTML autocontenido sin scripts, CSS ni imágenes remotas necesarias.
- Probar rutas, preparación, recarga offline y fallos de compartir si hay navegador.
- Diferenciar automatización de importación de foto y transferencia de radio real.

Fuentes oficiales: [vCard 3.0](https://www.rfc-editor.org/rfc/rfc2426), [Web Share](https://developer.mozilla.org/en-US/docs/Web/API/Web_Share_API), [Service Worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers).
