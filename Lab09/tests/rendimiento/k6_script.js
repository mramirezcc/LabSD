// k6 Performance Test Script - LogiFresh S.A.
// Prueba de rendimiento: 100 usuarios concurrentes durante 5 minutos
//
// Instalacion: https://k6.io/docs/get-started/installation/
// Ejecutar: k6 run tests/rendimiento/k6_script.js
//
// Requiere que los servicios esten corriendo (python main.py)

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Metricas personalizadas
const tiempoPedido = new Trend('tiempo_creacion_pedido', true);
const tasaErrores = new Rate('errores_pedido');
const pedidosExitosos = new Counter('pedidos_exitosos');
const pedidosFallidos = new Counter('pedidos_fallidos');

export const options = {
  // 100 usuarios concurrentes durante 5 minutos con ramp-up gradual
  stages: [
    { duration: '30s', target: 20 },   // Subir a 20 usuarios en 30s
    { duration: '30s', target: 50 },   // Subir a 50 usuarios
    { duration: '30s', target: 80 },   // Subir a 80 usuarios
    { duration: '30s', target: 100 },  // Llegar a 100 usuarios
    { duration: '2m',  target: 100 },  // Mantener 100 usuarios por 2 min
    { duration: '30s', target: 0 },    // Bajar a 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],     // 95% de requests < 5s
    http_req_failed: ['rate<0.1'],          // Menos de 10% de errores
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

const BASE_PEDIDOS = 'http://127.0.0.1:5001';
const BASE_INVENTARIO = 'http://127.0.0.1:5002';
const BASE_FACTURACION = 'http://127.0.0.1:5003';
const BASE_TRANSPORTE = 'http://127.0.0.1:5004';
const BASE_NOTIFICACIONES = 'http://127.0.0.1:5005';

const PRODUCTOS = ['P001', 'P002', 'P003', 'P004', 'P005',
                    'P006', 'P007', 'P008', 'P009', 'P010'];

const NOMBRES_CLIENTES = [
  'Supermercado El Sol', 'Tienda Express', 'Mercado Central',
  'Distribuidora Norte', 'Bodega La Esquina', 'Supermercado A1',
  'Tienda Del Barrio', 'Minimarket Rápido', 'Almacenes Perú',
  'Comercial Andina'
];

const DIRECCIONES = [
  'Av. Arequipa 450', 'Jr. Lima 100', 'Av. Central 200',
  'Av. Panamericana 500', 'Jr. Bolognesi 101', 'Av. Ejército 300',
  'Calle Comercio 45', 'Av. La Marina 890', 'Jr. Puno 234',
  'Av. Brasil 1200'
];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function crearPedido() {
  const producto_id = randomItem(PRODUCTOS);
  const cantidad = Math.floor(Math.random() * 5) + 1;
  const cliente = `${randomItem(NOMBRES_CLIENTES)}-${__VU}-${__ITER}`;

  const payload = JSON.stringify({
    cliente: cliente,
    email: `cliente${__VU}@test.pe`,
    direccion: randomItem(DIRECCIONES),
    productos: [{ producto_id: producto_id, cantidad: cantidad }],
    codigo_promocion: Math.random() > 0.5 ? '' : 'DESC10'
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
  };

  const start = new Date();
  try {
    const res = http.post(`${BASE_PEDIDOS}/pedido`, payload, params);
    const duration = new Date() - start;

    tiempoPedido.add(duration);

    const success = check(res, {
      'status es 201': (r) => r.status === 201,
      'tiene pedido_id': (r) => r.json('pedido_id') !== undefined,
      'tiene factura_id': (r) => r.json('factura_id') !== undefined,
      'total > 0': (r) => r.json('total') > 0,
    });

    if (success) {
      pedidosExitosos.add(1);
    } else {
      pedidosFallidos.add(1);
    }
    tasaErrores.add(!success);

    return success;
  } catch (e) {
    pedidosFallidos.add(1);
    tasaErrores.add(true);
    return false;
  }
}

function consultarInventario() {
  const producto_id = randomItem(PRODUCTOS);
  try {
    const res = http.get(`${BASE_INVENTARIO}/inventario/${producto_id}`, {
      timeout: '10s',
    });
    check(res, {
      'consulta inventario OK': (r) => r.status === 200 || r.status === 404,
    });
  } catch (e) {}
}

function listarPedidos() {
  try {
    const res = http.get(`${BASE_PEDIDOS}/pedidos`, { timeout: '10s' });
    check(res, {
      'listado pedidos OK': (r) => r.status === 200,
    });
  } catch (e) {}
}

function consultarFacturas() {
  try {
    const res = http.get(`${BASE_FACTURACION}/facturas`, { timeout: '10s' });
    check(res, {
      'listado facturas OK': (r) => r.status === 200,
    });
  } catch (e) {}
}

// Escenario principal
export default function () {
  group('Flujo Principal - Crear Pedido', function () {
    crearPedido();
  });

  // Simular otras operaciones del sistema
  sleep(Math.random() * 2);

  group('Consultas de Soporte', function () {
    if (Math.random() < 0.3) {
      consultarInventario();
    }
    if (Math.random() < 0.2) {
      listarPedidos();
    }
    if (Math.random() < 0.2) {
      consultarFacturas();
    }
  });

  sleep(Math.random() * 3 + 1); // Pausa entre 1 y 4 segundos
}

// Funcion que se ejecuta al finalizar
export function handleSummary(data) {
  const resumen = {
    fecha: new Date().toISOString(),
    configuracion: {
      usuarios_virtuales: 100,
      duracion: '5m (stages)',
      escenario: 'LogiFresh S.A. - Prueba de Carga',
    },
    metricas_http: {
      total_requests: data.metrics.http_reqs.values.count,
      requests_fallidos: data.metrics.http_req_failed.values.passes + data.metrics.http_req_failed.values.fails,
      tasa_fallos: data.metrics.http_req_failed.values.rate,
      duracion_promedio: data.metrics.http_req_duration.values.avg.toFixed(2) + ' ms',
      duracion_maxima: data.metrics.http_req_duration.values.max.toFixed(2) + ' ms',
      duracion_p90: data.metrics.http_req_duration.values['p(90)'].toFixed(2) + ' ms',
      duracion_p95: data.metrics.http_req_duration.values['p(95)'].toFixed(2) + ' ms',
      duracion_p99: data.metrics.http_req_duration.values['p(99)'].toFixed(2) + ' ms',
      throughput: (data.metrics.http_reqs.values.rate).toFixed(2) + ' req/s',
    },
    metricas_pedidos: {
      pedidos_exitosos: data.metrics.pedidos_exitosos ? data.metrics.pedidos_exitosos.values.count : 0,
      pedidos_fallidos: data.metrics.pedidos_fallidos ? data.metrics.pedidos_fallidos.values.count : 0,
    },
    metricas_tiempo_pedido: data.metrics.tiempo_creacion_pedido ? {
      promedio: data.metrics.tiempo_creacion_pedido.values.avg.toFixed(2) + ' ms',
      maximo: data.metrics.tiempo_creacion_pedido.values.max.toFixed(2) + ' ms',
      p95: data.metrics.tiempo_creacion_pedido.values['p(95)'].toFixed(2) + ' ms',
    } : {},
    interpretacion: {
      tiempo_promedio: data.metrics.http_req_duration.values.avg < 3000 ?
        'ACEPTABLE (< 3s)' : 'ALTO (> 3s) - Se requiere optimizacion',
      tasa_errores: data.metrics.http_req_failed.values.rate < 0.05 ?
        'ACEPTABLE (< 5%)' : 'ALTA (> 5%) - Se requiere investigar fallos',
      throughput: data.metrics.http_reqs.values.rate < 10 ?
        'BAJO - Capacidad limitada' : 'MODERADO - Sistema funcional bajo carga',
    }
  };

  return {
    'stdout': JSON.stringify(resumen, null, 2),
    'tests/rendimiento/resultados_k6.json': JSON.stringify(resumen, null, 2),
    'tests/rendimiento/resultados_k6_detallado.json': JSON.stringify(data, null, 2),
  };
}
