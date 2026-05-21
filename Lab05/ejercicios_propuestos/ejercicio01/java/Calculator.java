package Lab05.ejercicios_propuestos.ejercicio01.java;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Calculator extends Remote {
    double add(double a, double b) throws RemoteException;       // NUEVO
    double subtract(double a, double b) throws RemoteException;  // NUEVO
    double multiply(double a, double b) throws RemoteException;
    double divide(double a, double b) throws RemoteException;
    double power(double a, double b) throws RemoteException;
}