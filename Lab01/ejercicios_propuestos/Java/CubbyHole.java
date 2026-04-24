package Java;

public class CubbyHole {
    private int contents;
    private boolean available = false;

    // El Consumidor llama a este método
    public synchronized int get() {
        while (available == false) {
            try {
                wait(); // Espera si el cajón está vacío
            } catch (InterruptedException e) { }
        }
        available = false;
        notifyAll(); // Despierta al productor
        return contents;
    }

    // El Productor llama a este método
    public synchronized void put(int value) {
        while (available == true) {
            try {
                wait(); // Espera si el cajón ya tiene algo
            } catch (InterruptedException e) { }
        }
        contents = value;
        available = true;
        notifyAll(); // Despierta al consumidor
    }
}