package Lab05.ejercicios_propuestos.ejercicio02.java;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import java.io.IOException;

public class GrpcServer {
    public static void main(String[] args) throws IOException, InterruptedException {
        int puertoServicio = 9090;

        // Instanciamos y vinculamos nuestro servicio de conversión al hilo de red
        Server servidor = ServerBuilder.forPort(puertoServicio)
                .addService(new ConverterImpl())
                .build();

        System.out.println("=====================================================");
        System.out.println("   SERVIDOR gRPC (HTTP/2) - INICIADO EN LA UNSA     ");
        System.out.println("   Puerto Escucha activo: " + puertoServicio          );
        System.out.println("   Esperando peticiones de conversión remota...      ");
        System.out.println("=====================================================");

        servidor.start();
        servidor.awaitTermination(); // Evita que el hilo principal muera
    }
}