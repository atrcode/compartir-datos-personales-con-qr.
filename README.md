# Tarjeta digital, QR y firma de email

Skill abierta para asistentes compatibles con `SKILL.md`. Ayuda a crear un sitio móvil de contacto, una vCard, un QR que abre el sitio, una firma HTML y de texto, y un instructivo de instalación adaptado al correo y dispositivo de la persona.

> El QR definitivo requiere una URL HTTPS pública y estable. El script no construye ni publica el sitio: la skill guía ese trabajo y `scripts/build_assets.py` produce los archivos complementarios.

## Instalación

1. Descargá o cloná este repositorio.
2. En ChatGPT, importá la carpeta como skill desde la sección de Skills (o comprimila como ZIP si la interfaz pide un archivo). En Codex u otro agente compatible, ubicá la carpeta en el directorio de skills que indique esa aplicación.
3. Pedí: «Usá @compartir-datos-personales-con-qr para hacer mi tarjeta, QR y firma de Gmail».

El asistente irá pidiendo los datos de a uno. No necesitás completar todos los campos: logo, foto, redes y materiales son opcionales. La publicación del sitio depende del acceso a un hosting que elijas.

## Ejecución manual del generador

Requiere Python 3.10+ y `qrcode[pil]`:

```bash
python3 -m pip install -r requirements.txt
cp references/profile.example.json perfil.json
# Editá perfil.json con tus datos; mantenelo fuera del repositorio.
python3 scripts/build_assets.py --profile perfil.json --output entrega-v1
```

Con `public_url` genera `contacto.vcf`, `firma-email.html`, `firma-email.txt`, `qr-contacto.png` y `qr-contacto.svg`. Sin `public_url` genera la vCard y firmas; el QR queda pendiente. Publicá el sitio y verificá su URL antes de distribuir el QR.

El archivo `references/profile.example.json` contiene datos ficticios. No subas perfiles reales, fotografías, credenciales ni entregas generadas a este repositorio.

## Alcance y estructura

- [`SKILL.md`](SKILL.md): conversación, diseño, publicación y controles de calidad.
- [`references/intake.md`](references/intake.md): datos a recopilar de a un paso.
- [`references/email-install.md`](references/email-install.md): fuentes para instructivos de firmas.
- [`references/profile.example.json`](references/profile.example.json): contrato de datos ficticio.
- [`scripts/build_assets.py`](scripts/build_assets.py): generador reproducible.

La firma no se instala automáticamente en una cuenta y el script no envía correos. Las instrucciones de cada cliente se verifican con documentación oficial al hacer una entrega.

## Colaborar

Se aceptan reportes de problemas y propuestas mediante Issues y Pull Requests. Leé [`CONTRIBUTING.md`](CONTRIBUTING.md) para ejecutar las pruebas y proponer cambios. Licencia MIT: [`LICENSE`](LICENSE).
