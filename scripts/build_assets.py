#!/usr/bin/env python3
"""Generate contact, QR and email-signature assets; never upload or send mail.

Install qrcode[pil] when generating QR. Use a fresh output directory per version.
"""
import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import quote, urlencode, urlsplit


def text(data, key):
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{key}: se espera texto")
    return value.strip()


def url(value):
    parts = urlsplit(value)
    if (parts.scheme != "https" or not parts.hostname or parts.username
            or parts.password or re.search(r"[\s<>\x00-\x1f]", value)):
        raise ValueError("Usar URL HTTPS absoluta sin credenciales ni espacios")
    return value


def phone(value):
    if not value:
        return ""
    if not re.fullmatch(r"\+[1-9][0-9 .()-]*", value):
        raise ValueError("Teléfono/WhatsApp: aportar número internacional con + y código de país")
    digits = re.sub(r"\D", "", value)
    if not 7 <= len(digits) <= 15:
        raise ValueError("Revisar longitud del teléfono/WhatsApp internacional")
    return "+" + digits


def vescape(value):
    return (value.replace("\\", "\\\\").replace("\r\n", "\n").replace("\r", "\n")
            .replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,"))


def fold(line):
    """Fold at 75 UTF-8 bytes without splitting code points."""
    chunks, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            chunks.append(current)
            current = " "
        current += char
    return "\r\n".join(chunks + [current])


def build(profile, output):
    name = text(profile, "name")
    if not name:
        raise ValueError("Falta name: nombre público de persona o marca")
    public = text(profile, "public_url")
    if public:
        url(public)
    email = text(profile, "email")
    if email and not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", email):
        raise ValueError("Revisar email")
    tel, wa = phone(text(profile, "phone")), phone(text(profile, "whatsapp"))
    color = text(profile, "signature_color") or "#155E63"
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("signature_color debe ser #RRGGBB")
    role, org = text(profile, "role"), text(profile, "organization")
    links = []
    if tel:
        links.append((text(profile, "phone"), "tel:" + tel))
    if email:
        links.append((email, "mailto:" + quote(email, safe="@.+-_")))
    if wa:
        target = "https://wa.me/" + wa[1:]
        message = text(profile, "whatsapp_message")
        if message:
            target += "?" + urlencode({"text": message})
        links.append(("WhatsApp", target))
    for key, label in (("linkedin", "LinkedIn"), ("website", "Web")):
        if text(profile, key):
            links.append((label, url(text(profile, key))))
    if public:
        links.append(("Mi tarjeta de contacto", public))
    for item in profile.get("links", []):
        label = text(item, "label")
        if not label:
            raise ValueError("Cada enlace necesita label")
        links.append((label, url(text(item, "url"))))
    featured = []
    for item in profile.get("resources", []):
        target, title = url(text(item, "url")), text(item, "title")
        if not title:
            raise ValueError("Cada recurso necesita title")
        if item.get("signature") is True:
            featured.append((": ".join(filter(None, (text(item, "action"), title))), target))
    if len(featured) > 1:
        raise ValueError("Elegir como máximo un recurso destacado para la firma")
    links += featured

    family, given = text(profile, "family_name"), text(profile, "given_name")
    structured = [family, given, "", "", ""] if family or given else ["", name, "", "", ""]
    card = ["BEGIN:VCARD", "VERSION:3.0", "FN:" + vescape(name),
            "N:" + ";".join(vescape(part) for part in structured)]
    for key, value in (("ORG", org), ("TITLE", role), ("NOTE", text(profile, "bio"))):
        if value:
            card.append(key + ":" + vescape(value))
    for number in dict.fromkeys(filter(None, (tel, wa))):
        card.append("TEL;TYPE=VOICE:" + number)
    if email:
        card.append("EMAIL;TYPE=INTERNET:" + vescape(email))
    for target in dict.fromkeys(filter(None, (public, text(profile, "website"), text(profile, "linkedin")))):
        card.append("URL:" + url(target))
    card += ["END:VCARD"]

    esc, image_cell = html.escape, ""
    image_url = text(profile, "signature_image_url")
    if image_url:
        url(image_url)
        width, height = profile.get("signature_image_width", 80), profile.get("signature_image_height", 80)
        if any(not isinstance(n, int) or isinstance(n, bool) or not 16 <= n <= 200 for n in (width, height)):
            raise ValueError("Dimensiones de imagen: enteros entre 16 y 200 px")
        image_cell = (f'<td valign="top" style="padding:0 16px 0 0;">'
                      f'<img src="{esc(image_url)}" alt="{esc(org or name)}" '
                      f'width="{width}" height="{height}" style="display:block;border:0;"></td>')
    subtitle = " · ".join(filter(None, (role, org)))
    body = (f'<strong style="font-size:18px;line-height:24px;color:#20252b;">{esc(name)}</strong>'
            + (f'<br><span style="color:#404852;">{esc(subtitle)}</span>' if subtitle else ""))
    for label, target in links:
        body += (f'<br><a href="{esc(target)}" style="color:{color};text-decoration:underline;'
                 f'font-size:13px;line-height:21px;">{esc(label)}</a>')
    signature = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
                 f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                 f'<title>Firma de {esc(name)}</title></head><body>'
                 f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
                 f'style="font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:21px;">'
                 f'<tr>{image_cell}<td valign="top" style="padding:0;">{body}</td></tr></table>'
                 f'</body></html>')
    plain = "\n".join(filter(None, [name, subtitle] + [
        label if target.startswith(("mailto:", "tel:")) else f"{label}: {target}"
        for label, target in links])) + "\n"

    png = svg = None
    if public:
        try:
            import qrcode
            from qrcode.image.svg import SvgPathFillImage
        except ImportError as exc:
            raise ValueError('Instalar qrcode[pil] en este entorno para generar el QR') from exc
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=4)
        qr.add_data(public)
        qr.make(fit=True)
        png = qr.make_image(fill_color="black", back_color="white")
        svg = qr.make_image(image_factory=SvgPathFillImage)

    output.mkdir(parents=True, exist_ok=True)
    (output / "contacto.vcf").write_bytes(("\r\n".join(fold(line) for line in card) + "\r\n").encode("utf-8"))
    (output / "firma-email.html").write_text(signature, encoding="utf-8")
    (output / "firma-email.txt").write_text(plain, encoding="utf-8")
    if public:
        png.save(output / "qr-contacto.png")
        svg.save(str(output / "qr-contacto.svg"))
    return {"contacto": "generado", "firma": "generada", "qr": "generado" if public else "pendiente de URL estable"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            raise ValueError("El perfil debe ser un objeto JSON")
        print(json.dumps(build(profile, args.output), ensure_ascii=False))
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f"No se completó el paquete: {exc}\n")


if __name__ == "__main__":
    main()
