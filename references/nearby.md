# Compartir la tarjeta por NFC y Bluetooth

Usar la misma `public_url` estable del sitio, QR y Wallet. No fabricar URL temporal ni copiar todos los datos personales al canal de radio. El enlace es público; el receptor decide abrirlo y luego guardar la vCard.

## Elegir según la experiencia

- **Sin app en el receptor:** preparar una etiqueta/tarjeta NFC física con registro NDEF URI HTTPS. Puede llevarse pegada a una funda compatible. El lector es un Android o iPhone compatible; verificar modelo, antena y configuración. No decir que Wallet o el teléfono emiten cuando lo hace la etiqueta.
- **Teléfono a teléfono en las cuatro combinaciones:** usar una app nativa con Bluetooth Low Energy (BLE), rol periférico/GATT servidor para compartir y central/GATT cliente para recibir. Ambas apps deben estar abiertas y tener permisos. No necesita emparejamiento manual; sí selección del dispositivo y confirmación antes de abrir la URL. Es una arquitectura viable, no una función automática de Wallet ni del sitio web.
- **NFC con Android emisor:** prototipar HCE de etiqueta Type 4/NDEF; recibir con Android lector o Core NFC en iPhone. Comprobar en hardware ambas direcciones soportadas por el código antes de anunciar compatibilidad.
- **iPhone emisor NFC sin accesorio:** no prometerlo con una skill, un pase genérico o un permiso Core NFC lector. Las plataformas NFC/HCE de Apple tienen ámbitos, dispositivos, regiones, acuerdos y autorizaciones específicas; verificar documentación vigente si se propone otra ruta.

Si falta resolver la modalidad, preguntar una sola cosa: «¿La persona que recibe puede tener una app instalada, o tiene que funcionar sin instalar nada?». No repetirla si la conversación ya lo resuelve. Mientras tanto completar URL, QR y preparación NFC independientes.

## Preparar la etiqueta

```bash
python3 scripts/build_nfc.py --profile /ruta/perfil.json --output /ruta/entrega-nfc
```

Genera `tarjeta.ndef`, `enlace-nfc.txt` y `Grabar-NFC.txt`. El `.ndef` es el mensaje crudo, no un volcado del chip. El script valida formato HTTPS/ASCII y máximo 384 bytes; no comprueba DNS ni publicación. Usar URLs con caracteres escapados cuando corresponda. No compra, graba ni bloquea etiquetas. Grabar un registro URL con una herramienta NFC y confirmar capacidad útil y permiso antes de reemplazar contenido existente. No bloquear permanentemente por defecto.

## Prototipo de aplicación

El repositorio [compartir-datos-personales-con-qr.](https://github.com/atrcode/compartir-datos-personales-con-qr./) contiene el trabajo de `prototypes/nearby` en la rama `feat/nearby-nfc-ble` mientras esté en evaluación. Revisar su README y el estado de compilación antes de reutilizarlo. La skill no instala apps en teléfonos, no emite certificados iOS y no publica en tiendas automáticamente.

El prototipo implementa BLE con una URL pública de hasta 384 bytes ASCII, lectura GATT larga con offsets, descubrimiento por UUID, sesión de envío de dos minutos, selección de receptor y apertura manual. Android incluye servicio NFC HCE y lector; iOS incluye lector Core NFC. No afirmar soporte BLE de todos los modelos: comprobar advertising, lectura larga y permisos en dispositivos concretos. No presentar intensidad RSSI como distancia exacta ni cercanía como prueba de identidad.

## Verificación y entrega

- Separar estados: código preparado, compilado, instalado, probado entre dispositivos y distribuido.
- Registrar emisor, receptor, SO/modelo, transporte, longitud URL, resultado exacto y consentimiento. Probar Android→Android, Android→iPhone, iPhone→Android e iPhone→iPhone para BLE; NFC HCE solo con Android emisor.
- Probar permisos denegados, radio apagada, tiempo agotado, salir de la app, varios emisores y URL larga. No abrir automáticamente URLs recibidas; mostrar el enlace completo.
- Para NFC físico, comparar lectura exacta del chip y probar en ambos sistemas. Para BLE, leer una característica no acredita por sí solo las cuatro combinaciones.
- Entregar el instructivo de la modalidad elegida y declarar toda prueba pendiente. Conservar QR como alternativa.

## Fuentes oficiales (consultadas 2026-10-08)

- Android HCE: https://developer.android.com/develop/connectivity/nfc/hce
- Android BLE: https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview
- Permisos Android: https://developer.android.com/develop/connectivity/bluetooth/bt-permissions
- Core Bluetooth: https://developer.apple.com/documentation/corebluetooth
- Restricciones al pasar iOS a segundo plano: https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html
- Core NFC: https://developer.apple.com/documentation/corenfc/nfcndefreadersession
- NFC y Secure Element: https://developer.apple.com/support/nfc-se-platform/

Reverificar restricciones, versiones y requisitos antes de una entrega de producción.
