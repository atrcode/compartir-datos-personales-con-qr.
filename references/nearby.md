# Compartir por cercanía sin instalar una app en el receptor

Usar el kit de `offline.md` y la misma URL estable. El receptor acepta la transferencia o escanea el QR; no abrir enlaces automáticamente.

| Dirección | Opción nativa | Alternativa |
| --- | --- | --- |
| iPhone → iPhone | AirDrop de VCF local; NameDrop para contacto propio según los campos disponibles | QR de datos/enlace |
| Android → Android | Quick Share de VCF local en equipos compatibles | QR de datos/enlace |
| Android → iPhone | Quick Share ↔ AirDrop solo en Android compatibles | QR de datos/enlace |
| iPhone → Android | Misma interoperabilidad si el Android la admite | QR de datos/enlace |

Transferencia local compatible puede funcionar sin Internet, con Wi-Fi/Bluetooth habilitados. No llamar Bluetooth genérico a AirDrop/Quick Share ni prometer cualquier combinación. El flujo Quick Share de enlace temporal/cloud para equipos sin interoperabilidad requiere Internet; no sustituye el QR de contacto offline.

Desde el micrositio usar Web Share con archivo y detección `canShare`; el sistema elige destinos. Si no admite VCF, descargar y compartir desde Archivos/Contactos. La web no controla el encendido de radio ni garantiza que AirDrop/Quick Share aparezcan. Conservar QR como alternativa.

## NFC y Wallet

Tap to share existe en determinados Android, versiones y modelos; verificar documentación actual. No equivale a emitir tarjetas arbitrarias desde Wallet ni asegura cruce Android/iPhone. Una etiqueta NFC física NDEF URI puede transportar el enlace sin app propia en receptor compatible, pero exige accesorio y el sitio requiere Internet. Preparar `scripts/build_nfc.py` solo si se solicita; no compra ni graba el chip.

Wallet permite guardar y mostrar tarjeta/QR. Apple VAS y Google Smart Tap se orientan a lectores autorizados; no prometen envío NFC universal entre teléfonos. Compartir un pase tampoco equivale a exportar nuestra vCard. Emitir Wallet solo con certificados/emisor autorizados según `wallet.md`.

## Prototipo experimental

La rama `feat/nearby-nfc-ble` del [repositorio](https://github.com/atrcode/compartir-datos-personales-con-qr./) contiene apps BLE emisor/receptor y Android HCE. Requiere apps en ambos teléfonos y **no cumple el requisito de receptor sin instalación**. No recomendarla como flujo principal. Usarla solo si se pide esa modalidad; distinguir código, compilación y pruebas físicas.

## Verificar

Registrar emisor/receptor, modelo, sistema, radios, transporte y resultado. Probar envío con Internet apagado, aceptación, importación y foto. No inferir radio por compilación/test simulado. Si no hay teléfonos, dejar transferencia e importación física pendientes y entregar QR/archivos verificados.

Fuentes oficiales consultadas 2026-10-08; reverificar modelos antes de entrega:

- [Quick Share](https://support.google.com/android/answer/9286773?hl=en)
- [AirDrop](https://support.apple.com/en-us/119857)
- [Interoperabilidad sin servidor](https://blog.google/security/android-quick-share-support-for-airdrop-security/)
- [Tap to share](https://support.google.com/android/answer/17161144?hl=en)
- [Apple Wallet NFC](https://developer.apple.com/wallet/loyalty-passes/)
- [Google Smart Tap](https://developers.google.com/wallet/smart-tap/introduction/communication-flow)
