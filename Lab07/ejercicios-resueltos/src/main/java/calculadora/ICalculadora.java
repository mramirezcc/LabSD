package calculadora;

import javax.jws.WebMethod;
import javax.jws.WebService;

/**
 * Interfaz del servicio SOAP de Calculadora.
 * Define el contrato (WSDL) del servicio.
 */
@WebService(targetNamespace = "http://calculadora.soap/")
public interface ICalculadora {

    @WebMethod
    int sumar(int a, int b);
}
