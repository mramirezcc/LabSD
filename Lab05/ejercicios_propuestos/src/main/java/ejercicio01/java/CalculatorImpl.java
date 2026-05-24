package ejercicio01.java;

import java.rmi.RemoteException;
import java.rmi.server.RemoteServer;
import java.rmi.server.ServerNotActiveException;
import java.rmi.server.UnicastRemoteObject;

public class CalculatorImpl extends UnicastRemoteObject implements Calculator {

    protected CalculatorImpl() throws RemoteException {
        super();
    }

    private void logOperation(String operationDetails) {
        String clientIp = "Desconocido";
        try {
            clientIp = RemoteServer.getClientHost();
        } catch (ServerNotActiveException e) {
            // Llamada local de prueba
        }
        System.out.println("[" + clientIp + "] -> " + operationDetails);
    }

    @Override
    public double add(double a, double b) throws RemoteException {
        double result = a + b;
        logOperation("Suma: " + a + " + " + b + " = " + result);
        return result;
    }

    @Override
    public double subtract(double a, double b) throws RemoteException {
        double result = a - b;
        logOperation("Resta: " + a + " - " + b + " = " + result);
        return result;
    }

    @Override
    public double multiply(double a, double b) throws RemoteException {
        double result = a * b;
        logOperation("Multiplicación: " + a + " * " + b + " = " + result);
        return result;
    }

    @Override
    public double divide(double a, double b) throws RemoteException {
        if (b == 0) {
            logOperation("Intento de división entre cero (" + a + " / 0)");
            throw new ArithmeticException("No se puede dividir entre cero.");
        }
        double result = a / b;
        logOperation("División: " + a + " / " + b + " = " + result);
        return result;
    }

    @Override
    public double power(double a, double b) throws RemoteException {
        double result = Math.pow(a, b);
        logOperation("Potencia: " + a + " ^ " + b + " = " + result);
        return result;
    }
}