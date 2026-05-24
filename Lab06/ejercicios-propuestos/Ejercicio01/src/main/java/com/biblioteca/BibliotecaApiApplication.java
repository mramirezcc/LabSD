package com.biblioteca;

import com.biblioteca.model.Libro;
import com.biblioteca.model.Libro.EstadoLibro;
import com.biblioteca.repository.LibroRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.time.LocalDate;
import java.util.List;

@SpringBootApplication
@Slf4j
public class BibliotecaApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(BibliotecaApiApplication.class, args);
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        log.info("  ✅  Biblioteca API iniciada correctamente");
        log.info("  🌐  URL:     http://localhost:8080/api/libros");
        log.info("  🗄️  Base de datos H2: http://localhost:8080/h2-console");
        log.info("  📋  JDBC URL: jdbc:h2:mem:bibliotecadb");
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }

    /**
     * Se ejecuta al iniciar la app y carga datos de ejemplo automáticamente.
     */
    @Bean
    CommandLineRunner cargarDatosIniciales(LibroRepository repo) {
        return args -> {
            if (repo.count() == 0) {
                List<Libro> libros = List.of(
                    Libro.builder()
                        .titulo("Clean Code: A Handbook of Agile Software Craftsmanship")
                        .autor("Robert C. Martin")
                        .isbn("978-0132350884")
                        .genero("Programación")
                        .anioPublicacion(2008)
                        .stock(5)
                        .precio(49.99)
                        .estado(EstadoLibro.DISPONIBLE)
                        .fechaRegistro(LocalDate.now())
                        .build(),
                    Libro.builder()
                        .titulo("The Pragmatic Programmer")
                        .autor("David Thomas")
                        .isbn("978-0201616224")
                        .genero("Programación")
                        .anioPublicacion(1999)
                        .stock(3)
                        .precio(44.99)
                        .estado(EstadoLibro.DISPONIBLE)
                        .fechaRegistro(LocalDate.now())
                        .build(),
                    Libro.builder()
                        .titulo("Design Patterns: Elements of Reusable Object-Oriented Software")
                        .autor("Gang of Four")
                        .isbn("978-0201633610")
                        .genero("Arquitectura")
                        .anioPublicacion(1994)
                        .stock(2)
                        .precio(55.00)
                        .estado(EstadoLibro.DISPONIBLE)
                        .fechaRegistro(LocalDate.now())
                        .build(),
                    Libro.builder()
                        .titulo("Cien Años de Soledad")
                        .autor("Gabriel García Márquez")
                        .isbn("978-0060883287")
                        .genero("Novela")
                        .anioPublicacion(1967)
                        .stock(0)
                        .precio(18.50)
                        .estado(EstadoLibro.AGOTADO)
                        .fechaRegistro(LocalDate.now())
                        .build(),
                    Libro.builder()
                        .titulo("Introduction to Algorithms")
                        .autor("Thomas H. Cormen")
                        .isbn("978-0262033848")
                        .genero("Algoritmos")
                        .anioPublicacion(2009)
                        .stock(4)
                        .precio(89.99)
                        .estado(EstadoLibro.PRESTADO)
                        .fechaRegistro(LocalDate.now())
                        .build()
                );
                repo.saveAll(libros);
                log.info("✅ {} libros de ejemplo cargados en la base de datos", libros.size());
            }
        };
    }
}