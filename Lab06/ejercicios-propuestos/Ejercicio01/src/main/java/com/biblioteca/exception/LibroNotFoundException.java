package com.biblioteca.exception;

public class LibroNotFoundException extends RuntimeException {
    public LibroNotFoundException(Long id) {
        super("No se encontró el libro con ID: " + id);
    }
    public LibroNotFoundException(String mensaje) {
        super(mensaje);
    }
}