package ejercicio_2;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface CreditCardInterface extends Remote {
    // Retorna un mensaje de estado: "OK", "INVALID_PREFIX", "INVALID_LENGTH", etc.
    String validarORegistrarTarjeta(String numeroTarjeta) throws RemoteException;
    double consultarSaldo(String numeroTarjeta) throws RemoteException;
    double consultarLimite(String numeroTarjeta) throws RemoteException;
    boolean realizarOperacion(String numeroTarjeta, double monto, String detalle) throws RemoteException;
    List<String> obtenerHistorial(String numeroTarjeta) throws RemoteException;
}