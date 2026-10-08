# Digital card, contact QR, email signature and Wallet

[Español](README.md)

An open skill for creating a branded digital business card through a conversational intake: name, bio, photo, logo, WhatsApp, email, LinkedIn, website and authorized resources, one question at a time.

The kit includes a mobile microsite, a link QR, an offline contact QR, vCard with optional embedded photo, an HTML/plain-text email signature and installation guidance for the user's email app. Apple Wallet and Google Wallet are optional and require valid issuer credentials/certificates; templates are not installable passes.

## Online and offline

- **Online:** open the microsite for the full visual presentation, links and resources.
- **Sender offline, recipient online:** show the saved website QR; the recipient uses their connection.
- **Recipient offline:** scan the basic contact QR, if the camera supports vCard, or transfer a local contact file through compatible native sharing.
- **Photo:** the VCF embeds a JPEG so no image download is needed. Offer saving with or without a photo; verify preservation in the recipient's Contacts app.
- **Fallback:** show the QR when phone-to-phone sharing is unavailable. No project app is required on the recipient's phone.

Compatible AirDrop/Quick Share transfers may work without Internet with the required radios enabled. Cross-platform support varies by Android model and version. A Wallet pass is not a universal NFC transmitter. The experimental BLE app branch requires an app on both phones and does not meet the no-install requirement.

Download the self-contained offline HTML, contact file and QR in advance. Browser preparation can also cache the site, but storage may be evicted. Website links and resources need connectivity unless the actual files were downloaded and transferred.

## Generate assets

```bash
python -m pip install -r requirements.txt
python scripts/build_assets.py --profile profile.json --output delivery
```

Use `language: "en"` for signature labels and `contact_photo_local` for the portrait. The profile example is fictional. Keep client profiles and secrets out of the public repository. The script generates assets; it does not publish the website or issue Wallet passes.

For an existing buildless site with `index.html`, `styles.css`, `script.js`, a local portrait, vCard 3.0 and optional `en.html`:

```bash
python scripts/build_offline.py --site-dir /path/dist \
  --contact contact.vcf --photo /path/portrait.jpg \
  --public-url https://card.example.org/ --name "Ana Pérez"
```

The offline integration requires a dedicated origin at `/`. Subdirectory hosting needs adapted paths and service-worker scope. It preserves the existing contact path while adding both photo variants, QR codes, self-contained offline pages and native-share controls.

Keep Spanish at `/` and English at `/en.html`, with a language selector, translated biographies, actions and accessibility labels, plus canonical/hreflang metadata. Published book titles and resource files are not automatically translated.

## Test and contribute

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
node --test tests/test_offline_runtime.cjs
```

Tests decode QR payloads independently, parse embedded photos, check portable HTML and simulate sharing/cache fallbacks. They do not certify phone radio transfers, camera support, photo imports or visual browser rendering.

See [updates](docs/UPDATES.md), [skill instructions](SKILL.md), [offline workflow](references/offline.md), [compatibility](references/nearby.md), and [contribution guide](CONTRIBUTING.md). Skill instructions currently use Spanish; the assistant should follow the user's language.

Leandro E. Mocchegiani · [MIT license](LICENSE).
