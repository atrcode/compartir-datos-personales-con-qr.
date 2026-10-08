package ar.atrcode.tarjetacerca;

import android.Manifest;
import android.app.*;
import android.bluetooth.BluetoothDevice;
import android.content.*;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.nfc.*;
import android.nfc.cardemulation.CardEmulation;
import android.nfc.tech.Ndef;
import android.os.*;
import android.view.WindowManager;
import android.widget.*;
import java.util.HashSet;

public final class MainActivity extends Activity implements BleLink.Listener {
    private EditText input;
    private TextView message;
    private LinearLayout devices;
    private BleLink ble;
    private NfcAdapter nfc;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final HashSet<String> seen = new HashSet<>();
    private int generation;
    private final String[] permissions = { Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT, Manifest.permission.BLUETOOTH_ADVERTISE };
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        nfc = NfcAdapter.getDefaultAdapter(this);
        LinearLayout layout = new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL); layout.setPadding(36, 48, 36, 24);
        ScrollView scroll = new ScrollView(this); scroll.addView(layout); setContentView(scroll);
        TextView title = new TextView(this); title.setText("Tarjeta Cerca · prototipo"); title.setTextSize(26); layout.addView(title);
        TextView note = new TextView(this); note.setText("Compartí el enlace público de tu tarjeta. Bluetooth requiere esta app en ambos equipos. Cualquier lector cercano puede leer el enlace mientras compartís."); layout.addView(note);
        input = new EditText(this); input.setSingleLine(); input.setHint("https://tu-sitio.com/tarjeta"); input.setInputType(17);
        input.setText(getPreferences(MODE_PRIVATE).getString("url", "")); layout.addView(input);
        button(layout, "Compartir por Bluetooth", () -> { if (permitted()) withUrl(url -> { stop(); keepOn(); ble = new BleLink(this, this); ble.share(url); }); });
        button(layout, "Recibir por Bluetooth", () -> { if (permitted()) { stop(); ble = new BleLink(this, this); ble.scan(); } });
        button(layout, "Compartir por NFC · Android", () -> withUrl(url -> {
            if (!nfcReady() || !getPackageManager().hasSystemFeature(PackageManager.FEATURE_NFC_HOST_CARD_EMULATION)) { status("Se necesita NFC con emulación de tarjeta habilitada."); return; }
            stop(); keepOn(); CardService.arm(url);
            CardEmulation.getInstance(nfc).setPreferredService(this, new ComponentName(this, CardService.class));
            status("NFC activo durante 2 minutos. El receptor debe abrir «Recibir por NFC» y acercar las antenas.");
            ui.postDelayed(() -> { stop(); status("NFC detenido."); }, 120_000);
        }));
        button(layout, "Recibir por NFC", () -> {
            if (!nfcReady()) return;
            stop(); int current = generation; status("Acercá una tarjeta NFC o un Android que esté compartiendo.");
            nfc.enableReaderMode(this, tag -> {
                try {
                    Ndef reader = Ndef.get(tag);
                    if (reader == null) throw new Exception();
                    NdefMessage data;
                    try { reader.connect(); data = reader.getNdefMessage(); } finally { reader.close(); }
                    if (data == null || data.getRecords().length != 1) throw new Exception();
                    Uri uri = data.getRecords()[0].toUri(); if (uri == null) throw new Exception();
                    String url = CardWire.decode(CardWire.encode(uri.toString()));
                    runOnUiThread(() -> { if (generation == current) { stop(); received(url); } });
                } catch (Exception error) { runOnUiThread(() -> { if (generation == current) status("No se pudo leer. Mantené los teléfonos cerca y reintentá."); }); }
            }, NfcAdapter.FLAG_READER_NFC_A | NfcAdapter.FLAG_READER_NFC_B, null);
            ui.postDelayed(() -> { stop(); status("Lectura NFC finalizada."); }, 60_000);
        });
        button(layout, "Detener", () -> { stop(); status("Sesión detenida."); });
        message = new TextView(this); message.setPadding(0, 20, 0, 20); layout.addView(message);
        devices = new LinearLayout(this); devices.setOrientation(LinearLayout.VERTICAL); layout.addView(devices);
    }
    private void button(LinearLayout parent, String label, Runnable action) { Button b = new Button(this); b.setText(label); b.setOnClickListener(v -> action.run()); parent.addView(b); }
    private boolean permitted() {
        for (String p : permissions) if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(permissions, 1); status("Autorizá Bluetooth y volvé a tocar el botón."); return false;
        }
        return true;
    }
    private boolean nfcReady() { if (nfc == null || !nfc.isEnabled()) { status("Activá NFC en un dispositivo compatible."); return false; } return true; }
    private void withUrl(java.util.function.Consumer<String> action) {
        try { String url = input.getText().toString().trim(); CardWire.encode(url); getPreferences(MODE_PRIVATE).edit().putString("url", url).apply(); action.accept(url); }
        catch (IllegalArgumentException error) { status(error.getMessage()); }
    }
    private void keepOn() { getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON); }
    private void stop() {
        generation++; ui.removeCallbacksAndMessages(null); CardService.stop();
        if (ble != null) { ble.close(); ble = null; }
        if (nfc != null) { nfc.disableReaderMode(this); if (getPackageManager().hasSystemFeature(PackageManager.FEATURE_NFC_HOST_CARD_EMULATION)) CardEmulation.getInstance(nfc).unsetPreferredService(this); }
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if (devices != null) devices.removeAllViews(); seen.clear();
    }
    @Override public void status(String text) { message.setText(text); }
    @Override public void found(BluetoothDevice device, String label) {
        if (seen.add(device.getAddress())) button(devices, label, () -> { if (ble != null) ble.connect(device); });
    }
    @Override public void received(String url) {
        status("Enlace recibido. Verificá con la otra persona que sea su tarjeta.");
        new AlertDialog.Builder(this).setTitle("¿Abrir esta tarjeta?").setMessage(url)
            .setNegativeButton("Cancelar", null).setPositiveButton("Abrir", (d, w) -> {
                try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }
                catch (ActivityNotFoundException error) { status("No hay un navegador disponible."); }
            }).show();
    }
    @Override protected void onPause() { stop(); super.onPause(); }
}
