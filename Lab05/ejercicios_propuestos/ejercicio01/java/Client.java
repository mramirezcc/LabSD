package Lab05.ejercicios_propuestos.ejercicio01.java;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {

    public static void main(String[] args) {

        try {

            Registry registry = LocateRegistry.getRegistry("localhost", 1099);

            Calculator calculator = (Calculator) registry.lookup("CalculatorService");

            double multiplication = calculator.multiply(8, 4);
            double division = calculator.divide(20, 5);
            double power = calculator.power(2, 3);

            System.out.println("Multiplicación: " + multiplication);
            System.out.println("División: " + division);
            System.out.println("Potencia: " + power);

        } catch (Exception e) {

            System.out.println("Error en el cliente: " + e.getMessage());

            e.printStackTrace();
        }
    }
}