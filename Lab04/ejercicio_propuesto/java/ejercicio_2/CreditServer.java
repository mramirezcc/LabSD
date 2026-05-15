package ejercicio_2;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class CreditServer {
    public static void main(String[] args) {
        try {
            CreditCardInterface stub = new CreditCardImpl();
            Registry registry = LocateRegistry.createRegistry(1099);
            registry.rebind("ServicioTarjetas", stub);
            System.out.println(">>> Servidor de Tarjetas con Historial Activo (Puerto 1099)");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}