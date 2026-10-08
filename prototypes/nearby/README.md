# Tarjeta Cerca — prototipo NFC y Bluetooth

Apps nativas para compartir **la URL HTTPS de la tarjeta creada con la skill**. El receptor revisa el enlace y elige abrirlo. No se envía la agenda, no se instala nada a distancia y no se abre el navegador sin intervención.

**Estado: código experimental. Las pruebas de radio en teléfonos reales están pendientes.** La compilación y las pruebas de protocolo se ejecutan en el workflow [Nearby mobile prototype](https://github.com/atrcode/compartir-datos-personales-con-qr./actions/workflows/nearby.yml) del repositorio. Un APK generado permite iniciar la prueba; no certifica interoperabilidad. iOS requiere Mac/Xcode, firma y dispositivo para instalar.

## Qué incluye

| Ruta | Implementación | Condición |
| --- | --- | --- |
| Android → Android, por BLE | Android anuncia GATT y Android lee | Apps abiertas, permisos y hardware BLE compatible |
| Android → iPhone, por BLE | Android anuncia y Core Bluetooth lee | Misma app/protocolo en ambos |
| iPhone → Android, por BLE | Core Bluetooth anuncia y Android lee | iPhone en primer plano durante el envío |
| iPhone → iPhone, por BLE | Core Bluetooth anuncia y lee | Apps abiertas en ambos |
| Android → Android/iPhone, por NFC | Android emula etiqueta Type 4; lectores NDEF en ambas apps | Android con HCE, NFC habilitado, pantallas activas; pendiente validar con hardware |
| iPhone → Android/iPhone, por NFC sin accesorio | No implementado | Core NFC lector no equivale a emisión genérica de una tarjeta Wallet |
| Etiqueta física → Android/iPhone | Generador NDEF en `scripts/build_nfc.py` | Grabar el chip y probar con teléfonos compatibles; receptor sin esta app |

Wallet conserva el pase/QR. Estas apps son un componente adicional; no modifican Apple Wallet ni Google Wallet. Un enlace dentro del pase puede llevar al sitio, pero la instalación o apertura futura de una app requiere integrar y verificar el mecanismo específico de cada plataforma.

## Uso

1. Compilar e instalar las apps de prueba.
2. El emisor pega la URL pública estable que ya usa su QR.
3. Emisor: «Compartir por Bluetooth». Receptor: «Recibir por Bluetooth» y elegir el dispositivo.
4. Verificar el dominio y la URL con el emisor; tocar «Abrir esta tarjeta». Después, el sitio ofrece la vCard, redes y descargas.
5. Para invertir el sentido, cambiar quién comparte y quién recibe.

Para NFC, el Android emisor selecciona «Compartir por NFC» y el receptor abre «Recibir por NFC». Acercar las antenas de los equipos y mantenerlas juntas durante la lectura. Este prototipo no promete activación automática en segundo plano.

Las sesiones de envío duran dos minutos; salir de la app las detiene. El escaneo BLE dura 30 segundos y una conexión, 20. Se transmite una URL pública sin autenticación criptográfica: otros lectores cercanos podrían leerla mientras se comparte. No usar enlaces con tokens privados. La selección del dispositivo y revisión del enlace evitan aperturas automáticas, pero no demuestran la identidad del emisor.

## Compilar Android

Requisitos: JDK 17, Android SDK 35 y Gradle 8.11.1. Se puede abrir `android/` con Android Studio o ejecutar desde la raíz del repositorio:

```sh
gradle -p prototypes/nearby/android :app:assembleDebug
adb install -r prototypes/nearby/android/app/build/outputs/apk/debug/app-debug.apk
```

Mínimo de este prototipo: Android 12/API 31. Usa permisos Nearby Devices en tiempo de ejecución. NFC y BLE no son obligatorios en el manifiesto: la interfaz informa si un transporte falta. El APK de CI es de depuración, sin publicación en Play Store. La app no requiere permiso de Internet: abre el navegador para cargar la tarjeta.

## Compilar iOS

Requisitos: Mac con Xcode compatible, XcodeGen y iPhone con iOS 16 o posterior. Consultar requisitos vigentes para distribución. Desde la raíz:

```sh
brew install xcodegen
xcodegen generate --spec prototypes/nearby/ios/project.yml
open prototypes/nearby/ios/TarjetaCerca.xcodeproj
```

En Xcode seleccionar el equipo de desarrollo, un Bundle ID propio y el iPhone. Habilitar la capacidad **Near Field Communication Tag Reading** en App ID/perfil de firma; el proyecto declara el entitlement NDEF. Permitir Bluetooth al solicitarse. Compilar y ejecutar. El simulador solo sirve para compilar/revisar interfaz: no valida NFC/BLE.

CI compila para simulador con firma desactivada. No genera una app iPhone instalable ni publica en TestFlight. No poner certificados o claves en este repositorio.

## Protocolo BLE v1

- Servicio: `481cf310-1ca4-4c90-b639-14b072d803c7`.
- Característica read-only: `481cf311-1ca4-4c90-b639-14b072d803c7`.
- Valor inmutable por sesión: URL HTTPS, ASCII con escapes `%HH`, máximo 384 bytes. No credenciales, puerto explícito ni espacios. El validador verifica formato, no disponibilidad/DNS.
- Solo se anuncia el UUID del servicio para no exceder el paquete legacy. No se anuncia la URL ni el nombre personal.
- Lectura larga ATT/GATT, con offsets y MTU por conexión en Android; Core Bluetooth responde desde el offset pedido. Validar URLs cortas y de 384 bytes en cada combinación.
- No exige pairing/bonding; no cifra ni autentica por sí solo el enlace. El contenido del sitio se carga posteriormente por HTTPS.

## NFC

Android registra el AID NDEF `D2760000850101` en categoría `other` y solo entrega datos durante una sesión explícita. No se registra como app de pagos. El parser implementa SELECT aplicación, SELECT archivo y READ BINARY; rechaza escritura. CC `E103`, NDEF `E104`, registro URI con prefijo HTTPS. La preferencia de servicio se limita a la actividad visible.

Para etiqueta física:

```sh
python3 scripts/build_nfc.py --profile perfil.json --output entrega-nfc
```

Luego grabar el registro URL en un chip compatible y verificarlo. `tarjeta.ndef` es un mensaje crudo, no un volcado de memoria ni un pase Wallet. No bloquear el chip permanentemente.

## Validación

```sh
python3 -m unittest discover -s tests -v
python3 prototypes/nearby/tests/check_protocols.py java
python3 prototypes/nearby/tests/check_protocols.py swift
```

Los vectores compartidos comprueban validación de URL entre Python, Java y Swift, límites de tamaño y codificación. Java además reconstruye un NDEF largo mediante APDUs y prueba rechazos de escritura/selección inválida. Estas pruebas no simulan radio.

Registrar cada prueba real en [HARDWARE-TESTS.md](HARDWARE-TESTS.md). Pendiente: interoperabilidad BLE en las cuatro combinaciones, lectura NFC HCE desde ambos SO, permisos, interrupciones y modelos con/ sin advertising. No elevar el prototipo a producción hasta completar esa matriz.

Fuentes: [Android BLE](https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview), [permisos](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions), [HCE](https://developer.android.com/develop/connectivity/nfc/hce), [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth), [Core NFC](https://developer.apple.com/documentation/corenfc/nfcndefreadersession). Consultadas el 8 de octubre de 2026.
