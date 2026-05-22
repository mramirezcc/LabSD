package com.example.calculator;

import io.grpc.stub.StreamObserver;

public class CalculatorService extends CalculatorGrpc.CalculatorImplBase {

  @Override
  public void sum(CalculatorProto.Request req, StreamObserver<CalculatorProto.Response> responseObserver) {
    int result = req.getA() + req.getB();
    CalculatorProto.Response response = CalculatorProto.Response.newBuilder()
        .setResult(result)
        .build();
    responseObserver.onNext(response);
    responseObserver.onCompleted();
  }
}
