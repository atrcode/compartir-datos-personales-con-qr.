import CoreNFC
import Foundation

final class NFCReader: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?
    private let status: (String) -> Void
    private let receive: (String) -> Void
    private var active = true
    init(status: @escaping (String) -> Void, receive: @escaping (String) -> Void) { self.status = status; self.receive = receive }
    func start() {
        guard NFCNDEFReaderSession.readingAvailable else { status("Este iPhone no permite lectura NFC."); return }
        session = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: true)
        session?.alertMessage = "Acercá la parte superior del iPhone a la tarjeta o Android que comparte."
        session?.begin()
    }
    func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
        guard active else { return }
        guard messages.count == 1, messages[0].records.count == 1,
              let url = messages[0].records[0].wellKnownTypeURIPayload()?.absoluteString,
              CardWire.encode(url) != nil else { status("No se encontró un enlace HTTPS válido."); return }
        active = false; receive(url)
    }
    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        guard active else { return }; active = false
        status("Lectura NFC finalizada. Si no se recibió el enlace, volvé a intentarlo.")
    }
    func stop() { active = false; session?.invalidate(); session = nil }
}
