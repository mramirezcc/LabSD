package com.biblioteca.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import java.time.LocalDate;

@Entity
@Table(name = "libros")
@Data                   // Genera getters + setters + toString + equals + hashCode
@NoArgsConstructor      // Constructor vacío (requerido por JPA)
@AllArgsConstructor     // Constructor con todos los campos
@Builder                // Patrón Builder para crear objetos fácilmente
public class Libro {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // Auto-incremento
    private Long id;

    @NotBlank(message = "El título no puede estar vacío")
    @Size(min = 2, max = 200, message = "El título debe tener entre 2 y 200 caracteres")
    @Column(nullable = false)
    private String titulo;

    @NotBlank(message = "El autor no puede estar vacío")
    @Column(nullable = false)
    private String autor;

    @NotBlank(message = "El ISBN no puede estar vacío")
    @Pattern(regexp = "^[0-9-]{10,17}$", message = "ISBN inválido")
    @Column(unique = true, nullable = false)
    private String isbn;

    @NotBlank(message = "El género no puede estar vacío")
    private String genero;

    @Min(value = 1, message = "El año debe ser mayor a 0")
    @Max(value = 2030, message = "El año no puede ser futuro lejano")
    private Integer anioPublicacion;

    @Min(value = 0, message = "El stock no puede ser negativo")
    @Column(nullable = false)
    private Integer stock;

    @DecimalMin(value = "0.0", message = "El precio no puede ser negativo")
    private Double precio;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EstadoLibro estado;

    private LocalDate fechaRegistro;

    // Se ejecuta automáticamente antes de persistir
    @PrePersist
    public void prePersist() {
        if (this.fechaRegistro == null) {
            this.fechaRegistro = LocalDate.now();
        }
        if (this.estado == null) {
            this.estado = EstadoLibro.DISPONIBLE;
        }
    }

    public enum EstadoLibro {
        DISPONIBLE, PRESTADO, AGOTADO, BAJA
    }
}