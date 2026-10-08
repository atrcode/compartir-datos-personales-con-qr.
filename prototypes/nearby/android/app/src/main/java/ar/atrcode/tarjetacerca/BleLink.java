package ar.atrcode.tarjetacerca;

import android.annotation.SuppressLint;
import android.bluetooth.*;
import android.bluetooth.le.*;
import android.content.Context;
import android.os.*;
import java.util.*;

/** One foreground session; construct a new instance after close(). */
@SuppressLint("MissingPermission") // MainActivity checks all three runtime permissions.
public final class BleLink {
    public interface Listener {
        void status(String text);
        void found(BluetoothDevice device, String label);
        void received(String url);
        void ended();
    }
    private final Context context;
    private final Listener listener;
    private final BluetoothManager manager;
    private final BluetoothAdapter adapter;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final Map<String, Integer> mtus = new HashMap<>();
    private BluetoothGattServer server;
    private BluetoothGatt client;
    private byte[] payload;
    private volatile boolean active = true;
    private boolean scanning;
    private final Runnable timeout = () -> fail("Sesión finalizada. Podés volver a intentarlo.");
    public BleLink(Context context, Listener listener) {
        this.context = context; this.listener = listener;
        manager = context.getSystemService(BluetoothManager.class); adapter = manager.getAdapter();
    }
    private void status(String message) { ui.post(() -> { if (active) listener.status(message); }); }
    private void fail(String message) { ui.post(() -> { if (active) { close(); listener.status(message); } }); }
    private boolean ready() {
        if (adapter == null || !adapter.isEnabled()) { fail("Activá Bluetooth y volvé a intentarlo."); return false; }
        return true;
    }
    public void share(String url) {
        if (!ready()) return;
        payload = CardWire.encode(url);
        if (adapter.getBluetoothLeAdvertiser() == null) { fail("Este equipo no permite anunciar por Bluetooth LE."); return; }
        server = manager.openGattServer(context, serverCallback);
        if (server == null) { fail("No se pudo iniciar Bluetooth."); return; }
        BluetoothGattService service = new BluetoothGattService(CardWire.SERVICE, BluetoothGattService.SERVICE_TYPE_PRIMARY);
        service.addCharacteristic(new BluetoothGattCharacteristic(CardWire.VALUE, BluetoothGattCharacteristic.PROPERTY_READ, BluetoothGattCharacteristic.PERMISSION_READ));
        if (!server.addService(service)) fail("No se pudo publicar la tarjeta.");
        ui.postDelayed(timeout, 120_000);
    }
    private final BluetoothGattServerCallback serverCallback = new BluetoothGattServerCallback() {
        @Override public void onServiceAdded(int result, BluetoothGattService service) {
            ui.post(() -> {
                if (!active) return;
                if (result != BluetoothGatt.GATT_SUCCESS) { fail("Error al publicar la tarjeta."); return; }
                AdvertiseSettings settings = new AdvertiseSettings.Builder().setConnectable(true)
                    .setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY).setTimeout(120_000).build();
                // Only one 128-bit UUID, keeping legacy advertising below 31 bytes.
                AdvertiseData data = new AdvertiseData.Builder().addServiceUuid(new ParcelUuid(CardWire.SERVICE)).build();
                adapter.getBluetoothLeAdvertiser().startAdvertising(settings, data, advertiseCallback);
            });
        }
        @Override public void onMtuChanged(BluetoothDevice device, int mtu) { synchronized(mtus) { mtus.put(device.getAddress(), mtu); } }
        @Override public void onConnectionStateChange(BluetoothDevice device, int result, int state) {
            if (state == BluetoothProfile.STATE_DISCONNECTED) synchronized(mtus) { mtus.remove(device.getAddress()); }
        }
        @Override public void onCharacteristicReadRequest(BluetoothDevice device, int id, int offset, BluetoothGattCharacteristic characteristic) {
            ui.post(() -> {
                if (!active || server == null) return;
                if (!CardWire.VALUE.equals(characteristic.getUuid())) { server.sendResponse(device, id, BluetoothGatt.GATT_REQUEST_NOT_SUPPORTED, offset, null); return; }
                if (offset < 0 || offset > payload.length) { server.sendResponse(device, id, BluetoothGatt.GATT_INVALID_OFFSET, offset, null); return; }
                int mtu; synchronized(mtus) { mtu = mtus.getOrDefault(device.getAddress(), 23); }
                byte[] chunk = Arrays.copyOfRange(payload, offset, Math.min(payload.length, offset + mtu - 1));
                server.sendResponse(device, id, BluetoothGatt.GATT_SUCCESS, offset, chunk);
            });
        }
    };
    private final AdvertiseCallback advertiseCallback = new AdvertiseCallback() {
        @Override public void onStartSuccess(AdvertiseSettings settings) { status("Tarjeta visible por Bluetooth durante 2 minutos. Mantené esta pantalla abierta."); }
        @Override public void onStartFailure(int error) { fail("No se pudo anunciar por Bluetooth (" + error + ")."); }
    };
    public void scan() {
        if (!ready()) return;
        if (adapter.getBluetoothLeScanner() == null) { fail("Escaneo Bluetooth no disponible."); return; }
        scanning = true;
        adapter.getBluetoothLeScanner().startScan(Collections.singletonList(new ScanFilter.Builder().setServiceUuid(new ParcelUuid(CardWire.SERVICE)).build()),
            new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(), scanCallback);
        status("Buscando tarjetas. Elegí un dispositivo cercano."); ui.postDelayed(timeout, 30_000);
    }
    private final ScanCallback scanCallback = new ScanCallback() {
        @Override public void onScanResult(int type, ScanResult result) {
            ui.post(() -> { if (active && scanning) listener.found(result.getDevice(), "Tarjeta cercana · " + result.getDevice().getAddress()); });
        }
        @Override public void onScanFailed(int error) { fail("Error al buscar tarjetas (" + error + ")."); }
    };
    public void connect(BluetoothDevice device) {
        if (!active || !scanning) return;
        stopScan(); ui.removeCallbacks(timeout); ui.postDelayed(timeout, 20_000);
        status("Leyendo enlace…"); client = device.connectGatt(context, false, clientCallback, BluetoothDevice.TRANSPORT_LE);
        if (client == null) fail("No se pudo conectar.");
    }
    private final BluetoothGattCallback clientCallback = new BluetoothGattCallback() {
        @Override public void onConnectionStateChange(BluetoothGatt gatt, int result, int state) {
            if (!active) { gatt.close(); return; }
            if (result != BluetoothGatt.GATT_SUCCESS || state == BluetoothProfile.STATE_DISCONNECTED) { fail("Se perdió la conexión. Volvé a recibir."); return; }
            if (state == BluetoothProfile.STATE_CONNECTED && !gatt.discoverServices()) fail("No se pudo consultar la tarjeta.");
        }
        @Override public void onServicesDiscovered(BluetoothGatt gatt, int result) {
            if (!active) return;
            BluetoothGattService s = gatt.getService(CardWire.SERVICE);
            BluetoothGattCharacteristic c = s == null ? null : s.getCharacteristic(CardWire.VALUE);
            if (result != BluetoothGatt.GATT_SUCCESS || c == null || !gatt.readCharacteristic(c)) fail("El dispositivo no ofrece una tarjeta compatible.");
        }
        @Override public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic c, byte[] value, int result) { accept(c, value, result); }
        @SuppressWarnings("deprecation")
        @Override public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic c, int result) { if (Build.VERSION.SDK_INT < 33) accept(c, c.getValue(), result); }
        private void accept(BluetoothGattCharacteristic c, byte[] value, int result) {
            ui.post(() -> {
                if (!active) return;
                if (result != BluetoothGatt.GATT_SUCCESS || !CardWire.VALUE.equals(c.getUuid()) || value == null) { fail("No se pudo leer el enlace."); return; }
                try { String url = CardWire.decode(value); close(); listener.received(url); }
                catch (IllegalArgumentException e) { fail("La tarjeta recibida no contiene una URL HTTPS válida."); }
            });
        }
    };
    private void stopScan() {
        if (scanning && adapter != null && adapter.getBluetoothLeScanner() != null) adapter.getBluetoothLeScanner().stopScan(scanCallback);
        scanning = false;
    }
    public void close() {
        if (!active) return;
        active = false; ui.removeCallbacksAndMessages(null); listener.ended();
        try {
            stopScan();
            if (adapter != null && adapter.getBluetoothLeAdvertiser() != null) adapter.getBluetoothLeAdvertiser().stopAdvertising(advertiseCallback);
            if (client != null) { client.disconnect(); client.close(); client = null; }
            if (server != null) { server.close(); server = null; }
        } catch (SecurityException ignored) { /* Permission revoked in Settings; session remains stopped. */ }
    }
}
