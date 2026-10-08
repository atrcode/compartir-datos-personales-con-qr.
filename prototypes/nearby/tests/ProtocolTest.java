import ar.atrcode.tarjetacerca.CardWire;
import ar.atrcode.tarjetacerca.Type4Card;
import java.util.Arrays;
import java.io.*;

public class ProtocolTest {
    private static void equal(byte[] actual, String expected) { if (!Arrays.equals(actual, Type4Card.hex(expected))) throw new AssertionError(expected); }
    public static void main(String[] args) throws Exception {
        String url = "https://example.org/" + "x".repeat(364);
        byte[] ndef = CardWire.ndef(url);
        Type4Card card = new Type4Card(url);
        equal(card.respond(Type4Card.hex("00B0000002")), "6985");
        equal(card.respond(Type4Card.hex("00A4040007D276000085010100")), "9000");
        equal(card.respond(Type4Card.hex("00A4000C02E103")), "9000");
        equal(card.respond(Type4Card.hex("00B000000F")), "000F2000FF00FF0406E104020000FF9000");
        equal(card.respond(Type4Card.hex("00A4000C02E104")), "9000");
        byte[] length = card.respond(Type4Card.hex("00B0000002"));
        if ((length[0] & 255) * 256 + (length[1] & 255) != ndef.length) throw new AssertionError("NLEN");
        ByteArrayOutputStream decoded = new ByteArrayOutputStream();
        for (int offset = 2; offset < ndef.length + 2;) {
            int count = Math.min(37, ndef.length + 2 - offset);
            byte[] response = card.respond(new byte[] {0, (byte)0xB0, (byte)(offset >> 8), (byte)offset, (byte)count});
            if (response.length != count + 2 || response[count] != (byte)0x90 || response[count+1] != 0) throw new AssertionError("READ");
            decoded.write(response, 0, count); offset += count;
        }
        if (!Arrays.equals(decoded.toByteArray(), ndef)) throw new AssertionError("Long NDEF roundtrip");
        equal(card.respond(Type4Card.hex("00B07FFF01")), "6B00");
        equal(card.respond(Type4Card.hex("00D6000000")), "6D00");
        equal(card.respond(Type4Card.hex("00A4000C02FFFF")), "6A82");
        equal(card.respond(Type4Card.hex("00B0000002")), "6985");
        card.reset(); equal(card.respond(Type4Card.hex("00B0000002")), "6985");
        equal(card.respond(new byte[0]), "6700");
        BufferedReader input = new BufferedReader(new InputStreamReader(System.in, java.nio.charset.StandardCharsets.UTF_8));
        String line;
        while ((line = input.readLine()) != null) {
            try { CardWire.encode(line); System.out.println(java.util.HexFormat.of().formatHex(CardWire.ndef(line))); }
            catch (IllegalArgumentException e) { System.out.println("INVALID"); }
        }
    }
}
