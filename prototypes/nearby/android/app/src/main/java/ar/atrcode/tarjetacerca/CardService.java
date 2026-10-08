package ar.atrcode.tarjetacerca;

import android.nfc.cardemulation.HostApduService;
import android.os.Bundle;
import android.os.SystemClock;

public final class CardService extends HostApduService {
    private static Type4Card card;
    private static long expires;
    public static synchronized void arm(String url) { card = new Type4Card(url); expires = SystemClock.elapsedRealtime() + 120_000; }
    public static synchronized void stop() { card = null; expires = 0; }
    @Override public byte[] processCommandApdu(byte[] command, Bundle extras) {
        synchronized (CardService.class) {
            if (card == null || SystemClock.elapsedRealtime() >= expires) return Type4Card.hex("6985");
            return card.respond(command);
        }
    }
    @Override public void onDeactivated(int reason) { synchronized (CardService.class) { if (card != null) card.reset(); } }
}
