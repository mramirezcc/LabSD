package ejercicio_2;

import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class CreditCardImpl extends UnicastRemoteObject implements CreditCardInterface {
    
    private HashMap<String, Double> saldos = new HashMap<>();
    private HashMap<String, Double> limites = new HashMap<>();
    private HashMap<String, List<String>> historiales = new HashMap<>();
    private DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss");

    public CreditCardImpl() throws RemoteException {
        super();
    }

    @Override
    public String validarORegistrarTarjeta(String nro) throws RemoteException {
        if (nro.length() != 19) return "CANTIDAD_DIGITOS_INVALIDO";
        if (!nro.startsWith("4500-")) return "BANCO_NO_CORRESPONDE";

        if (!saldos.containsKey(nro)) {
            double limiteAsignado = calcularLimiteDesdeNumero(nro);
            saldos.put(nro, limiteAsignado); 
            limites.put(nro, limiteAsignado);
            historiales.put(nro, new ArrayList<>());
            
            // Formato limpio con 2 decimales para el registro inicial
            String registroInicial = String.format("[%s] %-40s  $%.2f", 
                dtf.format(LocalDateTime.now()), "Cuenta activada. Limite:", limiteAsignado);
            historiales.get(nro).add(registroInicial);
        }
        return "OK";
    }

    private double calcularLimiteDesdeNumero(String nro) {
        try {
            String[] partes = nro.split("-");
            int bloque2 = Integer.parseInt(partes[1]);
            if (bloque2 >= 0 && bloque2 <= 999) return 500.00;
            return (bloque2 / 1000) * 1000.00;
        } catch (Exception e) {
            return 500.00; 
        }
    }

    @Override
    public double consultarSaldo(String nro) throws RemoteException {
        return saldos.getOrDefault(nro, -1.0);
    }

    @Override
    public double consultarLimite(String nro) throws RemoteException {
        return limites.getOrDefault(nro, 0.0);
    }

    @Override
    public boolean realizarOperacion(String nro, double monto, String detalle) throws RemoteException {
        if (!saldos.containsKey(nro)) return false;

        double saldoActual = saldos.get(nro);
        double limiteMax = limites.get(nro);

        if (detalle.contains("Abono")) {
            if (saldoActual + monto > limiteMax) return false; 
            saldos.put(nro, saldoActual + monto);
        } else {
            if (saldoActual < monto) return false;
            saldos.put(nro, saldoActual - monto);
        }

        // Formato final: alineación de texto a la izquierda (%-40s) y montos con 2 decimales (%.2f)
        String signo = detalle.contains("Abono") ? "+" : "-";
        String desc = detalle + ":";
        String registro = String.format("[%s] %-40s %s$%.2f", 
            dtf.format(LocalDateTime.now()), desc, signo, monto);
            
        historiales.get(nro).add(registro);
        return true;
    }

    @Override
    public List<String> obtenerHistorial(String nro) throws RemoteException {
        return historiales.getOrDefault(nro, Arrays.asList("Tarjeta no encontrada."));
    }
}