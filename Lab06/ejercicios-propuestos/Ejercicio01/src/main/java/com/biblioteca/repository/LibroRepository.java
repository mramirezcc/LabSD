package com.biblioteca.repository;

import com.biblioteca.model.Libro;
import com.biblioteca.model.Libro.EstadoLibro;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface LibroRepository extends JpaRepository<Libro, Long> {

    // Buscar por ISBN exacto
    Optional<Libro> findByIsbn(String isbn);

    // Buscar por autor (ignorando mayúsculas/minúsculas)
    List<Libro> findByAutorContainingIgnoreCase(String autor);

    // Buscar por género
    List<Libro> findByGeneroIgnoreCase(String genero);

    // Buscar por estado (DISPONIBLE, PRESTADO, etc.)
    List<Libro> findByEstado(EstadoLibro estado);

    // Buscar libros con stock mayor a cero
    List<Libro> findByStockGreaterThan(int stock);

    // Búsqueda combinada por título o autor (JPQL)
    @Query("SELECT l FROM Libro l WHERE " +
           "LOWER(l.titulo) LIKE LOWER(CONCAT('%', :termino, '%')) OR " +
           "LOWER(l.autor) LIKE LOWER(CONCAT('%', :termino, '%'))")
    List<Libro> buscarPorTituloOAutor(@Param("termino") String termino);

    // Verificar si ya existe un ISBN
    boolean existsByIsbn(String isbn);

    // Contar libros por género
    @Query("SELECT l.genero, COUNT(l) FROM Libro l GROUP BY l.genero")
    List<Object[]> contarPorGenero();
}