package ejercicio01.java;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Calculator extends Remote {
    double add(double a, double b) throws RemoteException;      
    double subtract(double a, double b) throws RemoteException;  
    double multiply(double a, double b) throws RemoteException;
    double divide(double a, double b) throws RemoteException;
    double power(double a, double b) throws RemoteException;
}