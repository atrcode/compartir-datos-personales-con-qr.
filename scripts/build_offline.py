#!/usr/bin/env python3
"""Add a portable offline card and photo contact to an existing static microsite.

Requires beautifulsoup4, Pillow and qrcode. No network calls or Wallet issuance.
Run after editing index.html and optional en.html, before packaging the site.
"""
import argparse
import base64
import hashlib
import html
import io
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import qrcode
from qrcode.image.svg import SvgPathFillImage


def fold(line):
    lines, current = [], ''
    for c in line:
        if len((current + c).encode('utf-8')) > 75:
            lines.append(current)
            current = ' '
        current += c
    return '\r\n'.join(lines + [current])


def qr(payload, target):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=4)
    code.add_data(payload)
    code.make(fit=True)
    code.make_image(fill_color='black', back_color='white').save(target.with_suffix('.png'))
    code.make_image(image_factory=SvgPathFillImage).save(str(target.with_suffix('.svg')))


def embedded(path):
    suffix = path.suffix.lower()
    mime = {'.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.vcf':'text/vcard','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf'}[suffix]
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


LABELS = {
 'es': ['Guardar contacto con foto','Guardar sin foto','QR de contacto · sin Internet','Este QR contiene datos básicos, sin foto. La compatibilidad de lectura depende de la cámara.','Descargar tarjeta offline','Compartir contacto con foto','Preparar para usar sin Internet','Compartí el archivo con AirDrop o Quick Share si los equipos son compatibles. Si no, mostrales el QR.','Micrositio · requiere Internet','Descargar QR de contacto'],
 'en': ['Save contact with photo','Save without photo','Contact QR · no Internet needed','This QR contains basic details, without a photo. Camera support varies.','Download offline card','Share contact with photo','Prepare for offline use','Share the file with AirDrop or Quick Share on compatible phones. Otherwise, show the QR.','Microsite · Internet required','Download contact QR']
}


