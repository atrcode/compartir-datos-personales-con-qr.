#!/usr/bin/env python3
"""Prepare a standard NFC URI record. Does not write a physical tag or emit RF."""
import argparse
import json
import re
import struct
from pathlib import Path
from urllib.parse import urlsplit


def validate_url(url):
    if not isinstance(url, str) or not url.startswith('https://') or not 1 <= len(url.encode('utf-8')) <= 384:
        raise ValueError('Se necesita una URL HTTPS de hasta 384 bytes.')
    if not re.fullmatch(r"[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]+", url) or re.search(r'%(?![0-9A-Fa-f]{2})', url):
        raise ValueError('Codificá espacios y caracteres especiales en la URL.')
    parsed = urlsplit(url)
    host = parsed.hostname or ''
    if '.' not in host or parsed.username is not None or parsed.password is not None or parsed.port is not None:
        raise ValueError('Usá un dominio sin credenciales ni puerto.')
    if any(not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label) for label in host.split('.')):
        raise ValueError('Dominio inválido.')
    return url


def ndef_uri(url):
    payload = b'\x04' + validate_url(url)[8:].encode('ascii')  # https:// URI prefix
    header = b'\xd1\x01' + bytes([len(payload)]) if len(payload) <= 255 else b'\xc1\x01' + struct.pack('>I', len(payload))
    return header + b'U' + payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        url = validate_url(json.loads(args.profile.read_text(encoding='utf-8')).get('public_url'))
        data = ndef_uri(url)
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'tarjeta.ndef').write_bytes(data)
    (args.output / 'enlace-nfc.txt').write_text(url + '\n', encoding='utf-8')
    (args.output / 'Grabar-NFC.txt').write_text(
        'PREPARADO; ETIQUETA TODAVÍA NO GRABADA\n\n'
        f'URL: {url}\nNDEF: {len(data)} bytes.\n\n'
        '1. Usá una etiqueta NFC regrabable compatible con NDEF y capacidad suficiente.\n'
        '2. En una app grabadora NFC, agregá un registro URL/URI con la dirección exacta de enlace-nfc.txt.\n'
        '3. Revisá si la etiqueta contiene datos antes de sobrescribirla. No la bloquees de forma permanente.\n'
        '4. Grabá, leé de nuevo y compará la URL exacta.\n'
        '5. Probá en Android e iPhone compatibles, con pantalla encendida y NFC habilitado.\n'
        '6. El receptor toca la notificación y abre la tarjeta. Necesita Internet para cargar el sitio.\n\n'
        'tarjeta.ndef es un mensaje NDEF crudo para herramientas que admitan ese formato.\n'
        'No es una imagen de memoria completa: no escribirlo directamente en páginas de un chip.\n'
        'La capacidad útil necesaria también depende del formato y contenedor de la etiqueta.\n'
        'La etiqueta física emite el enlace; Wallet no se convierte en un emisor NFC.\n', encoding='utf-8')
    print(f'Preparado: {len(data)} bytes NDEF. Grabación y lectura físicas pendientes.')


if __name__ == '__main__':
    main()
