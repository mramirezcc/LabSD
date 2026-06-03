package service;

import javax.jws.WebMethod;
import javax.jws.WebParam;
import javax.jws.WebService;
import model.Producto;
import model.VentaResponse;

@WebService(name = "VentaSOAP")
public interface IVentaSOAP {

    @WebMethod
    Producto buscarProducto(@WebParam(name = "idProducto") String idProducto);

    @WebMethod
    VentaResponse procesarVenta(
        @WebParam(name = "idProducto") String idProducto,
        @WebParam(name = "cantidad") int cantidad,
        @WebParam(name = "cliente") String cliente
    );
}