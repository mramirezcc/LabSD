import psycopg2
import psycopg2.extras
from datetime import datetime
import uuid
import time
import logging
from typing import Dict, Tuple, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TwoPhaseCommit:
    """
    Implementación del protocolo Two-Phase Commit (2PC)
    para transacciones distribuidas en el Sistema Nacional de Bancos Cooperativos

    Arquitectura:
    - Coordinador: Esta clase (orquesta el protocolo)
    - Participantes: Nodos PostgreSQL (Arequipa, Cusco, Trujillo)
    - Log persistente: Base de datos de logs para recuperación
    """

    def __init__(self, logs_config: Dict):
        """
        Inicializa el coordinador 2PC

        Args:
            logs_config: Configuración de conexión a DB de logs
        """
        self.logs_config = logs_config
        self._init_logs_table()

    def _init_logs_table(self):
        """Asegura que las tablas de logs existan"""
        try:
            conn = psycopg2.connect(**self.logs_config)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacciones_2pc (
                    id SERIAL PRIMARY KEY,
                    transaccion_id VARCHAR(50) UNIQUE NOT NULL,
                    estado VARCHAR(20),
                    origen_nodo VARCHAR(50),
                    destino_nodo VARCHAR(50),
                    cuenta_origen VARCHAR(20),
                    cuenta_destino VARCHAR(20),
                    monto DECIMAL(15,2),
                    fase_actual VARCHAR(20),
                    timestamp_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    timestamp_fin TIMESTAMP,
                    error_mensaje TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS participantes_votos (
                    id SERIAL PRIMARY KEY,
                    transaccion_id VARCHAR(50),
                    participante_nodo VARCHAR(50),
                    voto VARCHAR(10),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error inicializando tablas de logs: {e}")

    def _registrar_transaccion(self, transaccion_id: str, origen_nodo: str,
                               destino_nodo: str, cuenta_origen: str,
                               cuenta_destino: str, monto: float):
        """Registra la transacción en la base de logs"""
        conn = psycopg2.connect(**self.logs_config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transacciones_2pc
            (transaccion_id, estado, origen_nodo, destino_nodo,
             cuenta_origen, cuenta_destino, monto, fase_actual)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (transaccion_id, 'INIT', origen_nodo, destino_nodo,
              cuenta_origen, cuenta_destino, monto, 'START'))
        cursor.close()
        conn.close()

    def _actualizar_estado(self, transaccion_id: str, estado: str, fase: str, error: str = None):
        """Actualiza el estado de la transacción en logs"""
        conn = psycopg2.connect(**self.logs_config)
        conn.autocommit = True
        cursor = conn.cursor()
        if error:
            cursor.execute("""
                UPDATE transacciones_2pc
                SET estado = %s, fase_actual = %s, error_mensaje = %s, timestamp_fin = %s
                WHERE transaccion_id = %s
            """, (estado, fase, error, datetime.now(), transaccion_id))
        else:
            cursor.execute("""
                UPDATE transacciones_2pc
                SET estado = %s, fase_actual = %s, timestamp_fin = %s
                WHERE transaccion_id = %s
            """, (estado, fase, datetime.now(), transaccion_id))
        cursor.close()
        conn.close()

    def _registrar_voto(self, transaccion_id: str, participante: str, voto: str):
        """Registra el voto de un participante"""
        conn = psycopg2.connect(**self.logs_config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO participantes_votos (transaccion_id, participante_nodo, voto)
            VALUES (%s, %s, %s)
        """, (transaccion_id, participante, voto))
        cursor.close()
        conn.close()

    def _preparar_participante(self, conn, transaccion_id: str,
                               cuenta: str, monto: float, es_origen: bool,
                               nodo_nombre: str) -> Tuple[bool, str]:
        """
        Fase PREPARE para un participante individual

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        cursor = conn.cursor()
        try:
            if es_origen:
                # Verificar saldo suficiente y bloquear fondos (SELECT FOR UPDATE)
                cursor.execute("""
                    SELECT saldo, titular FROM cuentas
                    WHERE numero_cuenta = %s FOR UPDATE
                """, (cuenta,))
                resultado = cursor.fetchone()

                if not resultado:
                    return False, f"Cuenta origen {cuenta} no encontrada"

                saldo_actual = resultado[0]
                titular = resultado[1]

                if saldo_actual < monto:
                    logger.warning(f"Saldo insuficiente en cuenta {cuenta} en {nodo_nombre}. "
                                   f"Disponible: {saldo_actual}, Necesario: {monto}")
                    return False, f"Saldo insuficiente. Disponible: {saldo_actual}"

                # Crear registro de retención (soft lock)
                cursor.execute("""
                    INSERT INTO transacciones_log (transaccion_id, tipo, monto, estado)
                    VALUES (%s, 'RETENCION_ORIGEN', %s, 'PREPARADO')
                """, (transaccion_id, monto))

                logger.info(f"Participante {nodo_nombre} (origen) preparado exitosamente. "
                            f"Saldo retenido: {monto}")
            else:
                # Preparar para recibir fondos
                cursor.execute("""
                    SELECT titular FROM cuentas
                    WHERE numero_cuenta = %s FOR UPDATE
                """, (cuenta,))

                if not cursor.fetchone():
                    return False, f"Cuenta destino {cuenta} no encontrada"

                cursor.execute("""
                    INSERT INTO transacciones_log (transaccion_id, tipo, monto, estado)
                    VALUES (%s, 'RETENCION_DESTINO', %s, 'PREPARADO')
                """, (transaccion_id, monto))

                logger.info(f"Participante {nodo_nombre} (destino) preparado exitosamente")

            conn.commit()
            return True, "OK"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error preparando participante {nodo_nombre}: {e}")
            return False, str(e)

    def _commit_participante(self, conn, transaccion_id: str,
                             cuenta_origen: str, cuenta_destino: str,
                             monto: float, es_origen: bool,
                             nodo_nombre: str) -> Tuple[bool, str]:
        """
        Fase COMMIT para un participante individual

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        cursor = conn.cursor()
        try:
            if es_origen:
                # Descontar saldo definitivamente
                cursor.execute("""
                    UPDATE cuentas
                    SET saldo = saldo - %s, updated_at = %s
                    WHERE numero_cuenta = %s
                """, (monto, datetime.now(), cuenta_origen))

                cursor.execute("""
                    UPDATE transacciones_log
                    SET estado = 'COMMITTED'
                    WHERE transaccion_id = %s AND tipo = 'RETENCION_ORIGEN'
                """, (transaccion_id,))

                logger.info(f"Commit exitoso en {nodo_nombre}: débito de {monto}")
            else:
                # Acreditar saldo definitivamente
                cursor.execute("""
                    UPDATE cuentas
                    SET saldo = saldo + %s, updated_at = %s
                    WHERE numero_cuenta = %s
                """, (monto, datetime.now(), cuenta_destino))

                cursor.execute("""
                    UPDATE transacciones_log
                    SET estado = 'COMMITTED'
                    WHERE transaccion_id = %s AND tipo = 'RETENCION_DESTINO'
                """, (transaccion_id,))

                logger.info(f"Commit exitoso en {nodo_nombre}: crédito de {monto}")

            conn.commit()
            return True, "OK"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error en commit para {nodo_nombre}: {e}")
            return False, str(e)

    def _abort_participante(self, conn, transaccion_id: str, nodo_nombre: str) -> Tuple[bool, str]:
        """
        Fase ABORT para un participante individual (rollback)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE transacciones_log
                SET estado = 'ABORTED'
                WHERE transaccion_id = %s AND estado = 'PREPARADO'
            """, (transaccion_id,))
            conn.commit()
            logger.info(f"Abort ejecutado para transacción {transaccion_id} en {nodo_nombre}")
            return True, "OK"
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en abort para {nodo_nombre}: {e}")
            return False, str(e)

    def execute_transaction(self, origen_config: Dict, destino_config: Dict,
                           cuenta_origen: str, cuenta_destino: str,
                           monto: float, timeout_seconds: int = 10) -> Tuple[bool, str]:
        """
        Ejecuta una transacción distribuida completa usando 2PC

        Args:
            origen_config: Configuración DB origen (Arequipa)
            destino_config: Configuración DB destino (Cusco)
            cuenta_origen: Número de cuenta origen
            cuenta_destino: Número de cuenta destino
            monto: Monto a transferir
            timeout_seconds: Timeout para esperar respuestas

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        transaccion_id = str(uuid.uuid4())
        logger.info(f"=== INICIANDO TRANSACCIÓN 2PC: {transaccion_id} ===")
        logger.info(f"Transferencia: {cuenta_origen} (Arequipa) → {cuenta_destino} (Cusco)")
        logger.info(f"Monto: S/ {monto}")

        # Registrar inicio de transacción
        self._registrar_transaccion(transaccion_id, 'Arequipa', 'Cusco',
                                    cuenta_origen, cuenta_destino, monto)

        # Conectar a participantes
        origen_conn = None
        destino_conn = None

        try:
            origen_conn = psycopg2.connect(**origen_config)
            destino_conn = psycopg2.connect(**destino_config)

            # ========== FASE 1: PREPARE ==========
            logger.info("")
            logger.info("╔══════════════════════════════════════════════════════════════╗")
            logger.info("║                    FASE 1: PREPARE                           ║")
            logger.info("╚══════════════════════════════════════════════════════════════╝")
            self._actualizar_estado(transaccion_id, 'PREPARING', 'PREPARE')

            # Preparar nodo origen (Arequipa)
            logger.info("→ Enviando PREPARE a nodo Arequipa...")
            origen_preparado, origen_msg = self._preparar_participante(
                origen_conn, transaccion_id, cuenta_origen, monto, True, 'Arequipa'
            )
            self._registrar_voto(transaccion_id, 'Arequipa', 'YES' if origen_preparado else 'NO')
            logger.info(f"  Respuesta Arequipa: {'YES' if origen_preparado else 'NO'} - {origen_msg}")

            # Preparar nodo destino (Cusco) - con timeout
            logger.info("→ Enviando PREPARE a nodo Cusco...")
            destino_preparado = False
            destino_msg = "Timeout"

            import threading

            def prepare_destino():
                nonlocal destino_preparado, destino_msg
                try:
                    resultado, msg = self._preparar_participante(
                        destino_conn, transaccion_id, cuenta_destino, monto, False, 'Cusco'
                    )
                    destino_preparado = resultado
                    destino_msg = msg
                except Exception as e:
                    destino_preparado = False
                    destino_msg = str(e)

            thread = threading.Thread(target=prepare_destino)
            thread.start()
            thread.join(timeout=timeout_seconds)

            if thread.is_alive():
                logger.warning(f"  ⚠️ TIMEOUT: Cusco no respondió en {timeout_seconds}s")
                destino_preparado = False
                destino_msg = f"Timeout después de {timeout_seconds} segundos"
            else:
                logger.info(f"  Respuesta Cusco: {'YES' if destino_preparado else 'NO'} - {destino_msg}")

            self._registrar_voto(transaccion_id, 'Cusco', 'YES' if destino_preparado else 'NO')

            # Evaluar votos (solo Arequipa y Cusco, Trujillo es testigo pasivo)
            all_prepared = origen_preparado and destino_preparado

            # ========== FASE 2: COMMIT / ABORT ==========
            logger.info("")
            logger.info("╔══════════════════════════════════════════════════════════════╗")

            if all_prepared:
                logger.info("║                    FASE 2: COMMIT                          ║")
                logger.info("╚══════════════════════════════════════════════════════════════╝")
                self._actualizar_estado(transaccion_id, 'COMMITTING', 'COMMIT')

                # Commit en origen
                logger.info("→ Enviando COMMIT a nodo Arequipa...")
                commit_origen, msg_origen = self._commit_participante(
                    origen_conn, transaccion_id, cuenta_origen, cuenta_destino, monto, True, 'Arequipa'
                )

                # Commit en destino
                logger.info("→ Enviando COMMIT a nodo Cusco...")
                commit_destino, msg_destino = self._commit_participante(
                    destino_conn, transaccion_id, cuenta_origen, cuenta_destino, monto, False, 'Cusco'
                )

                if commit_origen and commit_destino:
                    self._actualizar_estado(transaccion_id, 'COMMITTED', 'DONE')
                    logger.info("")
                    logger.info("✅ ✅ ✅ TRANSACCIÓN EXITOSA ✅ ✅ ✅")
                    logger.info(f"Transferencia de S/ {monto} completada")
                    logger.info(f"ID Transacción: {transaccion_id}")
                    return True, f"Transferencia de S/ {monto} completada exitosamente"
                else:
                    logger.error("❌ Fallo en commit, ejecutando rollback parcial")
                    self._abort_participante(origen_conn, transaccion_id, 'Arequipa')
                    self._abort_participante(destino_conn, transaccion_id, 'Cusco')
                    self._actualizar_estado(transaccion_id, 'ABORTED', 'FAILED',
                                           "Fallo durante commit")
                    return False, "Error durante confirmación de transacción"
            else:
                logger.info("║                    FASE 2: ABORT (ROLLBACK)                ║")
                logger.info("╚══════════════════════════════════════════════════════════════╝")
                self._actualizar_estado(transaccion_id, 'ABORTING', 'ABORT')

                if origen_preparado:
                    logger.info("→ Enviando ABORT a nodo Arequipa...")
                    self._abort_participante(origen_conn, transaccion_id, 'Arequipa')
                if destino_preparado:
                    logger.info("→ Enviando ABORT a nodo Cusco...")
                    self._abort_participante(destino_conn, transaccion_id, 'Cusco')

                self._actualizar_estado(transaccion_id, 'ABORTED', 'DONE',
                                       f"Voto negativo: Origen={origen_preparado}, Destino={destino_preparado}")
                logger.info("")
                logger.info("❌ ❌ ❌ TRANSACCIÓN ABORTADA ❌ ❌ ❌")
                logger.info(f"Motivo: {origen_msg if not origen_preparado else destino_msg}")
                return False, f"Transferencia abortada: {origen_msg if not origen_preparado else destino_msg}"

        except Exception as e:
            logger.error(f"Error durante transacción 2PC: {e}")
            self._actualizar_estado(transaccion_id, 'ABORTED', 'ERROR', str(e))
            return False, f"Error en transacción: {str(e)}"

        finally:
            if origen_conn:
                origen_conn.close()
            if destino_conn:
                destino_conn.close()

    def get_transaction_status(self, transaccion_id: str) -> Optional[Dict]:
        """Obtiene el estado de una transacción desde los logs"""
        try:
            conn = psycopg2.connect(**self.logs_config)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT * FROM transacciones_2pc WHERE transaccion_id = %s
            """, (transaccion_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return None

    def get_pending_transactions(self) -> List[Dict]:
        """Obtiene transacciones pendientes de recuperación"""
        try:
            conn = psycopg2.connect(**self.logs_config)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT * FROM transacciones_2pc
                WHERE estado IN ('PREPARING', 'COMMITTING')
                AND timestamp_fin IS NULL
            """)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error obteniendo transacciones pendientes: {e}")
            return []