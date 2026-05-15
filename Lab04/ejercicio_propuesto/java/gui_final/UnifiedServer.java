package gui_final;

import ejercicio_2.CreditCardImpl;
import ejercicio_3.CurrencyConverterImpl;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class UnifiedServer {
    public static void main(String[] args) {
        try {
            // Creamos el registro en el puerto 1099 UNA SOLA VEZ
            Registry registry = LocateRegistry.createRegistry(1099);
            
            // Registramos AMBOS servicios en el mismo puerto
            registry.rebind("ServicioTarjetas", new CreditCardImpl());
            registry.rebind("ServicioConversor", new CurrencyConverterImpl());
            
            System.out.println(" SERVIDOR UNIFICADO RMI ACTIVO");
            System.out.println(" Modulos cargados: Cajero y Conversor");
            
        } catch (Exception e) {
            System.out.println("Error en el servidor unificado: " + e.getMessage());
        }
    }
}