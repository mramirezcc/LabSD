package Lab05.ejercicios_propuestos.ejercicio01.java;

import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class CalculatorImpl extends UnicastRemoteObject implements Calculator {

    protected CalculatorImpl() throws RemoteException {
        super();
    }

    @Override
    public double multiply(double a, double b) throws RemoteException {
        System.out.println("Multiplicando: " + a + " * " + b);
        return a * b;
    }

    @Override
    public double divide(double a, double b) throws RemoteException {

        if (b == 0) {
            throw new ArithmeticException("No se puede dividir entre cero.");
        }

        System.out.println("Dividiendo: " + a + " / " + b);

        return a / b;
    }

    @Override
    public double power(double a, double b) throws RemoteException {

        System.out.println("Potencia: " + a + " ^ " + b);

        return Math.pow(a, b);
    }
}
