package publisher;

import javax.xml.ws.Endpoint;
import service.ConversorSOAP;

public class Publicador {

    public static void main(String[] args) {

        String host = "localhost";
        int port = 8080;
        String path = "/ConversorSOAP";
        String url = "http://" + host + ":" + port + path;

        Endpoint endpoint = Endpoint.publish(url, new ConversorSOAP());

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            endpoint.stop();
            System.out.println("\nServicio SOAP detenido.");
        }));

        System.out.println();
        System.out.println("  +------------------------------------------+");
        System.out.println("  |   SERVICIO SOAP - Conversor Temperatura  |");
        System.out.println("  +------------------------------------------+");
        System.out.println("  |  URL  : " + url + "               |");
        System.out.println("  |  WSDL : " + url + "?wsdl          |");
        System.out.println("  +------------------------------------------+");
        System.out.println("  |  Presiona Ctrl+C para detener            |");
        System.out.println("  +------------------------------------------+");
        System.out.println();
    }
}
