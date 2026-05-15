1package ejercicio_2;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.*;

public class CreditClient {
    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            CreditCardInterface tarjetaRMI = (CreditCardInterface) registry.lookup("ServicioTarjetas");
            Scanner sc = new Scanner(System.in);
            Random rnd = new Random();

            // CICLO PRINCIPAL: Mantiene el cajero encendido siempre
            while (true) {
                System.out.println("  BIENVENIDO AL CAJERO AUTOMATICO");
                System.out.print("Ingrese Numero de Tarjeta: ");
                String nro = sc.nextLine();

                if (nro.equalsIgnoreCase("salir")) {
                    System.out.println("Apagando cajero... ¡Hasta pronto!");
                    break; // Esto apaga el programa por completo
                }

                String status = tarjetaRMI.validarORegistrarTarjeta(nro);
                
                if (!status.equals("OK")) {
                    if (status.equals("CANTIDAD_DIGITOS_INVALIDO")) 
                        System.out.println("Error: Cantidad de digitos invalido.");
                    else if (status.equals("BANCO_NO_CORRESPONDE"))
                        System.out.println("Error: No corresponde a este banco.");
                    continue; // Vuelve a pedir la tarjeta en lugar de cerrar el programa
                }

                System.out.printf("Tarjeta aceptada. Limite de credito asignado: $%.2f%n", tarjetaRMI.consultarLimite(nro));

                boolean enMenu = true;
                // CICLO DEL MENÚ: Funciona mientras la tarjeta esté ingresada
                while (enMenu) {
                    System.out.println("\n MENU");
                    System.out.println("1. Consultar Saldo");
                    System.out.println("2. Pago en Linea (Virtual)");
                    System.out.println("3. Abonar a Tarjeta");
                    System.out.println("4. Ver Historial");
                    System.out.println("5. Salir");
                    System.out.print("Seleccione: ");
                    
                    int op;
                    try {
                        op = Integer.parseInt(sc.nextLine());
                    } catch (Exception e) { continue; }

                    if (op == 5) {
                        System.out.println("Retirando tarjeta...");
                        enMenu = false; // Rompe el ciclo del menú y vuelve al ciclo principal
                        break;
                    }

                    switch (op) {
                        case 1:
                            System.out.printf("-> Saldo Disponible: $%.2f de $%.2f%n", 
                                tarjetaRMI.consultarSaldo(nro), tarjetaRMI.consultarLimite(nro));
                            break;

                        case 2:
                            System.out.print("Monto Compra Virtual: ");
                            double m2 = Double.parseDouble(sc.nextLine());
                            
                            if (m2 > tarjetaRMI.consultarSaldo(nro)) {
                                System.out.println("Rechazado: Saldo insuficiente para realizar esta compra.");
                                break; 
                            }
                            
                            int cod = 100000 + rnd.nextInt(900000);
                            System.out.println("[SISTEMA] Codigo de verificacion: " + cod);
                            System.out.print("¿Confirmar el pago? (Si/No): ");
                            if (sc.nextLine().equalsIgnoreCase("Si")) {
                                if(tarjetaRMI.realizarOperacion(nro, m2, "Compra Virtual (Cod:" + cod + ")"))
                                    System.out.println("Transaccion Autorizada.");
                                else 
                                    System.out.println("Rechazado: Ocurrió un error en la transacción.");
                            } else {
                                System.out.println("Operacion cancelada.");
                            }
                            break;

                        case 3:
                            double limite = tarjetaRMI.consultarLimite(nro);
                            double saldo = tarjetaRMI.consultarSaldo(nro);
                            double maxAbono = limite - saldo;
                            
                            if (maxAbono <= 0) {
                                System.out.println("Su tarjeta no tiene deuda actualmente. No es posible realizar abonos.");
                                break; 
                            }
                            
                            System.out.printf("Puede abonar como máximo: $%.2f%n", maxAbono);
                            System.out.print("Monto a Abonar: ");
                            double m3 = Double.parseDouble(sc.nextLine());
                            
                            if(tarjetaRMI.realizarOperacion(nro, m3, "Abono (Pago Deuda)"))
                                System.out.println("Abono procesado correctamente.");
                            else 
                                System.out.printf("ERROR: El abono excede el limite ($%.2f).%n", limite);
                            break;

                        case 4:
                            System.out.println("\n HISTORIAL");
                            for(String t : tarjetaRMI.obtenerHistorial(nro)) System.out.println(t);
                            break;
                            
                        default:
                            System.out.println("-> Opcion no valida.");
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}