package com.example.calculator;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;

public class CalculatorServer {

  public static void main(String[] args) throws IOException, InterruptedException {
    Server server = ServerBuilder.forPort(50051)
        .addService(new CalculatorService())
        .build();

    server.start();
    System.out.println("Servidor gRPC iniciado en el puerto 50051...");

    server.awaitTermination();
  }
}
