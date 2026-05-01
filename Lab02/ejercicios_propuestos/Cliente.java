import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

public class Cliente {

    private String nomeServidor;
    private int portaServidor;
    private static int count;   //El número de conexiones
    private Timer temporizador;        //Este temporizador es para enviar el pedido al servidor cada 6 segundos
    private PrintWriter pr;     //Para escribir en el archivo
    private long t0;            //El momento en que envía el pedido al servidor
    private long t3;            //El momento en que recibe la respuesta del servidor

    //Constructor
    public Cliente(String nomeServidor, int portaServidor) {
        this.nomeServidor = nomeServidor;
        this.portaServidor = portaServidor;
        Cliente.count = 0;
        this.temporizador = new Timer();
        try {
            //Se guarda en la misma carpeta de ejecución
            this.pr = new PrintWriter("LogClientes.txt", "UTF-8");
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }
    }

    class Conversation extends TimerTask {
        //Función de ejecución Override en TimerTask
        @Override
        public void run() {
            //Número de clientes que van a hacer la sincronización
            if (count < 5) {
                try {
                    System.out.println("--------------------------------------------");
                    System.out.println("Conectando a ... " + nomeServidor + " en el puerto " + portaServidor);

                    //Conecta al servidor
                    Socket cliente = new Socket(nomeServidor, portaServidor);
                    System.out.println("Conectado a " + cliente.getRemoteSocketAddress());

                    //Envía mensaje al servidor
                    t0 = System.currentTimeMillis();
                    OutputStream outToServer = cliente.getOutputStream();
                    DataOutputStream out = new DataOutputStream(outToServer);
                    out.writeUTF("Solicito la hora " + cliente.getLocalSocketAddress());

                    //Recibe mensaje del servidor
                    InputStream inFromServer = cliente.getInputStream();
                    DataInputStream in = new DataInputStream(inFromServer);
                    long t1 = in.readLong();   //Recibe cuando el servidor recibió el mensaje
                    long ts = in.readLong();   //Recibe el tiempo del servidor
                    long t2 = in.readLong();   //Recibe el tiempo de envío en el servidor
                    t3 = System.currentTimeMillis();

                    //Cierra la conexión
                    cliente.close();

                    count ++;

                    //Definir tiempos de atraso para simular los atrasos de solicitud / respuesta
                    //t1 += 500;
                    //ts += 900;
                    t2 += 1500; //Simulando un atraso en la respuesta del servidor
                    t3 += 2000; //Simulando un atraso en la recepción de la respuesta del servidor para el cliente

                    //Cálculo del algoritmo de Cristian
                    long tiv = t3 - t0; //Tiempo que llevó en el cliente, desde su petición al servidor, hasta recibir la respuesta
                    long tm2 = t3 - t2; //Tiempo que llevó para que el mensaje de respuesta del servidor llegara al cliente
                    long tm1 = t1 - t0; //Tiempo que llevó para que el mensaje de petición del cliente llegara al servidor

                    //Fórmula del algoritmo de Cristian
                    long tc = ts + ((tiv + tm2 - tm1)/2);

                    //Guardando los datos en el archivo
                    pr.println("----------------------------------------------------");
                    pr.println("Tiempo de envío del Cliente: " + formataData(t0));
                    pr.println("Tiempo de recepción en el Servidor: " + formataData(t1));
                    pr.println("Tiempo de envío del Servidor: " + formataData(t2));
                    pr.println("Tiempo de recepción en el Cliente: " + formataData(t3));

                    pr.println("\nTiempo marcado en el servidor: " + formataData(ts));
                    pr.println("Tiempo Algoritmo de Cristian: " + formataData(tc));

                    //Imprimiendo en consola
                    System.out.println("\nTiempo de envío del Cliente: " + formataData(t0));
                    System.out.println("Tiempo de recepción en el Servidor: " + formataData(t1));
                    System.out.println("Tiempo de envío del Servidor: " + formataData(t2));
                    System.out.println("Tiempo de recepción en el Cliente: " + formataData(t3));

                    System.out.println("\nTiempo marcado en el servidor: " + formataData(ts));
                    System.out.println("Tiempo Algoritmo de Cristian: " + formataData(tc));

                }
                catch (IOException e) {
                    e.printStackTrace();
                }
            }
            else {
                pr.close(); //Libera el archivo
                temporizador.cancel();
                temporizador.purge();
            }
        }
    }

    public static void main(String [] args) {

        //Nombre del servidor
        String nomeServidor = "Localhost";

        //Puerto del servidor
        int portaServidor = 9092;

        //Crea un cliente que se va a conectar al servidor
        Cliente cliente = new Cliente(nomeServidor, portaServidor);

        //Tiempo en que el objeto Timer va a hacer las conexiones
        long periodo = 6000;

        //Instancia la clase Conversation
        Cliente.Conversation  conversation = cliente.new Conversation();

        cliente.temporizador.schedule(conversation, 0, periodo);
    }

    public String formataData(long data) {
        Timestamp timeStamp = new Timestamp(data);
        Date date = new Date(timeStamp.getTime());

        SimpleDateFormat formato = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss.SSS");
        String dataFormatada = formato.format(date);

        return dataFormatada;
    }
}