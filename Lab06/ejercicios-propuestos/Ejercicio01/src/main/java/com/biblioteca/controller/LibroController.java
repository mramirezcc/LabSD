package com.biblioteca.controller;

import com.biblioteca.dto.ApiResponse;
import com.biblioteca.dto.LibroDTO;
import com.biblioteca.model.Libro.EstadoLibro;
import com.biblioteca.service.LibroService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * ╔═══════════════════════════════════════════════════╗
 * ║         CONTROLADOR REST - BIBLIOTECA API         ║
 * ╠═══════════════════════════════════════════════════╣
 * ║  GET    /api/libros              → Listar todos   ║
 * ║  GET    /api/libros/{id}         → Buscar por ID  ║
 * ║  GET    /api/libros/isbn/{isbn}  → Buscar por ISBN║
 * ║  GET    /api/libros/buscar?q=    → Búsqueda libre ║
 * ║  GET    /api/libros/genero/{g}   → Por género     ║
 * ║  GET    /api/libros/estado/{e}   → Por estado     ║
 * ║  GET    /api/libros/estadisticas → Estadísticas   ║
 * ║  POST   /api/libros              → Registrar      ║
 * ║  PUT    /api/libros/{id}         → Actualizar     ║
 * ║  PATCH  /api/libros/{id}/stock   → Actualizar     ║
 * ║  DELETE /api/libros/{id}         → Eliminar       ║
 * ╚═══════════════════════════════════════════════════╝
 */
@RestController
@RequestMapping("/api/libros")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Permite peticiones desde el cliente HTML
public class LibroController {

    private final LibroService libroService;

    // ─────────────────────────────────────────
    // GET /api/libros → Listar todos
    // ─────────────────────────────────────────
    @GetMapping
    public ResponseEntity<ApiResponse<List<LibroDTO>>> listarTodos() {
        List<LibroDTO> libros = libroService.listarTodos();
        ApiResponse<List<LibroDTO>> respuesta = ApiResponse.<List<LibroDTO>>builder()
                .exito(true)
                .mensaje("Libros obtenidos correctamente")
                .datos(libros)
                .totalRegistros(libros.size())
                .build();
        return ResponseEntity.ok(respuesta);
    }

    // ─────────────────────────────────────────
    // GET /api/libros/{id} → Buscar por ID
    // ─────────────────────────────────────────
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<LibroDTO>> buscarPorId(@PathVariable Long id) {
        return ResponseEntity.ok(
                ApiResponse.ok("Libro encontrado", libroService.buscarPorId(id))
        );
    }

    // ─────────────────────────────────────────
    // GET /api/libros/isbn/{isbn} → Buscar por ISBN
    // ─────────────────────────────────────────
    @GetMapping("/isbn/{isbn}")
    public ResponseEntity<ApiResponse<LibroDTO>> buscarPorIsbn(@PathVariable String isbn) {
        return ResponseEntity.ok(
                ApiResponse.ok("Libro encontrado", libroService.buscarPorIsbn(isbn))
        );
    }

    // ─────────────────────────────────────────
    // GET /api/libros/buscar?q=termino
    // ─────────────────────────────────────────
    @GetMapping("/buscar")
    public ResponseEntity<ApiResponse<List<LibroDTO>>> buscar(
            @RequestParam(name = "q") String termino) {
        List<LibroDTO> resultados = libroService.buscar(termino);
        return ResponseEntity.ok(ApiResponse.<List<LibroDTO>>builder()
                .exito(true)
                .mensaje("Búsqueda completada para: " + termino)
                .datos(resultados)
                .totalRegistros(resultados.size())
                .build());
    }

    // ─────────────────────────────────────────
    // GET /api/libros/genero/{genero}
    // ─────────────────────────────────────────
    @GetMapping("/genero/{genero}")
    public ResponseEntity<ApiResponse<List<LibroDTO>>> buscarPorGenero(
            @PathVariable String genero) {
        List<LibroDTO> libros = libroService.buscarPorGenero(genero);
        return ResponseEntity.ok(ApiResponse.<List<LibroDTO>>builder()
                .exito(true)
                .mensaje("Libros del género: " + genero)
                .datos(libros)
                .totalRegistros(libros.size())
                .build());
    }

    // ─────────────────────────────────────────
    // GET /api/libros/estado/{estado}
    // ─────────────────────────────────────────
    @GetMapping("/estado/{estado}")
    public ResponseEntity<ApiResponse<List<LibroDTO>>> buscarPorEstado(
            @PathVariable EstadoLibro estado) {
        List<LibroDTO> libros = libroService.buscarPorEstado(estado);
        return ResponseEntity.ok(ApiResponse.<List<LibroDTO>>builder()
                .exito(true)
                .mensaje("Libros con estado: " + estado)
                .datos(libros)
                .totalRegistros(libros.size())
                .build());
    }

    // ─────────────────────────────────────────
    // GET /api/libros/estadisticas
    // ─────────────────────────────────────────
    @GetMapping("/estadisticas")
    public ResponseEntity<ApiResponse<Map<String, Object>>> estadisticas() {
        return ResponseEntity.ok(
                ApiResponse.ok("Estadísticas generadas", libroService.obtenerEstadisticas())
        );
    }

    // ─────────────────────────────────────────
    // POST /api/libros → Registrar libro
    // ─────────────────────────────────────────
    @PostMapping
    public ResponseEntity<ApiResponse<LibroDTO>> registrar(
            @Valid @RequestBody LibroDTO dto) {
        LibroDTO nuevo = libroService.registrar(dto);
        return ResponseEntity
                .status(HttpStatus.CREATED)          // 201 Created
                .body(ApiResponse.ok("Libro registrado exitosamente", nuevo));
    }

    // ─────────────────────────────────────────
    // PUT /api/libros/{id} → Actualizar completo
    // ─────────────────────────────────────────
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<LibroDTO>> actualizar(
            @PathVariable Long id,
            @Valid @RequestBody LibroDTO dto) {
        return ResponseEntity.ok(
                ApiResponse.ok("Libro actualizado correctamente", libroService.actualizar(id, dto))
        );
    }

    // ─────────────────────────────────────────
    // PATCH /api/libros/{id}/stock → Actualizar stock
    // ─────────────────────────────────────────
    @PatchMapping("/{id}/stock")
    public ResponseEntity<ApiResponse<LibroDTO>> actualizarStock(
            @PathVariable Long id,
            @RequestParam int cantidad) {
        return ResponseEntity.ok(
                ApiResponse.ok("Stock actualizado", libroService.actualizarStock(id, cantidad))
        );
    }

    // ─────────────────────────────────────────
    // DELETE /api/libros/{id} → Eliminar
    // ─────────────────────────────────────────
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> eliminar(@PathVariable Long id) {
        libroService.eliminar(id);
        return ResponseEntity.ok(ApiResponse.ok("Libro eliminado correctamente", null));
    }
}