import java.io.*;
import java.net.Socket;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

public class Cliente {
  private String nomeServidor;
  private int portaServidor;
  private static int conexionesExitosas;
  private Timer temporizador;
  private PrintWriter pr;

  // Simulamos que el reloj de este cliente está atrasado 5 minutos (300,000 ms).
  private long desfaseRelojLocal = -300000;

  // Precisión deseada ±D (ms). El umbral máximo aceptable es 2*D.
  private long precisionD;
  private long UMBRAL_RTT_MAX;
  private int objetivoSincronizaciones;

  public Cliente(String nomeServidor, int portaServidor, long precisionD, long desfaseRelojLocal, int objetivoSincronizaciones) {
    this.nomeServidor = nomeServidor;
    this.portaServidor = portaServidor;
    Cliente.conexionesExitosas = 0;
    this.temporizador = new Timer();
    this.precisionD = precisionD;
    this.UMBRAL_RTT_MAX = 2 * precisionD;
    this.desfaseRelojLocal = desfaseRelojLocal;
    this.objetivoSincronizaciones = objetivoSincronizaciones;
    try {
      this.pr = new PrintWriter("LogClientes.txt", "UTF-8");
      pr.println("--- Log de sincronización (Cristian) ---");
      pr.println("Precisión deseada ±D (ms): " + precisionD + " ms");
      pr.println("UMBRAL_RTT_MAX (2·D): " + this.UMBRAL_RTT_MAX + " ms");
      pr.println("Objetivo sincronizaciones: " + this.objetivoSincronizaciones);
      pr.println("----------------------------------------");
      pr.flush();
    } catch (IOException e) {
      System.out.println(e.getMessage());
    }
  }

  // Método para obtener la "hora" del cliente basándose en su propio reloj
  // desfasado
  private long getHoraLocal() {
    return System.currentTimeMillis() + desfaseRelojLocal;
  }

  class Conversation extends TimerTask {
    @Override
    public void run() {
      // El programa intentará hasta conseguir el número objetivo de sincronizaciones.
      if (conexionesExitosas < objetivoSincronizaciones) {
        System.out.println("\n--- Intento de Sincronización ---");
        long horaLocalAntes = getHoraLocal();
        System.out.println("Hora local ANTES de sincronizar: " + formataData(horaLocalAntes));
        System.out.println("Desfase local actual: " + desfaseRelojLocal + " ms");
        System.out.println("Precisión deseada ±D: " + precisionD + " ms (umbral RTT=" + UMBRAL_RTT_MAX + " ms)");

        // T0: instante en que el cliente envía la solicitud.
        try (Socket cliente = new Socket(nomeServidor, portaServidor);
            DataOutputStream out = new DataOutputStream(cliente.getOutputStream());
            DataInputStream in = new DataInputStream(cliente.getInputStream())) {

          long t0 = getHoraLocal();
          out.writeUTF("Solicito la hora");
          out.flush();

          // T_servidor: tiempo que marca el servidor al responder.
          long t_servidor = in.readLong();

          // T1: instante en que el cliente recibe la respuesta.
          long t1 = getHoraLocal();

          // Cálculo de RTT (Round-Trip Time)
          long rtt = t1 - t0;
          System.out.println("RTT calculado: " + rtt + " ms");

          // VALIDACIÓN DE LA TEORÍA: Descartar si hay congestión de red
          if (rtt > UMBRAL_RTT_MAX) {
            System.out.println("ADVERTENCIA: RTT supera el umbral de " + UMBRAL_RTT_MAX + " ms.");
            System.out.println("Descartando respuesta por posible congestión o latencia excesiva.");
            pr.println("Intento fallido: RTT muy alto (" + rtt + " ms)");
            pr.flush();
          } else {
            // Cálculo de Cristian: T_nuevo = T_servidor + (RTT / 2)
            long t_nuevo = t_servidor + (rtt / 2);

            // Ajustamos nuestro reloj interno para que la hora local pase a t_nuevo.
            long diferencia = t_nuevo - t1;
            desfaseRelojLocal += diferencia;

            System.out.println("Sincronización EXITOSA. Reloj interno ajustado.");
            System.out.println("Desfase estimado por Cristian: " + diferencia + " ms");
            System.out.println("Hora local DESPUÉS de sincronizar: " + formataData(getHoraLocal()));

            // Escribir al log
            pr.println("--- Sincronización Exitosa ---");
            pr.println("T0 (Envío Cliente): \t\t" + formataData(t0));
            pr.println("T_servidor (Hora Servidor): \t" + formataData(t_servidor));
            pr.println("T1 (Recepción Cliente): \t" + formataData(t1));
            pr.println("RTT de la red: \t\t\t" + rtt + " ms");
            pr.println("Desfase aplicado: \t\t" + diferencia + " ms");
            pr.println("T_nuevo (Calculado): \t\t" + formataData(t_nuevo));
            pr.println("------------------------------");
            pr.flush();

            conexionesExitosas++;
          }

        } catch (IOException e) {
          System.out.println("ERROR: Servidor inalcanzable. Reintentando en el próximo ciclo...");
        }
      } else {
        pr.close();
        temporizador.cancel();
        temporizador.purge();
        System.out.println("\nSincronización completada. Cliente finalizado.");
      }
    }
  }

  public static void main(String[] args) {
    // Parámetros por defecto
    String host = "localhost";
    int port = 9092;
    long D = 400; // ms
    long desfase = -300000; // -5 minutos
    int objetivo = 3;

    if (args.length >= 1) host = args[0];
    if (args.length >= 2) try { port = Integer.parseInt(args[1]); } catch (NumberFormatException ignored) {}
    if (args.length >= 3) try { D = Long.parseLong(args[2]); } catch (NumberFormatException ignored) {}
    if (args.length >= 4) try { desfase = Long.parseLong(args[3]); } catch (NumberFormatException ignored) {}
    if (args.length >= 5) try { objetivo = Integer.parseInt(args[4]); } catch (NumberFormatException ignored) {}

    System.out.println("Iniciando ClienteV2 con: host=" + host + " port=" + port + " D=" + D + "ms desfase=" + desfase + "ms objetivo=" + objetivo);
    Cliente cliente = new Cliente(host, port, D, desfase, objetivo);
    // Intentará conectarse cada 4 segundos.
    cliente.temporizador.schedule(cliente.new Conversation(), 0, 4000);
  }

  public String formataData(long data) {
    Timestamp timeStamp = new Timestamp(data);
    Date date = new Date(timeStamp.getTime());
    SimpleDateFormat formato = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss.SSS");
    return formato.format(date);
  }
}