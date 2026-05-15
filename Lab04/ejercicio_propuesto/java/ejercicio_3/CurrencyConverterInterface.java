package ejercicio_3;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface CurrencyConverterInterface extends Remote {
    
    // Constantes de VENTA (El banco te vende moneda extranjera, tú das Soles)
    double VENTA_DOLAR_NA = 3.419;
    double VENTA_DOLAR_CANADIENSE = 2.497;
    double VENTA_PESO_CHILENO = 0.003;
    double VENTA_LIBRA_ESTERLINA = 4.737;
    double VENTA_YEN_JAPONES = 0.022;
    double VENTA_PESO_MEXICANO = 0.199;
    double VENTA_EURO = 4.172;

    // Constantes de COMPRA (El banco compra tu moneda extranjera, te da Soles)
    double COMPRA_DOLAR_NA = 3.413;
    double COMPRA_DOLAR_CANADIENSE = 2.366;
    double COMPRA_PESO_CHILENO = 0.003; 
    double COMPRA_LIBRA_ESTERLINA = 4.737; 
    double COMPRA_YEN_JAPONES = 0.022;
    double COMPRA_PESO_MEXICANO = 0.198;
    double COMPRA_EURO = 3.762;

    // Métodos para VENDER SOLES (Comprar moneda extranjera) -> Se divide entre VENTA
    double convertirADolarNA(double monto) throws RemoteException;
    double convertirADolarCanadiense(double monto) throws RemoteException;
    double convertirAPesoChileno(double monto) throws RemoteException;
    double convertirALibraEsterlina(double monto) throws RemoteException;
    double convertirAYenJapones(double monto) throws RemoteException;
    double convertirAPesoMexicano(double monto) throws RemoteException;
    double convertirAEuro(double monto) throws RemoteException;

    // Métodos para COMPRAR SOLES (Vender moneda extranjera) -> Se multiplica por COMPRA
    double convertirDesdeDolarNA(double monto) throws RemoteException;
    double convertirDesdeDolarCanadiense(double monto) throws RemoteException;
    double convertirDesdePesoChileno(double monto) throws RemoteException;
    double convertirDesdeLibraEsterlina(double monto) throws RemoteException;
    double convertirDesdeYenJapones(double monto) throws RemoteException;
    double convertirDesdePesoMexicano(double monto) throws RemoteException;
    double convertirDesdeEuro(double monto) throws RemoteException;
}