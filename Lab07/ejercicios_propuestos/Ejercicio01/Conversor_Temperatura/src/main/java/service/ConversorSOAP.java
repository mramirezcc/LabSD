package service;

import javax.jws.WebService;

@WebService(
    endpointInterface = "service.IConversorSOAP",
    serviceName = "ConversorTemperaturaService",
    portName = "ConversorSOAPPort",
    targetNamespace = "http://service/")
public class ConversorSOAP implements IConversorSOAP {

    @Override
    public double cToF(double c) {
        return (c * 9.0 / 5.0) + 32;
    }

    @Override
    public double fToC(double f) {
        return (f - 32) * 5.0 / 9.0;
    }
}