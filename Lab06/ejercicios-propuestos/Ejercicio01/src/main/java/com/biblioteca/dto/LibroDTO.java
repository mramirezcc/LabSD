package com.biblioteca.dto;

import com.biblioteca.model.Libro.EstadoLibro;
import jakarta.validation.constraints.*;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LibroDTO {

    private Long id;

    @NotBlank(message = "El título no puede estar vacío")
    @Size(min = 2, max = 200)
    private String titulo;

    @NotBlank(message = "El autor es requerido")
    private String autor;

    @NotBlank(message = "El ISBN es requerido")
    private String isbn;

    @NotBlank(message = "El género es requerido")
    private String genero;

    @Min(1) @Max(2030)
    private Integer anioPublicacion;

    @Min(0)
    private Integer stock;

    @DecimalMin("0.0")
    private Double precio;

    private EstadoLibro estado;
    private String fechaRegistro;
}