package ar.atrcode.tarjetacerca;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.UUID;

/** Pure protocol code: no Android dependencies. Read-only public HTTPS URLs. */
public final class CardWire {
    public static final UUID SERVICE = UUID.fromString("481cf310-1ca4-4c90-b639-14b072d803c7");
    public static final UUID VALUE = UUID.fromString("481cf311-1ca4-4c90-b639-14b072d803c7");
    public static final int MAX_URL_BYTES = 384;
    public static byte[] encode(String text) {
        try {
            byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
            URI uri = new URI(text);
            String host = uri.getRawAuthority();
            if (!text.startsWith("https://") || host == null || !host.contains(".")
                    || uri.getRawUserInfo() != null || uri.getPort() != -1 || bytes.length > MAX_URL_BYTES
                    || !text.matches("[A-Za-z0-9\\-._~:/?#@!$&'()*+,;=%]+")) throw new Exception();
            for (String label : host.split("\\.", -1))
                if (!label.matches("[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")) throw new Exception();
            return bytes;
        } catch (Exception error) { throw new IllegalArgumentException("Usá una URL HTTPS pública, sin usuario ni puerto, de hasta 384 caracteres. Codificá tildes y espacios en la URL."); }
    }
    public static String decode(byte[] value) {
        String url = new String(value, StandardCharsets.UTF_8);
        if (!Arrays.equals(value, encode(url))) throw new IllegalArgumentException("Enlace inválido");
        return url;
    }
    public static byte[] ndef(String url) {
        byte[] suffix = Arrays.copyOfRange(encode(url), 8, encode(url).length);
        int payload = suffix.length + 1;
        boolean shortRecord = payload <= 255;
        byte[] record = new byte[payload + (shortRecord ? 4 : 7)];
        record[0] = (byte)(shortRecord ? 0xD1 : 0xC1); // MB ME [SR] TNF well-known
        record[1] = 1;
        int p;
        if (shortRecord) { record[2] = (byte)payload; p = 3; }
        else { record[2] = 0; record[3] = 0; record[4] = (byte)(payload >> 8); record[5] = (byte)payload; p = 6; }
        record[p++] = 0x55; // URI
        record[p++] = 0x04; // https://
        System.arraycopy(suffix, 0, record, p, suffix.length);
        return record;
    }
}
