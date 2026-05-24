package com.biblioteca.service;

import com.biblioteca.dto.LibroDTO;
import com.biblioteca.exception.*;
import com.biblioteca.model.Libro;
import com.biblioteca.model.Libro.EstadoLibro;
import com.biblioteca.repository.LibroRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Capa de lógica de negocio (Service).
 * Aquí va toda la lógica: validaciones, transformaciones, reglas de negocio.
 * El Controller llama al Service; el Service llama al Repository.
 */
@Service
@RequiredArgsConstructor // Inyección de dependencias por constructor (Lombok)
@Slf4j                   // Logger automático: log.info(), log.error(), etc.
@Transactional           // Todas las operaciones son transaccionales por defecto
public class LibroService {

    private final LibroRepository libroRepository;

    // ─────────────────────────────────────────
    // LISTAR TODOS LOS LIBROS
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<LibroDTO> listarTodos() {
        log.info("Listando todos los libros");
        return libroRepository.findAll()
                .stream()
                .map(this::convertirADTO)
                .collect(Collectors.toList());
    }

    // ─────────────────────────────────────────
    // BUSCAR POR ID
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public LibroDTO buscarPorId(Long id) {
        log.info("Buscando libro con ID: {}", id);
        Libro libro = libroRepository.findById(id)
                .orElseThrow(() -> new LibroNotFoundException(id));
        return convertirADTO(libro);
    }

    // ─────────────────────────────────────────
    // BUSCAR POR ISBN
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public LibroDTO buscarPorIsbn(String isbn) {
        Libro libro = libroRepository.findByIsbn(isbn)
                .orElseThrow(() -> new LibroNotFoundException("No se encontró el ISBN: " + isbn));
        return convertirADTO(libro);
    }

    // ─────────────────────────────────────────
    // BUSCAR (título o autor)
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<LibroDTO> buscar(String termino) {
        log.info("Buscando libros con término: {}", termino);
        return libroRepository.buscarPorTituloOAutor(termino)
                .stream()
                .map(this::convertirADTO)
                .collect(Collectors.toList());
    }

    // ─────────────────────────────────────────
    // BUSCAR POR GÉNERO
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<LibroDTO> buscarPorGenero(String genero) {
        return libroRepository.findByGeneroIgnoreCase(genero)
                .stream()
                .map(this::convertirADTO)
                .collect(Collectors.toList());
    }

    // ─────────────────────────────────────────
    // BUSCAR POR ESTADO
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<LibroDTO> buscarPorEstado(EstadoLibro estado) {
        return libroRepository.findByEstado(estado)
                .stream()
                .map(this::convertirADTO)
                .collect(Collectors.toList());
    }

    // ─────────────────────────────────────────
    // REGISTRAR NUEVO LIBRO
    // ─────────────────────────────────────────
    public LibroDTO registrar(LibroDTO dto) {
        // Validar ISBN único
        if (libroRepository.existsByIsbn(dto.getIsbn())) {
            throw new IsbnDuplicadoException(dto.getIsbn());
        }

        Libro libro = convertirAEntidad(dto);
        Libro guardado = libroRepository.save(libro);
        log.info("Libro registrado con ID: {}", guardado.getId());
        return convertirADTO(guardado);
    }

    // ─────────────────────────────────────────
    // ACTUALIZAR LIBRO COMPLETO (PUT)
    // ─────────────────────────────────────────
    public LibroDTO actualizar(Long id, LibroDTO dto) {
        Libro existente = libroRepository.findById(id)
                .orElseThrow(() -> new LibroNotFoundException(id));

        // Si cambió el ISBN, verificar que el nuevo no exista
        if (!existente.getIsbn().equals(dto.getIsbn()) &&
                libroRepository.existsByIsbn(dto.getIsbn())) {
            throw new IsbnDuplicadoException(dto.getIsbn());
        }

        existente.setTitulo(dto.getTitulo());
        existente.setAutor(dto.getAutor());
        existente.setIsbn(dto.getIsbn());
        existente.setGenero(dto.getGenero());
        existente.setAnioPublicacion(dto.getAnioPublicacion());
        existente.setStock(dto.getStock());
        existente.setPrecio(dto.getPrecio());
        if (dto.getEstado() != null) {
            existente.setEstado(dto.getEstado());
        }

        Libro actualizado = libroRepository.save(existente);
        log.info("Libro actualizado con ID: {}", id);
        return convertirADTO(actualizado);
    }

