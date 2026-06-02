package consumer;

import java.net.URL;
import javax.xml.namespace.QName;
import javax.xml.ws.Service;

import service.IConversorSOAP;
public class Consumidor {

    public static void main(String[] args) throws Exception {

        URL wsdlUrl =
                new URL(
                        "http://localhost:8080/ConversorSOAP?wsdl"
                );

        QName qname =
                new QName(
                        "http://service/",
                        "ConversorTemperaturaService"
                );

        Service service =
                Service.create(wsdlUrl, qname);

        IConversorSOAP proxy =
                service.getPort(
                        IConversorSOAP.class
                );

        System.out.println("=================================");
        System.out.println(" PRUEBAS DEL SERVICIO SOAP");
        System.out.println("=================================");

        System.out.println(
                "30 °C -> "
                + proxy.cToF(30)
                + " °F"
        );

        System.out.println(
                "86 °F -> "
                + proxy.fToC(86)
                + " °C"
        );

        System.out.println(
                "0 °C -> "
                + proxy.cToF(0)
                + " °F"
        );

        System.out.println(
                "100 °C -> "
                + proxy.cToF(100)
                + " °F"
        );

        System.out.println("=================================");
    }
}