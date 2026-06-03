package service.impl;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import javax.jws.WebService;
import model.Producto;
import model.VentaResponse;
import service.IVentaSOAP;

@WebService(
    endpointInterface = "service.IVentaSOAP",
    serviceName = "VentaOnlineService",
    portName = "VentaSOAPPort",
    targetNamespace = "http://service/"
)
public class VentaSOAPImpl implements IVentaSOAP {

    // Simulación de base de datos de productos en línea
    private static final Map<String, Producto> inventario = new HashMap<>();

    static {
        inventario.put("PROD01", new Producto("PROD01", "Laptop ASUS ROG Strix", 1250.00, 10));
        inventario.put("PROD02", new Producto("PROD02", "Mouse Logi G Pro X", 115.50, 45));
        inventario.put("PROD03", new Producto("PROD03", "Monitor BenQ 144Hz", 320.00, 5));
    }

    @Override
    public Producto buscarProducto(String idProducto) {
        if (idProducto == null || !inventario.containsKey(idProducto)) {
            return null; // Retorna vacío si el producto no existe
        }
        return inventario.get(idProducto);
    }

    @Override
    public synchronized VentaResponse procesarVenta(String idProducto, int cantidad, String cliente) {
        // Validaciones de negocio robustas
        if (idProducto == null || !inventario.containsKey(idProducto)) {
            return new VentaResponse(false, "Error: El producto especificado no existe.", "ERR-404", 0.0);
        }

        if (cantidad <= 0) {
            return new VentaResponse(false, "Error: La cantidad debe ser mayor a cero.", "ERR-400", 0.0);
        }

        Producto prod = inventario.get(idProducto);

        // Control crítico de Stock
        if (prod.getStock() < cantidad) {
            return new VentaResponse(false, 
                "Transacción declinada: Stock insuficiente. Unidades disponibles: " + prod.getStock(), 
                "ERR-STOCK", 0.0);
        }

        // Procesar la transacción y descontar inventario
        int nuevoStock = prod.getStock() - cantidad;
        prod.setStock(nuevoStock);

        double total = prod.getPrecio() * cantidad;
        String ticketFiscal = "TX-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();

        return new VentaResponse(
            true, 
            "Orden procesada con éxito para el cliente: " + cliente, 
            ticketFiscal, 
            total
        );
    }
}