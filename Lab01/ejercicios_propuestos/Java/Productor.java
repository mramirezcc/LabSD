package Java;

public class Productor extends Thread {
    private CubbyHole cubbyhole;
    private int numero;

    public Productor(CubbyHole c, int numero) {
        cubbyhole = c;
        this.numero = numero;
    }

    public void run() {
        for (int i = 0; i < 10; i++) {
            cubbyhole.put(i);
            System.out.println("Productor #" + this.numero + " pone: " + i);
            try {
                // Duerme un tiempo aleatorio para simular trabajo
                sleep((int)(Math.random() * 100));
            } catch (InterruptedException e) { }
        }
    }
}
