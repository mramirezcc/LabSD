package ejercicio_3;

import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;

public class CurrencyConverterImpl extends UnicastRemoteObject implements CurrencyConverterInterface {
    
    public CurrencyConverterImpl() throws RemoteException {
        super();
    }

    // --- DE SOLES A EXTRANJERA (Aplicamos precio de VENTA) ---
    @Override public double convertirADolarNA(double monto) throws RemoteException { return monto / VENTA_DOLAR_NA; }
    @Override public double convertirADolarCanadiense(double monto) throws RemoteException { return monto / VENTA_DOLAR_CANADIENSE; }
    @Override public double convertirAPesoChileno(double monto) throws RemoteException { return monto / VENTA_PESO_CHILENO; }
    @Override public double convertirALibraEsterlina(double monto) throws RemoteException { return monto / VENTA_LIBRA_ESTERLINA; }
    @Override public double convertirAYenJapones(double monto) throws RemoteException { return monto / VENTA_YEN_JAPONES; }
    @Override public double convertirAPesoMexicano(double monto) throws RemoteException { return monto / VENTA_PESO_MEXICANO; }
    @Override public double convertirAEuro(double monto) throws RemoteException { return monto / VENTA_EURO; }

    // --- DE EXTRANJERA A SOLES (Aplicamos precio de COMPRA) ---
    @Override public double convertirDesdeDolarNA(double monto) throws RemoteException { return monto * COMPRA_DOLAR_NA; }
    @Override public double convertirDesdeDolarCanadiense(double monto) throws RemoteException { return monto * COMPRA_DOLAR_CANADIENSE; }
    @Override public double convertirDesdePesoChileno(double monto) throws RemoteException { return monto * COMPRA_PESO_CHILENO; }
    @Override public double convertirDesdeLibraEsterlina(double monto) throws RemoteException { return monto * COMPRA_LIBRA_ESTERLINA; }
    @Override public double convertirDesdeYenJapones(double monto) throws RemoteException { return monto * COMPRA_YEN_JAPONES; }
    @Override public double convertirDesdePesoMexicano(double monto) throws RemoteException { return monto * COMPRA_PESO_MEXICANO; }
    @Override public double convertirDesdeEuro(double monto) throws RemoteException { return monto * COMPRA_EURO; }
}