import Foundation
while let text = readLine() {
    if let encoded = CardWire.encode(text), let decoded = CardWire.decode(encoded), decoded == text { print("VALID") }
    else { print("INVALID") }
}
