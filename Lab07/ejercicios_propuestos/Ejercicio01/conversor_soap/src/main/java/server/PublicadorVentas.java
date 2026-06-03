package server;

import javax.xml.ws.Endpoint;
import service.impl.VentaSOAPImpl;

public class PublicadorVentas {
    public static void main(String[] args) {
        String url = "http://localhost:8085/VentaOnlineSOAP";
        System.out.println("🚀 Inicializando el servidor de transacciones e-Commerce...");
        
        Endpoint.publish(url, new VentaSOAPImpl());
        
        System.out.println("📌 Servicio SOAP publicado exitosamente en: " + url + "?wsdl");
        System.out.println("Acceda a la URL para verificar la generación del contrato WSDL.");
    }
}