import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;

public class Servidor extends Thread {

    private final ServerSocket servidorSocket;
    private long tempoRecv;  //El tiempo al recibir el mensaje del cliente
    private long tempoEnvio;  //El momento en que envía el mensaje al cliente

    public Servidor(int port) throws IOException {
        servidorSocket = new ServerSocket(port);
    }

    @Override
    public void run() {
        while (true) {
            try {
                //Salida del nombre del servidor
                String nomeHost = java.net.InetAddress.getLocalHost().getHostName();
                System.out.println("--------------------------------------------");
                System.out.println("Nombre del Servidor: " + nomeHost);

                System.out.println("Esperando cliente en el puerto " + servidorSocket.getLocalPort() + "...");

                //Acepta una conexión de clientes
                Socket server = servidorSocket.accept();
                System.out.println("Conectado en: " + server.getRemoteSocketAddress());

                //Recibir mensaje de clientes
                DataInputStream in = new DataInputStream(server.getInputStream());
                System.out.println(in.readUTF());
                tempoRecv = System.currentTimeMillis();

                //Enviar mensaje de vuelta a los clientes
                DataOutputStream out = new DataOutputStream(server.getOutputStream());
                long tempoServidor = System.currentTimeMillis();
                tempoEnvio = System.currentTimeMillis();

                out.writeLong(tempoRecv);      //Envía el tiempo cuando recibió el mensaje del cliente
                out.writeLong(tempoServidor);  //Envía el tiempo actual del servidor
                out.writeLong(tempoEnvio);     //Envía el tiempo de envío para el cliente

                //Cierra la conexión
                server.close();
            } catch (SocketTimeoutException s) {
                System.out.println("¡El socket expiró!");
                break;
            } catch (IOException e) {
                e.printStackTrace();
                break;
            }
        }
    }

    public static void main(String [] args) {
        int porta = 9092;
        try {
            Thread t = new Servidor(porta);
            t.start();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}