package service;

import javax.jws.WebMethod;
import javax.jws.WebParam;
import javax.jws.WebService;

@WebService(name = "ConversorSOAP")
public interface IConversorSOAP {
    
    @WebMethod
    double cToF(@WebParam(name = "c") double c); // <-- Agregar @WebParam aquí
    
    @WebMethod
    double fToC(@WebParam(name = "f") double f); // <-- Agregar @WebParam aquí
}