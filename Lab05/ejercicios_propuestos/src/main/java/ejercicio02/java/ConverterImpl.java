package ejercicio02.java;

import io.grpc.stub.StreamObserver;

public class ConverterImpl extends ConverterGrpc.ConverterImplBase {

    @Override
    public void convert(ConvertRequest request, StreamObserver<ConvertResponse> responseObserver) {

        double value  = request.getValue();
        String type   = request.getConversionType();
        double result = 0;
        String message;

        try {
            switch (type) {

                // ── TEMPERATURA ───────────────────────────────────────────────
                case "C_TO_F":
                    result  = (value * 1.8) + 32;
                    message = "Celsius → Fahrenheit";
                    break;
                case "F_TO_C":
                    result  = (value - 32) / 1.8;
                    message = "Fahrenheit → Celsius";
                    break;
                case "C_TO_K":
                    result  = value + 273.15;
                    message = "Celsius → Kelvin";
                    break;
                case "K_TO_C":
                    result  = value - 273.15;
                    message = "Kelvin → Celsius";
                    break;

                // ── MONEDA ────────────────────────────────────────────────────
                case "PEN_TO_USD":
                    result  = value * 0.27;
                    message = "Soles → Dólares";
                    break;
                case "USD_TO_PEN":
                    result  = value * 3.75;
                    message = "Dólares → Soles";
                    break;
                case "USD_TO_EUR":
                    result  = value * 0.92;
                    message = "Dólares → Euros";
                    break;
                case "EUR_TO_USD":
                    result  = value * 1.09;
                    message = "Euros → Dólares";
                    break;

                // ── DISTANCIA ─────────────────────────────────────────────────
                case "KM_TO_MI":
                    result  = value * 0.621371;
                    message = "Kilómetros → Millas";
                    break;
                case "MI_TO_KM":
                    result  = value * 1.60934;
                    message = "Millas → Kilómetros";
                    break;
                case "M_TO_CM":
                    result  = value * 100;
                    message = "Metros → Centímetros";
                    break;
                case "CM_TO_M":
                    result  = value / 100;
                    message = "Centímetros → Metros";
                    break;

                // ── PESO ──────────────────────────────────────────────────────
                case "KG_TO_LB":
                    result  = value * 2.20462;
                    message = "Kilogramos → Libras";
                    break;
                case "LB_TO_KG":
                    result  = value * 0.453592;
                    message = "Libras → Kilogramos";
                    break;

                // ── VELOCIDAD ─────────────────────────────────────────────────
                case "KMH_TO_MS":
                    result  = value / 3.6;
                    message = "Km/h → m/s";
                    break;
                case "MS_TO_KMH":
                    result  = value * 3.6;
                    message = "m/s → Km/h";
                    break;

                // ── TIEMPO ────────────────────────────────────────────────────
                case "H_TO_MIN":
                    result  = value * 60;
                    message = "Horas → Minutos";
                    break;
                case "MIN_TO_SEC":
                    result  = value * 60;
                    message = "Minutos → Segundos";
                    break;

                default:
                    // ── Respuesta de error limpia (NO lanza onError) ──────────
                    System.out.println("[SERVIDOR] Tipo desconocido recibido: " + type);
                    ConvertResponse errResp = ConvertResponse.newBuilder()
                            .setResult(0)
                            .setMessage("Error: tipo de conversión no reconocido → " + type)
                            .build();
                    responseObserver.onNext(errResp);
                    responseObserver.onCompleted();
                    return;
            }

            System.out.println("[SERVIDOR] " + message + ": " + value + " = " + result);

            ConvertResponse response = ConvertResponse.newBuilder()
                    .setResult(result)
                    .setMessage(message)
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();

        } catch (Exception e) {
            // Cualquier otro error también se devuelve como respuesta limpia
            System.err.println("[SERVIDOR] Error inesperado: " + e.getMessage());
            ConvertResponse errResp = ConvertResponse.newBuilder()
                    .setResult(0)
                    .setMessage("Error interno del servidor: " + e.getMessage())
                    .build();
            responseObserver.onNext(errResp);
            responseObserver.onCompleted();
        }
    }
}