def build(site, contact, photo, public, name, crop=None):
    parts = urlsplit(public)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or re.search(r'[\s<>\x00-\x1f]', public):
        raise ValueError('public_url must be a stable HTTPS URL')
    if parts.path not in ('', '/'):
        raise ValueError('This static-site integration requires a dedicated origin at /. For subdirectory hosting, adapt the base paths before deployment.')
    original = site / contact
    raw = original.read_text(encoding='utf-8')
    lines = re.sub(r'\r?\n[ \t]', '', raw).splitlines()
    if lines[:2] != ['BEGIN:VCARD','VERSION:3.0'] or lines[-1] != 'END:VCARD':
        raise ValueError('Expected a vCard 3.0 contact')
    lines = [line for line in lines if not line.upper().startswith('PHOTO')]
    if not any(line == 'URL:' + public for line in lines):
        lines.insert(-1, 'URL:' + public)
    without = '\r\n'.join(fold(line) for line in lines) + '\r\n'
    (site/'contacto-sin-foto.vcf').write_bytes(without.encode('utf-8'))
    image = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    if crop:
        image = image.crop(tuple(round(v*d) for v,d in zip(crop,[image.width,image.height,image.width,image.height])))
    image = ImageOps.fit(image,(320,320),method=Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    image.save(buf,format='JPEG',quality=82,optimize=True)
    lines.insert(-1,'PHOTO;ENCODING=b;TYPE=JPEG:' + base64.b64encode(buf.getvalue()).decode('ascii'))
    with_photo = '\r\n'.join(fold(line) for line in lines) + '\r\n'
    (site/'contacto-con-foto.vcf').write_bytes(with_photo.encode('utf-8'))
    # Preserve the established contact URL; default import now includes the photo.
    original.write_bytes(with_photo.encode('utf-8'))
    basic = ['BEGIN:VCARD','VERSION:3.0'] + [l for l in lines if l.startswith(('N:','FN:','ORG:','TEL','EMAIL'))] + ['URL:' + public,'END:VCARD']
    payload = '\r\n'.join(basic) + '\r\n'
    (site/'contacto-qr.vcf').write_bytes(payload.encode('utf-8'))
    qr(payload,site/'assets/qr-contacto-datos')
    qr(public,site/'assets/qr-micrositio')
    css = '''.offline-tools{margin:18px 0;padding:18px;border:1px solid currentColor;border-radius:16px}.offline-tools summary{cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center}.offline-tools a,.offline-tools button{display:block;width:100%;padding:12px;margin:8px 0;border:1px solid currentColor;border-radius:10px;background:transparent;color:inherit;text-align:center;line-height:1.4;overflow-wrap:anywhere}.offline-tools p{font-size:.85rem;line-height:1.5}.offline-tools img{margin:12px auto;width:min(100%,300px);height:auto;background:white}.language-nav{display:flex;gap:10px;justify-content:flex-end;margin:0 0 12px}.language-nav a{padding:8px 12px;border:1px solid currentColor;border-radius:8px}.offline-status{font-size:.85rem;line-height:1.5}.offline-hint{font-size:.85rem;line-height:1.5;opacity:.8}@media(max-width:420px){.topbar{gap:8px}.share-trigger,.share-button{font-size:.75rem}.offline-tools{padding:12px}}'''
    (site/'offline.css').write_text(css,encoding='utf-8')
    # File preparation happens ahead of the gesture to retain native-share activation.
    js = '''(()=>{'use strict';const en=document.documentElement.lang.startsWith('en');const say=(es,enText)=>en?enText:es;let file;const share=document.querySelector('[data-share-contact]');const status=document.querySelector('[data-offline-status]');const msg=t=>{if(status)status.textContent=t};fetch('/contacto-con-foto.vcf').then(r=>{if(!r.ok)throw Error();return r.blob()}).then(b=>{file=new File([b],'contacto-con-foto.vcf',{type:'text/vcard'})}).catch(()=>{});share?.addEventListener('click',async()=>{if(!file||!navigator.canShare?.({files:[file]})){msg(say('Descargá el contacto y compartilo desde Archivos o Contactos.','Download the contact and share it from Files or Contacts.'));return}try{await navigator.share({files:[file]})}catch(e){if(e.name!=='AbortError')msg(say('Descargá el contacto y compartilo desde Archivos o Contactos.','Download the contact and share it from Files or Contacts.'))}});document.querySelector('[data-prepare-offline]')?.addEventListener('click',async()=>{if(!('serviceWorker'in navigator)){msg(say('Descargá la tarjeta offline para guardarla en el celular.','Download the offline card to keep it on your phone.'));return}msg(say('Preparando…','Preparing…'));try{const reg=await navigator.serviceWorker.register('/sw.js');let worker=reg.installing||reg.waiting||reg.active;if(worker&&worker.state!=='activated'){await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error()),30000);worker.addEventListener('statechange',()=>{if(worker.state==='activated'){clearTimeout(timer);resolve()}else if(worker.state==='redundant'){clearTimeout(timer);reject(Error())}})})}const cached=await caches.open(window.CARD_CACHE);const paths=window.CARD_OFFLINE_FILES;const found=await Promise.all(paths.map(p=>cached.match(p)));if(found.some(r=>!r))throw Error();msg(say('Tarjeta lista para usar offline en este navegador. Guardá también el HTML y el contacto como respaldo; el navegador puede borrar su almacenamiento.','Card ready offline in this browser. Also save the HTML and contact as a backup; browser storage can be cleared.'))}catch{msg(say('No se completó la preparación. Descargá la tarjeta offline y el contacto.','Preparation was not completed. Download the offline card and contact.'))}})})();'''
    (site/'offline.js').write_text(js,encoding='utf-8')
    for page in ['index.html','en.html']:
        if not (site/page).exists():
            continue
        soup = BeautifulSoup((site/page).read_text(encoding='utf-8'),'html.parser')
        lang = 'en' if page=='en.html' else 'es'
        labels = LABELS[lang]
        for old in soup.select('[data-offline-tools],.contact-photo-choice,.language-nav,link[href="/offline.css"],script[src="/offline.js"],script[data-offline-config]'):
            old.decompose()
        nav = soup.new_tag('nav',attrs={'class':'language-nav','aria-label':'Language / Idioma'})
        for target,title in [('/','ES'),('/en.html','EN')]:
            a=soup.new_tag('a',href=target);a.string=title
            if (lang=='es' and target=='/') or (lang=='en' and target=='/en.html'): a['aria-current']='page'
            nav.append(a)
        soup.select_one('main').insert(0,nav)
        tools = BeautifulSoup(f'''<details class="offline-tools" data-offline-tools><summary>{labels[6]}</summary><p class="offline-hint">{labels[7]}</p><a href="/contacto-con-foto.vcf" download>{labels[0]}</a><a href="/contacto-sin-foto.vcf" download>{labels[1]}</a><button type="button" data-share-contact>{labels[5]}</button><button type="button" data-prepare-offline>{labels[6]}</button><a href="/tarjeta-offline{'-en' if lang=='en' else ''}.html" download>{labels[4]}</a><h3>{labels[2]}</h3><img src="/assets/qr-contacto-datos.svg" width="300" height="300" alt="{labels[2]}" loading="lazy"><p>{labels[3]}</p><a href="/assets/qr-contacto-datos.png" download>{labels[9]}</a><p class="offline-status" data-offline-status role="status" aria-live="polite"></p></details>''','html.parser').details
        soup.select_one('main').append(tools)
        link=soup.new_tag('link',rel='stylesheet',href='/offline.css');soup.head.append(link)
        script=soup.new_tag('script',src='/offline.js',defer=True);soup.head.append(script)
        for a in soup.select('a.save-contact'):
            for node in list(a.find_all(string=True)):
                if node.strip():node.replace_with(labels[0])
            choice=soup.new_tag('a',attrs={'class':'contact-photo-choice','href':'/contacto-sin-foto.vcf','download':'contacto-sin-foto.vcf','style':'display:block;font-size:.85rem;text-decoration:underline;padding:10px 0;line-height:1.4'})
            choice.string=labels[1]
            a.insert_after(choice)
        for p in soup.select('.dialog-subtitle'):
            p.string=labels[8]
        # Self-contained HTML: stable public links, data-URI photos, QR and contact.
        portable=BeautifulSoup(str(soup),'html.parser')
        for script in portable.find_all('script'):script.decompose()
        for modal in portable.find_all('dialog'):
            modal.name='section';modal['class']=['offline-tools'];modal.attrs.pop('open',None)
        for control in portable.select('button'):
            control.decompose()
        for link in portable.select('link[rel="stylesheet"]'):
            source=site/link['href'].lstrip('/')
            css_text=source.read_text(encoding='utf-8')
            css_text=re.sub(r'@import\s+[^;]+;', '', css_text)
            css_text=re.sub(r'url\(([\'"]?)(/[^)\'"]+)\1\)', lambda m:'url('+embedded(site/m.group(2).lstrip('/'))+')', css_text)
            style=portable.new_tag('style');style.string=css_text;link.replace_with(style)
        for image in portable.find_all('img'):
            src=image.get('src','')
            if src.startswith('/'):
                image['src']=embedded(site/src.lstrip('/'))
                image.attrs.pop('loading',None)
        for a in portable.find_all('a',href=True):
            href=a['href']
            if href.startswith('/'):
                local=site/href.lstrip('/')
                if local.exists() and local.suffix in ('.vcf','.png','.svg'):
                    a['href']=embedded(local);a['download']=local.name
                else:a['href']=public.rstrip('/')+href
        portable.select_one('[data-offline-tools]')['open']=''
        offline_name='tarjeta-offline' + ('-en' if lang=='en' else '') + '.html'
        (site/offline_name).write_text(str(portable),encoding='utf-8')
        (site/page).write_text(str(soup),encoding='utf-8')
    files=['/','/index.html','/styles.css','/script.js','/offline.css','/offline.js','/contacto-con-foto.vcf','/contacto-sin-foto.vcf','/'+contact,'/tarjeta-offline.html']
    if (site/'en.html').exists():files+=['/en.html','/tarjeta-offline-en.html']
    for page in ['index.html','en.html']:
        if (site/page).exists():
            soup=BeautifulSoup((site/page).read_text(encoding='utf-8'),'html.parser')
            files += [urlsplit(i['src']).path for i in soup.select('img[src]') if i['src'].startswith('/')]
            files += [a['href'] for a in soup.select('a[href]') if a['href'].startswith('/assets/')]
    files=list(dict.fromkeys(files))
    files += ['/'+str(path.relative_to(site)) for path in (site/'assets/fonts').glob('*.woff2')]
    digest=hashlib.sha256()
    for path in files:
        digest.update((site/('index.html' if path=='/' else path.lstrip('/'))).read_bytes())
    cache='card-offline-'+digest.hexdigest()[:12]
    for page in ['index.html','en.html']:
        if (site/page).exists():
            soup=BeautifulSoup((site/page).read_text(encoding='utf-8'),'html.parser')
            config=soup.new_tag('script',attrs={'data-offline-config':''})
            config.string='window.CARD_CACHE='+json.dumps(cache)+';window.CARD_OFFLINE_FILES='+json.dumps(files)+';'
            soup.head.append(config);(site/page).write_text(str(soup),encoding='utf-8')
    sw='const CACHE='+json.dumps(cache)+';const FILES='+json.dumps(files)+''';self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('card-offline-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||!FILES.includes(u.pathname))return;e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();e.waitUntil(caches.open(CACHE).then(c=>c.put(u.pathname,copy)))}return r}).catch(()=>caches.open(CACHE).then(c=>c.match(u.pathname))))});'''
    (site/'sw.js').write_text(sw,encoding='utf-8')
    return {'photo_bytes':len(buf.getvalue()),'contact_qr_bytes':len(payload.encode()),'cache':cache,'cached_files':len(files)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site-dir',type=Path,required=True)
    p.add_argument('--contact',required=True)
    p.add_argument('--photo',type=Path,required=True)
    p.add_argument('--public-url',required=True)
    p.add_argument('--name',required=True)
    p.add_argument('--crop',help='Normalized left,top,right,bottom for the portrait')
    a=p.parse_args()
    crop=None
    if a.crop:
        crop=[float(v) for v in a.crop.split(',')]
        if len(crop)!=4 or not (0<=crop[0]<crop[2]<=1 and 0<=crop[1]<crop[3]<=1):p.error('Invalid crop')
    try:print(json.dumps(build(a.site_dir,a.contact,a.photo,a.public_url,a.name,crop)))
    except (ValueError,OSError,KeyError) as e:p.exit(2,str(e)+'\n')


if __name__=='__main__':main()
