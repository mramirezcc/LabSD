package ejercicio_3;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Scanner;

public class CurrencyClient {
    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            CurrencyConverterInterface conversorRMI = (CurrencyConverterInterface) registry.lookup("ServicioConversor");
            Scanner sc = new Scanner(System.in);

            while (true) {
                System.out.println("\nCASA DE CAMBIO VIRTUAL RMI");
                System.out.println("1. Comprar Moneda Extranjera (Pago con Soles)");
                System.out.println("2. Vender Moneda Extranjera (Recibo Soles)");
                System.out.println("3. Salir");
                System.out.print("Seleccione una operacion: ");
                
                int opPrincipal;
                try {
                    opPrincipal = Integer.parseInt(sc.nextLine());
                } catch (Exception e) { continue; }

                if (opPrincipal == 3) {
                    System.out.println("Cerrando sistema...");
                    break;
                }

                if (opPrincipal == 1 || opPrincipal == 2) {
                    System.out.println("\nMONEDAS DISPONIBLES");
                    System.out.println("1. Dolar de N.A.");
                    System.out.println("2. Dolar Canadiense");
                    System.out.println("3. Peso Chileno");
                    System.out.println("4. Libra Esterlina");
                    System.out.println("5. Yen Japones");
                    System.out.println("6. Peso Mexicano");
                    System.out.println("7. Euro");
                    System.out.println("8. Regresar al Menu Principal");
                    System.out.print("Seleccione la moneda: ");

                    int opMoneda;
                    try {
                        opMoneda = Integer.parseInt(sc.nextLine());
                    } catch (Exception e) { continue; }

                    if (opMoneda == 8) continue;

                    if (opMoneda >= 1 && opMoneda <= 7) {
                        String[] nombresMonedas = {"", "Dolares de N.A.", "Dolares Canadienses", "Pesos Chilenos", "Libras Esterlinas", "Yenes Japoneses", "Pesos Mexicanos", "Euros"};
                        String nomMoneda = nombresMonedas[opMoneda];
                        
                        if (opPrincipal == 1) {
                            System.out.print("Ingrese el monto en SOLES (S/) que desea cambiar: ");
                            double montoSoles = Double.parseDouble(sc.nextLine());
                            double resultado = 0;

                            switch (opMoneda) {
                                case 1: resultado = conversorRMI.convertirADolarNA(montoSoles); break;
                                case 2: resultado = conversorRMI.convertirADolarCanadiense(montoSoles); break;
                                case 3: resultado = conversorRMI.convertirAPesoChileno(montoSoles); break;
                                case 4: resultado = conversorRMI.convertirALibraEsterlina(montoSoles); break;
                                case 5: resultado = conversorRMI.convertirAYenJapones(montoSoles); break;
                                case 6: resultado = conversorRMI.convertirAPesoMexicano(montoSoles); break;
                                case 7: resultado = conversorRMI.convertirAEuro(montoSoles); break;
                            }
                            System.out.printf("Entregas: S/%.2f -> Recibes: %.2f %s%n", montoSoles, resultado, nomMoneda);

                        } else {
                            System.out.print("Ingrese la cantidad de " + nomMoneda + " que desea vender: ");
                            double montoExtranjera = Double.parseDouble(sc.nextLine());
                            double resultado = 0;

                            switch (opMoneda) {
                                case 1: resultado = conversorRMI.convertirDesdeDolarNA(montoExtranjera); break;
                                case 2: resultado = conversorRMI.convertirDesdeDolarCanadiense(montoExtranjera); break;
                                case 3: resultado = conversorRMI.convertirDesdePesoChileno(montoExtranjera); break;
                                case 4: resultado = conversorRMI.convertirDesdeLibraEsterlina(montoExtranjera); break;
                                case 5: resultado = conversorRMI.convertirDesdeYenJapones(montoExtranjera); break;
                                case 6: resultado = conversorRMI.convertirDesdePesoMexicano(montoExtranjera); break;
                                case 7: resultado = conversorRMI.convertirDesdeEuro(montoExtranjera); break;
                            }
                            System.out.printf("Entregas: %.2f %s -> Recibes: S/%.2f%n", montoExtranjera, nomMoneda, resultado);
                        }
                    } else {
                        System.out.println("Opcion no valida.");
                    }
                } else {
                    System.out.println("Opcion no valida.");
                }
            }
        } catch (Exception e) {
            System.out.println("Error en el cliente: " + e.getMessage());
        }
    }
}