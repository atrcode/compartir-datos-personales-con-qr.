import SwiftUI
import CoreBluetooth

final class CardModel: ObservableObject {
    @Published var message = ""
    @Published var peers: [CBPeripheral] = []
    @Published var received: String?
    private var radio: RadioSession?
    private var nfc: NFCReader?
    func stop() { radio?.stop(); radio = nil; nfc?.stop(); nfc = nil; peers = []; UIApplication.shared.isIdleTimerDisabled = false }
    private func newRadio() -> RadioSession {
        RadioSession(status: { [weak self] in self?.message = $0 }, found: { [weak self] peer in
            guard let self = self else { return }
            if !self.peers.contains(where: { $0.identifier == peer.identifier }) { self.peers.append(peer) }
        }, receive: { [weak self] url in self?.received = url; self?.message = "Enlace recibido. Verificalo con la otra persona."; UIApplication.shared.isIdleTimerDisabled = false })
    }
    func share(_ url: String) {
        guard let data = CardWire.encode(url) else { message = "Usá una URL HTTPS pública, sin usuario ni puerto, de hasta 384 caracteres. Codificá espacios y tildes."; return }
        stop(); received = nil; radio = newRadio(); radio?.share(data); UIApplication.shared.isIdleTimerDisabled = true
    }
    func scan() { stop(); received = nil; radio = newRadio(); radio?.scan() }
    func connect(_ peer: CBPeripheral) { radio?.connect(peer) }
    func readNFC() {
        stop(); received = nil
        nfc = NFCReader(status: { [weak self] in self?.message = $0 }, receive: { [weak self] in self?.received = $0 })
        nfc?.start()
    }
}

@main struct TarjetaCercaApp: App {
    @StateObject private var model = CardModel()
    @AppStorage("cardURL") private var url = ""
    @Environment(\.scenePhase) private var phase
    @Environment(\.openURL) private var openURL
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                Form {
                    Section("Mi tarjeta") {
                        TextField("https://tu-sitio.com/tarjeta", text: $url).keyboardType(.URL).textInputAutocapitalization(.never).autocorrectionDisabled()
                        Button("Compartir por Bluetooth") { model.share(url.trimmingCharacters(in: .whitespacesAndNewlines)) }
                        Text("El enlace público será visible durante 2 minutos para lectores cercanos. Mantené la app abierta.").font(.footnote)
                    }
                    Section("Recibir tarjeta") {
                        Button("Recibir por Bluetooth") { model.scan() }
                        Button("Recibir por NFC") { model.readNFC() }
                        ForEach(model.peers, id: \.identifier) { peer in
                            Button("Tarjeta cercana · \(peer.identifier.uuidString.prefix(8))") { model.connect(peer) }
                        }
                    }
                    if let text = model.received, let target = URL(string: text) {
                        Section("Verificá el enlace recibido") {
                            Text(text).textSelection(.enabled)
                            Button("Abrir esta tarjeta") { openURL(target) }
                            Button("Descartar") { model.received = nil }
                        }
                    }
                    Section {
                        Text(model.message)
                        Button("Detener") { model.stop(); model.message = "Sesión detenida." }
                        Text("Prototipo. Bluetooth requiere esta app en ambos equipos. El envío NFC desde iPhone/Wallet no está implementado.").font(.footnote)
                    }
                }.navigationTitle("Tarjeta Cerca")
            }.onChange(of: phase) { if $0 == .background { model.stop(); model.message = "Sesión detenida al salir de la app." } }
        }
    }
}
