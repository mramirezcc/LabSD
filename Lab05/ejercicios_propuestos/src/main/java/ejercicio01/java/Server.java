package ejercicio01.java;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Server {

    public static void main(String[] args) {

        try {

            CalculatorImpl calculator = new CalculatorImpl();

            Registry registry = LocateRegistry.createRegistry(1099);

            registry.rebind("CalculatorService", calculator);

            System.out.println("====================================");
            System.out.println(" SERVIDOR RMI INICIADO CORRECTAMENTE ");
            System.out.println(" Puerto: 1099");
            System.out.println("====================================");

        } catch (Exception e) {

            System.out.println("Error en el servidor: " + e.getMessage());

            e.printStackTrace();
        }
    }
}