    // ─────────────────────────────────────────
    // ACTUALIZAR STOCK (PATCH)
    // ─────────────────────────────────────────
    public LibroDTO actualizarStock(Long id, int nuevoStock) {
        if (nuevoStock < 0) throw new IllegalArgumentException("El stock no puede ser negativo");
        Libro libro = libroRepository.findById(id)
                .orElseThrow(() -> new LibroNotFoundException(id));
        libro.setStock(nuevoStock);
        // Actualizar estado automáticamente según stock
        if (nuevoStock == 0) libro.setEstado(EstadoLibro.AGOTADO);
        else if (libro.getEstado() == EstadoLibro.AGOTADO) libro.setEstado(EstadoLibro.DISPONIBLE);
        return convertirADTO(libroRepository.save(libro));
    }

    // ─────────────────────────────────────────
    // ELIMINAR LIBRO
    // ─────────────────────────────────────────
    public void eliminar(Long id) {
        if (!libroRepository.existsById(id)) {
            throw new LibroNotFoundException(id);
        }
        libroRepository.deleteById(id);
        log.info("Libro eliminado con ID: {}", id);
    }

    // ─────────────────────────────────────────
    // ESTADÍSTICAS
    // ─────────────────────────────────────────
    @Transactional(readOnly = true)
    public Map<String, Object> obtenerEstadisticas() {
        long total = libroRepository.count();
        long disponibles = libroRepository.findByEstado(EstadoLibro.DISPONIBLE).size();
        long prestados = libroRepository.findByEstado(EstadoLibro.PRESTADO).size();
        long agotados = libroRepository.findByEstado(EstadoLibro.AGOTADO).size();

        // Agrupar por género
        List<Object[]> porGenero = libroRepository.contarPorGenero();
        Map<String, Long> generos = porGenero.stream()
                .collect(Collectors.toMap(
                        row -> (String) row[0],
                        row -> (Long) row[1]
                ));

        return Map.of(
                "totalLibros", total,
                "disponibles", disponibles,
                "prestados", prestados,
                "agotados", agotados,
                "porGenero", generos
        );
    }

    // ─────────────────────────────────────────
    // CONVERSORES (Entidad ↔ DTO)
    // ─────────────────────────────────────────
    private LibroDTO convertirADTO(Libro libro) {
        return LibroDTO.builder()
                .id(libro.getId())
                .titulo(libro.getTitulo())
                .autor(libro.getAutor())
                .isbn(libro.getIsbn())
                .genero(libro.getGenero())
                .anioPublicacion(libro.getAnioPublicacion())
                .stock(libro.getStock())
                .precio(libro.getPrecio())
                .estado(libro.getEstado())
                .fechaRegistro(libro.getFechaRegistro() != null
                        ? libro.getFechaRegistro().toString() : null)
                .build();
    }

    private Libro convertirAEntidad(LibroDTO dto) {
        return Libro.builder()
                .titulo(dto.getTitulo())
                .autor(dto.getAutor())
                .isbn(dto.getIsbn())
                .genero(dto.getGenero())
                .anioPublicacion(dto.getAnioPublicacion())
                .stock(dto.getStock() != null ? dto.getStock() : 0)
                .precio(dto.getPrecio())
                .estado(dto.getEstado() != null ? dto.getEstado() : EstadoLibro.DISPONIBLE)
                .fechaRegistro(LocalDate.now())
                .build();
    }
}