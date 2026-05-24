package com.biblioteca.exception;

import com.biblioteca.dto.ApiResponse;
import org.springframework.http.*;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // Maneja: libro no encontrado → 404
    @ExceptionHandler(LibroNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResponse<Void> manejarNoEncontrado(LibroNotFoundException ex) {
        return ApiResponse.error(ex.getMessage());
    }

    // Maneja: ISBN duplicado → 409 Conflict
    @ExceptionHandler(IsbnDuplicadoException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ApiResponse<Void> manejarIsbnDuplicado(IsbnDuplicadoException ex) {
        return ApiResponse.error(ex.getMessage());
    }

    // Maneja: errores de validación (@NotBlank, @Size, etc.) → 400
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Map<String, String>> manejarValidacion(MethodArgumentNotValidException ex) {
        Map<String, String> errores = new LinkedHashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String campo = ((FieldError) error).getField();
            String mensaje = error.getDefaultMessage();
            errores.put(campo, mensaje);
        });
        return ApiResponse.<Map<String, String>>builder()
                .exito(false)
                .mensaje("Error de validación en los datos enviados")
                .datos(errores)
                .build();
    }

    // Maneja: cualquier otro error inesperado → 500
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> manejarGeneral(Exception ex) {
        return ApiResponse.error("Error interno del servidor: " + ex.getMessage());
    }
}