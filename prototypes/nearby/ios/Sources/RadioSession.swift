import CoreBluetooth
import Foundation

final class RadioSession: NSObject, CBPeripheralManagerDelegate, CBCentralManagerDelegate, CBPeripheralDelegate {
    let onStatus: (String) -> Void
    let onFound: (CBPeripheral) -> Void
    let onReceive: (String) -> Void
    private let serviceID = CBUUID(string: CardWire.service)
    private let valueID = CBUUID(string: CardWire.value)
    private var server: CBPeripheralManager?
    private var central: CBCentralManager?
    private var peer: CBPeripheral?
    private var timer: Timer?
    private var payload: Data?
    private var active = true
    private var scanning = false
    private var published = false
    init(status: @escaping (String) -> Void, found: @escaping (CBPeripheral) -> Void, receive: @escaping (String) -> Void) {
        onStatus = status; onFound = found; onReceive = receive; super.init()
    }
    func share(_ data: Data) {
        payload = data
        server = CBPeripheralManager(delegate: self, queue: nil)
        expire(after: 120)
    }
    func scan() { central = CBCentralManager(delegate: self, queue: nil); expire(after: 30) }
    private func expire(after seconds: TimeInterval) {
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: seconds, repeats: false) { [weak self] _ in self?.fail("Sesión finalizada. Podés volver a intentarlo.") }
    }
    private func fail(_ message: String) { guard active else { return }; stop(); onStatus(message) }
    private func check(_ state: CBManagerState) -> Bool {
        guard active else { return false }
        switch state {
        case .poweredOn: return true
        case .unauthorized: fail("Permití Bluetooth para esta app en Ajustes.")
        case .unsupported: fail("Este dispositivo no ofrece Bluetooth LE compatible.")
        case .poweredOff: fail("Activá Bluetooth y volvé a intentarlo.")
        default: onStatus("Preparando Bluetooth…")
        }
        return false
    }
    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        guard check(peripheral.state), !published else { return }
        published = true
        let service = CBMutableService(type: serviceID, primary: true)
        service.characteristics = [CBMutableCharacteristic(type: valueID, properties: [.read], value: nil, permissions: [.readable])]
        peripheral.add(service)
    }
    func peripheralManager(_ peripheral: CBPeripheralManager, didAdd service: CBService, error: Error?) {
        guard active else { return }
        guard error == nil else { fail("No se pudo publicar la tarjeta."); return }
        // One 128-bit service UUID; no local name or URL in the advertisement.
        peripheral.startAdvertising([CBAdvertisementDataServiceUUIDsKey: [serviceID]])
    }
    func peripheralManagerDidStartAdvertising(_ peripheral: CBPeripheralManager, error: Error?) {
        guard active else { return }
        if error != nil { fail("No se pudo anunciar por Bluetooth.") }
        else { onStatus("Tarjeta visible por Bluetooth durante 2 minutos. Mantené esta pantalla abierta.") }
    }
    func peripheralManager(_ peripheral: CBPeripheralManager, didReceiveRead request: CBATTRequest) {
        guard active, let data = payload, request.characteristic.uuid == valueID else {
            peripheral.respond(to: request, withResult: .readNotPermitted); return
        }
        guard request.offset <= data.count else { peripheral.respond(to: request, withResult: .invalidOffset); return }
        request.value = data.subdata(in: request.offset..<data.count)
        peripheral.respond(to: request, withResult: .success)
    }
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard check(central.state), !scanning else { return }
        scanning = true; central.scanForPeripherals(withServices: [serviceID], options: nil)
        onStatus("Buscando tarjetas. Elegí un dispositivo cercano.")
    }
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        if active && scanning { onFound(peripheral) }
    }
    func connect(_ peripheral: CBPeripheral) {
        guard active, scanning else { return }
        scanning = false; central?.stopScan(); peer = peripheral; peer?.delegate = self
        expire(after: 20); onStatus("Leyendo enlace…"); central?.connect(peripheral, options: nil)
    }
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        if active { peripheral.discoverServices([serviceID]) }
    }
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) { fail("No se pudo conectar. Volvé a recibir.") }
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) { fail("Se perdió la conexión. Volvé a recibir.") }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard active else { return }
        guard error == nil, let service = peripheral.services?.first(where: { $0.uuid == serviceID }) else { fail("No hay una tarjeta compatible."); return }
        peripheral.discoverCharacteristics([valueID], for: service)
    }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard active else { return }
        guard error == nil, let value = service.characteristics?.first(where: { $0.uuid == valueID }) else { fail("No se pudo consultar el enlace."); return }
        peripheral.readValue(for: value)
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard active else { return }
        guard error == nil, characteristic.uuid == valueID, let data = characteristic.value, let url = CardWire.decode(data) else { fail("La tarjeta no contiene una URL HTTPS válida."); return }
        stop(); onReceive(url)
    }
    func stop() {
        active = false; scanning = false; timer?.invalidate(); timer = nil
        server?.stopAdvertising(); server?.removeAllServices(); payload = nil
        central?.stopScan()
        if let peer = peer { central?.cancelPeripheralConnection(peer) }
    }
}
