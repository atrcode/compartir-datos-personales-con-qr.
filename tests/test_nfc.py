import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_nfc', ROOT / 'scripts/build_nfc.py')
nfc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nfc)


class NFCTests(unittest.TestCase):
    def test_known_uri_record(self):
        self.assertEqual(nfc.ndef_uri('https://example.org/ana/'), bytes.fromhex('d101115504') + b'example.org/ana/')

    def test_short_and_long_ndef(self):
        for length in [22, 261, 262, 384]:
            url = 'https://example.org/' + 'a' * (length - 20)
            record = nfc.ndef_uri(url)
            self.assertEqual(record[0] & 0xC7, 0xC1)
            short = bool(record[0] & 0x10)
            size = record[2] if short else struct.unpack('>I', record[2:6])[0]
            at = 3 if short else 6
            self.assertEqual(record[at:at+2], b'U\x04')
            self.assertEqual(size, len(record) - at - 1)
            self.assertEqual('https://' + record[at+2:].decode('ascii'), url)

    def test_reject_invalid_links(self):
        for url in [None, '', 'http://example.org', 'https://user@example.org', 'https://a..org', 'https://example.org:443',
                    'https://localhost/', 'https://example.org/%ZZ', 'https://example.org/a b', 'https://example.org/ñ',
                    'https://example.org/' + 'x'*400, 'javascript:alert(1)', 'https://example.org/\n']:
            with self.subTest(url=url), self.assertRaises(ValueError): nfc.ndef_uri(url)

    def test_cli_prepares_without_claiming_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); profile = root / 'profile.json'
            profile.write_text(json.dumps({'public_url': 'https://example.org/ana/'}))
            subprocess.run([sys.executable, str(ROOT/'scripts/build_nfc.py'), '--profile', str(profile), '--output', str(root/'out')], check=True, capture_output=True)
            self.assertEqual((root/'out/tarjeta.ndef').read_bytes(), nfc.ndef_uri('https://example.org/ana/'))
            self.assertIn('ETIQUETA TODAVÍA NO GRABADA', (root/'out/Grabar-NFC.txt').read_text())


if __name__ == '__main__': unittest.main()
