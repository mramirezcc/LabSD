package ejercicio_3;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class CurrencyServer {
    public static void main(String[] args) {
        try {
            CurrencyConverterImpl conversor = new CurrencyConverterImpl();
            Registry registry = LocateRegistry.createRegistry(1099);
            registry.rebind("ServicioConversor", conversor);
            
            System.out.println("Servidor de Cambio de Moneda ACTIVO");
            System.out.println("Esperando solicitudes de conversion...");
            
        } catch (Exception e) {
            System.out.println("Error en el servidor: " + e.getMessage());
        }
    }
}