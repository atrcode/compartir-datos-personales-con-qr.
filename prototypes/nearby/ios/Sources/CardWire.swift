import Foundation

enum CardWire {
    static let service = "481cf310-1ca4-4c90-b639-14b072d803c7"
    static let value = "481cf311-1ca4-4c90-b639-14b072d803c7"
    static func encode(_ text: String) -> Data? {
        guard text.hasPrefix("https://"), text.utf8.count <= 384,
              text.range(of: #"^[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]+$"#, options: .regularExpression) != nil,
              let url = URLComponents(string: text), let host = url.host, host.contains("."),
              url.user == nil, url.password == nil, url.port == nil,
              url.url != nil else { return nil }
        guard host.components(separatedBy: ".").allSatisfy({
            $0.range(of: #"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"#, options: .regularExpression) != nil
        }) else { return nil }
        // Reject malformed percent escapes equally on Java and Swift.
        let bytes = Array(text.utf8)
        for i in bytes.indices where bytes[i] == 37 {
            guard i + 2 < bytes.count, isHex(bytes[i + 1]), isHex(bytes[i + 2]) else { return nil }
        }
        return Data(text.utf8)
    }
    private static func isHex(_ c: UInt8) -> Bool { (48...57).contains(c) || (65...70).contains(c) || (97...102).contains(c) }
    static func decode(_ data: Data) -> String? {
        guard let text = String(data: data, encoding: .utf8), encode(text) == data else { return nil }
        return text
    }
}
