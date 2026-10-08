import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

from bs4 import BeautifulSoup
from PIL import Image
import vobject
import zxingcpp

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
assets, offline = module('build_assets'), module('build_offline')


class OfflineTest(unittest.TestCase):
    def test_contact_qr_without_internet_or_public_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            assets.build({'name':'Lucía Pérez','email':'lucia@example.org','phone':'+5491112345678'},d)
            result=zxingcpp.read_barcode(Image.open(d/'qr-contacto-datos.png'))
            self.assertIsNotNone(result)
            card=vobject.readOne(result.text)
            self.assertEqual(card.fn.value,'Lucía Pérez')
            self.assertNotIn('photo',card.contents)
            self.assertFalse((d/'qr-micrositio.png').exists())

    def test_photo_and_portable_card_preserve_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'assets').mkdir()
            Image.new('RGB',(500,400),'teal').save(d/'assets/photo.jpg')
            profile={'name':'Lucía Pérez','email':'lucia@example.org','public_url':'https://example.org/','contact_photo_local':str(d/'assets/photo.jpg')}
            assets.build(profile,d)
            (d/'styles.css').write_text('body{color:#123}')
            (d/'script.js').write_text('')
            page='<html lang="es"><head><link rel="stylesheet" href="/styles.css"></head><body><main><img src="/assets/photo.jpg"><a class="save-contact" href="/contacto.vcf">Guardar contacto</a></main></body></html>'
            (d/'index.html').write_text(page)
            (d/'en.html').write_text(page.replace('lang="es"','lang="en"'))
            offline.build(d,'contacto.vcf',d/'assets/photo.jpg','https://example.org/','Lucía Pérez')
            card=vobject.readOne((d/'contacto-con-foto.vcf').read_text())
            self.assertEqual(card.fn.value,profile['name'])
            self.assertEqual(Image.open(io.BytesIO(card.photo.value)).size,(320,320))
            self.assertNotIn('photo',vobject.readOne((d/'contacto-sin-foto.vcf').read_text()).contents)
            self.assertLess((d/'contacto-con-foto.vcf').stat().st_size,256*1024)
            for lang in ('','-en'):
                s=BeautifulSoup((d/f'tarjeta-offline{lang}.html').read_text(),'html.parser')
                self.assertFalse(s.find('script'))
                self.assertFalse(s.select('link[rel=stylesheet]'))
                self.assertTrue(all(i['src'].startswith('data:') for i in s.select('img[src]')))
                photo_link=s.find('a',href=lambda h:h and h.startswith('data:text/vcard;'))
                self.assertIsNotNone(photo_link)
            config=BeautifulSoup((d/'index.html').read_text(),'html.parser').select_one('script[data-offline-config]').string
            paths=json.loads(config.split('window.CARD_OFFLINE_FILES=')[1].rstrip(';'))
            self.assertTrue(all((d/('index.html' if p=='/' else p[1:])).exists() for p in paths))
            qr=zxingcpp.read_barcode(Image.open(d/'assets/qr-contacto-datos.png'))
            self.assertEqual(qr.text.replace('\r\n','\n'),(d/'contacto-qr.vcf').read_text())
            # Re-running does not duplicate controls or re-embed a second photo.
            offline.build(d,'contacto.vcf',d/'assets/photo.jpg','https://example.org/','Lucía Pérez')
            self.assertEqual(len(BeautifulSoup((d/'index.html').read_text(),'html.parser').select('[data-offline-tools]')),1)
            self.assertEqual(len(vobject.readOne((d/'contacto-con-foto.vcf').read_text()).contents['photo']),1)

    def test_reject_subdirectory_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'dedicated origin'):
                offline.build(Path(tmp),'missing.vcf',Path('missing.jpg'),'https://example.org/person/','Person')
            self.assertEqual(list(Path(tmp).iterdir()),[])


if __name__=='__main__':unittest.main()
