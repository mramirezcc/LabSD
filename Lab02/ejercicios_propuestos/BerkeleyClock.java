import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

class Node {
    String name;
    long time;

    public Node(String name, long time) {
        this.name = name;
        this.time = time;
    }

    public long getTime() {
        return time;
    }

    public void adjustTime(long offset) {
        time += offset;
    }
}

public class BerkeleyClock {

    static Random random = new Random();

    // convierte milisegundos a hora legible
    public static String formatTime(long millis) {
        LocalTime base = LocalTime.of(10,0,0);
        LocalTime t = base.plusNanos(millis * 1_000_000);
        return t.toString();
    }

    public static void main(String[] args) throws InterruptedException {

        int numberOfNodes = 5;

        List<Node> nodes = new ArrayList<>();

        long realTime = 0;

        System.out.println("Hora real base: 10:00:00\n");

        // generar relojes aleatorios +-5 segundos
        for (int i = 0; i < numberOfNodes; i++) {

            long drift = (random.nextInt(10000) - 5000);

            Node node = new Node("Nodo " + i, realTime + drift);

            nodes.add(node);

            System.out.println(node.name + " reloj inicial: " + formatTime(node.getTime()));
        }

        System.out.println("\n--- Maestro inicia sincronización ---\n");

        Node master = nodes.get(0);

        List<Long> differences = new ArrayList<>();

        long sum = 0;

        for (Node node : nodes) {

            // latencia simulada
            Thread.sleep(random.nextInt(200));

            long diff = node.getTime() - master.getTime();

            differences.add(diff);

            sum += node.getTime();

            System.out.println("Maestro consulta a " + node.name +
                    " -> tiempo: " + formatTime(node.getTime()));
        }

        long average = sum / numberOfNodes;

        System.out.println("\nTiempo promedio calculado: " + formatTime(average) + "\n");

        // enviar ajustes
        for (Node node : nodes) {

            long offset = average - node.getTime();

            node.adjustTime(offset);

            System.out.println(node.name + " ajusta reloj en " + offset + " ms -> nuevo tiempo: " + formatTime(node.getTime()));
        }

        System.out.println("\n--- Relojes sincronizados ---\n");

        for (Node node : nodes) {
            System.out.println(node.name + " tiempo final: " + formatTime(node.getTime()));
        }
    }
}