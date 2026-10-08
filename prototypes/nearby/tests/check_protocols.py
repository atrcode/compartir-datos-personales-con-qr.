"""Cross-language vectors plus Type 4 APDU roundtrip. Requires javac or swiftc."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('build_nfc', ROOT/'scripts/build_nfc.py')
nfc = importlib.util.module_from_spec(spec); spec.loader.exec_module(nfc)
parser = argparse.ArgumentParser(); parser.add_argument('language', choices=['java', 'swift']); args = parser.parse_args()
vectors = [
    'https://example.org/ana/', 'https://example.org/%C3%B1?q=a%20b#contacto',
    'https://example.org/' + 'x'*364, 'https://example.org/' + 'x'*365,
    'https://example.org/' + 'x'*244, 'https://example.org/' + 'x'*245,
    'http://example.org', 'https://localhost/', 'https://user@example.org', 'https://example.org:443/',
    'https://example.org/%ZZ', 'https://example.org/a b', 'https://example.org/ñ',
    'https://example.org/<script>', 'https://a..org/', 'https://-a.org/', 'https://example.org/a\\b',
    'https://example%2Eorg/', 'https://example.123/', 'https://example.org/%', 'https://example.org/%2', 'javascript:alert(1)', ''
]
expected = []
for value in vectors:
    try: expected.append(nfc.ndef_uri(value).hex() if args.language == 'java' else ('VALID' if nfc.validate_url(value) else 'INVALID'))
    except ValueError: expected.append('INVALID')
with tempfile.TemporaryDirectory() as tmp:
    if args.language == 'java':
        src = ROOT/'prototypes/nearby/android/app/src/main/java/ar/atrcode/tarjetacerca'
        subprocess.run(['javac', '-d', tmp, str(src/'CardWire.java'), str(src/'Type4Card.java'), str(ROOT/'prototypes/nearby/tests/ProtocolTest.java')], check=True)
        command = ['java', '-ea', '-cp', tmp, 'ProtocolTest']
    else:
        binary = str(Path(tmp)/'protocol')
        subprocess.run(['swiftc', str(ROOT/'prototypes/nearby/ios/Sources/CardWire.swift'), str(ROOT/'prototypes/nearby/tests/main.swift'), '-o', binary], check=True)
        command = [binary]
    result = subprocess.run(command, input='\n'.join(vectors)+'\n', text=True, capture_output=True, check=True)
    actual = result.stdout.splitlines()
    assert len(actual) == len(expected), (actual, result.stderr)
    for value, got, want in zip(vectors, actual, expected):
        assert got == want, (value, got, want)
print(f'{args.language}: {len(vectors)} shared vectors passed; '+ ('NFC Type 4 APDU roundtrip passed.' if args.language == 'java' else 'Swift URL roundtrip passed.'))
