package com.biblioteca.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ApiResponse<T> {

    private boolean exito;
    private String mensaje;
    private T datos;
    private LocalDateTime timestamp;
    private int totalRegistros;

    // Constructor para respuestas simples (sin lista)
    public static <T> ApiResponse<T> ok(String mensaje, T datos) {
        return ApiResponse.<T>builder()
                .exito(true)
                .mensaje(mensaje)
                .datos(datos)
                .timestamp(LocalDateTime.now())
                .build();
    }

    // Constructor para respuestas de error
    public static <T> ApiResponse<T> error(String mensaje) {
        return ApiResponse.<T>builder()
                .exito(false)
                .mensaje(mensaje)
                .timestamp(LocalDateTime.now())
                .build();
    }
}