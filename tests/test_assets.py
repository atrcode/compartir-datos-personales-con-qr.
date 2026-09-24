import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_assets.py"
spec = importlib.util.spec_from_file_location("build_assets", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AssetsTest(unittest.TestCase):
    def test_without_public_url_defers_qr(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = mod.build({"name": "Ana Pérez", "email": "ana@example.org"}, Path(tmp))
            self.assertIn("pendiente", result["qr"])
            self.assertFalse((Path(tmp) / "qr-contacto.png").exists())
            self.assertIn("FN:Ana Pérez", (Path(tmp) / "contacto.vcf").read_text())

    def test_with_public_url_generates_qr_and_escapes_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod.build({"name": "Ana & Pérez", "public_url": "https://example.org/ana/"}, Path(tmp))
            self.assertTrue((Path(tmp) / "qr-contacto.png").exists())
            self.assertTrue((Path(tmp) / "qr-contacto.svg").exists())
            self.assertIn("Ana &amp; Pérez", (Path(tmp) / "firma-email.html").read_text())

    def test_rejects_unstable_or_invalid_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                mod.build({"name": "Ana", "public_url": "http://localhost:8000/"}, Path(tmp))


if __name__ == "__main__":
    unittest.main()
