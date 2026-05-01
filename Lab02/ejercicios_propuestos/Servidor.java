import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.ThreadLocalRandom;

public class ServidorV2 extends Thread {
  private final ServerSocket servidorSocket;
  private final long minLatencyMs;
  private final long maxLatencyMs;

  public ServidorV2(int port, long minLatencyMs, long maxLatencyMs) throws IOException {
    servidorSocket = new ServerSocket(port);
    this.minLatencyMs = Math.max(0, Math.min(minLatencyMs, maxLatencyMs));
    this.maxLatencyMs = Math.max(this.minLatencyMs, maxLatencyMs);
  }

  @Override
  public void run() {
    System.out.println("--------------------------------------------");
    System.out.println("Servidor de Tiempo iniciado en el puerto " + servidorSocket.getLocalPort());
    System.out.println("Latencia simulada: min=" + minLatencyMs + " ms, max=" + maxLatencyMs + " ms");

    while (true) {
      try (Socket server = servidorSocket.accept();
          DataInputStream in = new DataInputStream(server.getInputStream());
          DataOutputStream out = new DataOutputStream(server.getOutputStream())) {

        // Lee la petición del cliente.
        in.readUTF();

        long t_recibido = System.currentTimeMillis();
        System.out.println("Petición recibida en: " + formataData(t_recibido));

        // Latencia simulada para que el laboratorio muestre RTT variables.
        long latenciaSimulada = ThreadLocalRandom.current().nextLong(minLatencyMs, maxLatencyMs + 1);
        System.out.println("Latencia simulada de respuesta: " + latenciaSimulada + " ms");
        Thread.sleep(latenciaSimulada);

        // T_servidor: instante en que el servidor responde con su tiempo actual.
        long t_servidor = System.currentTimeMillis();
        System.out.println("Respuesta enviada en: " + formataData(t_servidor));
        out.writeLong(t_servidor);
        out.flush();

      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        System.out.println("Servidor interrumpido durante la simulación de latencia.");
      } catch (IOException e) {
        System.out.println("Error en la conexión con un cliente.");
      }
    }
  }

  public static void main(String[] args) {
    // Valores por defecto
    int port = 9092;
    long minLat = 100;
    long maxLat = 1000;

    if (args.length >= 1) try { port = Integer.parseInt(args[0]); } catch (NumberFormatException ignored) {}
    if (args.length >= 2) try { minLat = Long.parseLong(args[1]); } catch (NumberFormatException ignored) {}
    if (args.length >= 3) try { maxLat = Long.parseLong(args[2]); } catch (NumberFormatException ignored) {}

    try {
      Thread t = new ServidorV2(port, minLat, maxLat);
      t.start();
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  public String formataData(long data) {
    Timestamp timeStamp = new Timestamp(data);
    Date date = new Date(timeStamp.getTime());
    SimpleDateFormat formato = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss.SSS");
    return formato.format(date);
  }
}