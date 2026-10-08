package ar.atrcode.tarjetacerca;

import java.util.Arrays;

/** Minimal read-only NFC Forum Type 4 mapping v2.0 (SELECT + READ BINARY). */
public final class Type4Card {
    private static final byte[] AID = hex("D2760000850101");
    private static final byte[] CC = hex("000F2000FF00FF0406E104020000FF");
    private final byte[] file;
    private boolean selected;
    private int fileId;
    public Type4Card(String url) {
        byte[] record = CardWire.ndef(url);
        file = new byte[record.length + 2];
        file[0] = (byte)(record.length >> 8); file[1] = (byte)record.length;
        System.arraycopy(record, 0, file, 2, record.length);
    }
    public void reset() { selected = false; fileId = 0; }
    public byte[] respond(byte[] a) {
        if (a == null || a.length < 4) return hex("6700");
        if (a[0] != 0) return hex("6E00");
        if ((a[1] & 255) == 0xA4 && a[2] == 4) {
            reset();
            if (a.length < 5 || (a[4] & 255) != AID.length || a.length < 5 + AID.length) return hex("6700");
            if (a[3] != 0 || !Arrays.equals(Arrays.copyOfRange(a, 5, 12), AID)) return hex("6A82");
            selected = true; return hex("9000");
        }
        if (!selected) return hex("6985");
        if ((a[1] & 255) == 0xA4) {
            fileId = 0;
            if (a.length < 7 || a[2] != 0 || (a[3] != 0 && a[3] != 0x0C) || a[4] != 2) return hex("6A86");
            int id = (a[5] & 255) * 256 + (a[6] & 255);
            if (id != 0xE103 && id != 0xE104) return hex("6A82");
            fileId = id; return hex("9000");
        }
        if ((a[1] & 255) != 0xB0) return hex("6D00");
        if (a.length != 5) return hex("6700");
        if (fileId == 0) return hex("6985");
        int offset = (a[2] & 255) * 256 + (a[3] & 255), length = a[4] & 255;
        if (length == 0) length = 256;
        byte[] data = fileId == 0xE103 ? CC : file;
        if (offset > data.length || offset + length > data.length) return hex("6B00");
        byte[] reply = Arrays.copyOfRange(data, offset, offset + length + 2);
        reply[length] = (byte)0x90; reply[length + 1] = 0;
        return reply;
    }
    public static byte[] hex(String text) {
        byte[] bytes = new byte[text.length() / 2];
        for (int i = 0; i < bytes.length; i++) bytes[i] = (byte)Integer.parseInt(text.substring(i * 2, i * 2 + 2), 16);
        return bytes;
    }
}
