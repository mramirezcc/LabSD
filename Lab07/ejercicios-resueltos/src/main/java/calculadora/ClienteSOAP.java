package calculadora;

import java.net.URL;
import javax.xml.namespace.QName;
import javax.xml.ws.Service;

/**
 * Cliente que consume el servicio SOAP de Calculadora.
 */
public class ClienteSOAP {

    public static void main(String[] args) throws Exception {
        URL url = new URL("http://localhost:8080/calculadora?wsdl");

        QName qname = new QName(
            "http://calculadora.soap/",
            "CalculadoraSOAPService"
        );

        Service service = Service.create(url, qname);
        ICalculadora calc = service.getPort(ICalculadora.class);

        System.out.println("Resultado de sumar(10, 20): " + calc.sumar(10, 20));
    }
}
