package calculadora;

import javax.xml.ws.Endpoint;

/**
 * Publica el servicio SOAP en http://localhost:8080/calculadora
 */
public class Publicador {

    public static void main(String[] args) {
        Endpoint.publish(
            "http://localhost:8080/calculadora",
            new CalculadoraSOAP()
        );
        System.out.println("Servicio SOAP activo en http://localhost:8080/calculadora");
        System.out.println("WSDL disponible en http://localhost:8080/calculadora?wsdl");
        System.out.println("Presiona Ctrl+C para detener el servicio.");
    }
}
