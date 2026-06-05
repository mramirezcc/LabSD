package calculadora;

import javax.jws.WebMethod;
import javax.jws.WebService;

/**
 * Implementación del servicio SOAP de Calculadora.
 */
@WebService(
    targetNamespace = "http://calculadora.soap/",
    serviceName = "CalculadoraSOAPService",
    endpointInterface = "calculadora.ICalculadora"
)
public class CalculadoraSOAP implements ICalculadora {

    @Override
    @WebMethod
    public int sumar(int a, int b) {
        return a + b;
    }
}
