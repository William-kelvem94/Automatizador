# -*- coding: utf-8 -*-

"""
ENTERPRISE CONNECTION POOL - PostgreSQL
Sistema avançado de pool de conexões com monitoramento e failover
"""

import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from contextlib import asynccontextmanager
import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor

from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector


class EnterpriseConnectionPool:
    """Pool de conexões PostgreSQL enterprise-grade"""

    def __init__(self,
                 dsn: str,
                 min_connections: int = 5,
                 max_connections: int = 20,
                 connection_timeout: float = 30.0,
                 command_timeout: float = 60.0,
                 health_check_interval: float = 60.0,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        Inicializar pool de conexões enterprise

        Args:
            dsn: String de conexão PostgreSQL
            min_connections: Número mínimo de conexões no pool
            max_connections: Número máximo de conexões no pool
            connection_timeout: Timeout para estabelecer conexão
            command_timeout: Timeout para comandos SQL
            health_check_interval: Intervalo entre health checks
            max_retries: Máximo de tentativas de reconexão
            retry_delay: Delay entre tentativas
        """
        self.logger = get_logger(__name__)
        self.dsn = dsn
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.command_timeout = command_timeout
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Pool subjacente
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None

        # Estatísticas e monitoramento
        self.stats = {
            'connections_created': 0,
            'connections_destroyed': 0,
            'connections_active': 0,
            'connections_idle': 0,
            'queries_executed': 0,
            'queries_failed': 0,
            'connection_errors': 0,
            'health_check_failures': 0,
            'last_health_check': None,
            'pool_status': 'initializing'
        }

        # Controle de threading
        self._lock = threading.RLock()
        self._health_check_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Callbacks
        self._connection_created_callbacks: List[Callable] = []
        self._connection_destroyed_callbacks: List[Callable] = []
        self._health_check_callbacks: List[Callable] = []

        self.logger.info(f"EnterpriseConnectionPool inicializado - Pool size: {min_connections}-{max_connections}")

    def initialize(self) -> bool:
        """Inicializar pool de conexões"""
        try:
            self.logger.info("🏊 Inicializando pool de conexões PostgreSQL...")

            # Criar pool
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                dsn=self.dsn,
                connection_factory=self._create_connection
            )

            # Verificar se pool foi criado corretamente
            if not self._pool:
                raise Exception("Falha ao criar pool de conexões")

            # Executar health check inicial
            if not self._perform_health_check():
                raise Exception("Health check inicial falhou")

            # Iniciar thread de health check
            self._start_health_check_thread()

            self.stats['pool_status'] = 'healthy'
            self.logger.info("✅ Pool de conexões inicializado com sucesso")
            return True

        except Exception as e:
            self.stats['pool_status'] = 'failed'
            self.logger.error(f"❌ Falha na inicialização do pool: {e}")
            return False

    def _create_connection(self, dsn: str) -> PgConnection:
        """Criar conexão com configurações enterprise"""
        conn = psycopg2.connect(dsn)

        # Configurações de performance e segurança
        with conn.cursor() as cur:
            # Configurações de sessão
            cur.execute("SET SESSION work_mem = '64MB';")  # Memória de trabalho
            cur.execute("SET SESSION maintenance_work_mem = '256MB';")  # Memória de manutenção
            cur.execute("SET SESSION temp_buffers = '32MB';")  # Buffers temporários

            # Configurações de timeout
            cur.execute(f"SET SESSION statement_timeout = '{int(self.command_timeout * 1000)}';")

            # Configurações de segurança
            cur.execute("SET SESSION ssl_min_protocol_version = 'TLSv1.2';")

            # Configurações de logging (se disponível)
            try:
                cur.execute("SET SESSION log_statement = 'ddl';")  # Log DDL statements
                cur.execute("SET SESSION log_min_duration_statement = 1000;")  # Log queries > 1s
            except:
                pass  # Extensão pode não estar disponível

        # Incrementar contador
        self.stats['connections_created'] += 1

        # Executar callbacks
        for callback in self._connection_created_callbacks:
            try:
                callback(conn)
            except Exception as e:
                self.logger.warning(f"Erro em callback de criação de conexão: {e}")

        return conn

    def _destroy_connection(self, conn: PgConnection):
        """Destruir conexão"""
        try:
            if conn and not conn.closed:
                conn.close()

            self.stats['connections_destroyed'] += 1

            # Executar callbacks
            for callback in self._connection_destroyed_callbacks:
                try:
                    callback(conn)
                except Exception as e:
                    self.logger.warning(f"Erro em callback de destruição de conexão: {e}")

        except Exception as e:
            self.logger.error(f"Erro ao destruir conexão: {e}")

    def _start_health_check_thread(self):
        """Iniciar thread de health check"""
        if self._health_check_thread and self._health_check_thread.is_alive():
            return

        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="ConnectionPool-HealthCheck"
        )
        self._health_check_thread.start()

        self.logger.debug("Thread de health check iniciada")

    def _health_check_loop(self):
        """Loop de health check"""
        while not self._shutdown_event.is_set():
            try:
                # Executar health check
                is_healthy = self._perform_health_check()

                # Executar callbacks
                for callback in self._health_check_callbacks:
                    try:
                        callback(is_healthy)
                    except Exception as e:
                        self.logger.warning(f"Erro em callback de health check: {e}")

                # Atualizar métricas
                if is_healthy:
                    metrics_collector.set_gauge_value('automator_db_pool_healthy', 1)
                else:
                    metrics_collector.set_gauge_value('automator_db_pool_healthy', 0)
                    self.stats['health_check_failures'] += 1

            except Exception as e:
                self.logger.error(f"Erro no health check loop: {e}")

            # Aguardar próximo check
            self._shutdown_event.wait(self.health_check_interval)

    def _perform_health_check(self) -> bool:
        """Executar health check do pool"""
        try:
            conn = self.get_connection()
            if not conn:
                return False

            with conn.cursor() as cur:
                # Query simples de health check
                cur.execute("SELECT 1 as health_check, pg_is_in_recovery() as is_replica;")
                result = cur.fetchone()

                if result and result[0] == 1:
                    is_replica = result[1]
                    self.logger.debug(f"Health check OK - Replica: {is_replica}")

                    # Atualizar estatísticas
                    self.stats['last_health_check'] = time.time()

                    # Métricas do pool
                    pool_stats = self.get_pool_stats()
                    metrics_collector.set_gauge_value('automator_db_connections_active',
                                                     pool_stats.get('active', 0))
                    metrics_collector.set_gauge_value('automator_db_connections_idle',
                                                     pool_stats.get('idle', 0))

                    return True
                else:
                    self.logger.warning("Health check query falhou")
                    return False

        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            self.stats['connection_errors'] += 1
            return False
        finally:
            if 'conn' in locals() and conn:
                self.return_connection(conn)

    @asynccontextmanager
    async def get_connection_async(self):
        """Obter conexão de forma assíncrona (context manager)"""
        conn = None
        try:
            conn = await asyncio.get_event_loop().run_in_executor(None, self.get_connection)
            yield conn
        finally:
            if conn:
                await asyncio.get_event_loop().run_in_executor(None, self.return_connection, conn)

    def get_connection(self) -> Optional[PgConnection]:
        """Obter conexão do pool"""
        if not self._pool:
            self.logger.error("Pool não inicializado")
            return None

        try:
            with self._lock:
                conn = self._pool.getconn()

                if conn:
                    # Verificar se conexão ainda é válida
                    if self._is_connection_valid(conn):
                        self.stats['connections_active'] += 1
                        return conn
                    else:
                        # Conexão inválida, tentar fechar e obter nova
                        self.logger.warning("Conexão inválida detectada, tentando nova...")
                        self._pool.putconn(conn, close=True)

                        # Tentar novamente
                        conn = self._pool.getconn()
                        if conn and self._is_connection_valid(conn):
                            self.stats['connections_active'] += 1
                            return conn

                self.logger.error("Falha ao obter conexão válida do pool")
                return None

        except psycopg2.pool.PoolError as e:
            self.logger.error(f"Pool error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter conexão: {e}")
            return None

    def return_connection(self, conn: PgConnection):
        """Retornar conexão ao pool"""
        if not self._pool or not conn:
            return

        try:
            with self._lock:
                self._pool.putconn(conn)
                self.stats['connections_active'] -= 1

        except Exception as e:
            self.logger.error(f"Erro ao retornar conexão: {e}")
            # Tentar fechar conexão problemática
            try:
                if not conn.closed:
                    conn.close()
            except:
                pass

    def _is_connection_valid(self, conn: PgConnection) -> bool:
        """Verificar se conexão é válida"""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                return result and result[0] == 1
        except Exception:
            return False

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Executar query com retry automático e monitoramento

        Args:
            query: Query SQL
            params: Parâmetros da query
            fetch: Se deve buscar resultados

        Returns:
            Resultados da query ou None se erro
        """
        start_time = time.time()

        for attempt in range(self.max_retries):
            conn = self.get_connection()
            if not conn:
                self.logger.error("Não foi possível obter conexão")
                return None

            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(query, params or ())

                    # Registrar métrica de performance
                    execution_time = time.time() - start_time
                    metrics_collector.observe_histogram(
                        'automator_db_query_duration_seconds',
                        execution_time,
                        {'query_type': self._classify_query(query)}
                    )

                    self.stats['queries_executed'] += 1

                    if fetch and cur.description:
                        results = cur.fetchall()
                        return [dict(row) for row in results]
                    else:
                        return []

            except psycopg2.OperationalError as e:
                self.logger.warning(f"Erro operacional na tentativa {attempt + 1}: {e}")
                self.stats['connection_errors'] += 1

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    self.logger.error(f"Query falhou após {self.max_retries} tentativas")
                    return None

            except Exception as e:
                self.stats['queries_failed'] += 1
                self.logger.error(f"Erro na execução da query: {e}")
                return None

            finally:
                self.return_connection(conn)

        return None

    def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """
        Executar transação com múltiplas queries

        Args:
            queries: Lista de dicts com 'query' e 'params'

        Returns:
            True se sucesso, False se erro
        """
        conn = self.get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # Iniciar transação
                conn.autocommit = False

                for query_info in queries:
                    query = query_info['query']
                    params = query_info.get('params', ())
                    cur.execute(query, params)

                # Commit
                conn.commit()
                self.logger.debug(f"Transação executada com sucesso: {len(queries)} queries")

                return True

        except Exception as e:
            # Rollback em caso de erro
            try:
                conn.rollback()
            except:
                pass

            self.logger.error(f"Erro na transação: {e}")
            return False

        finally:
            conn.autocommit = True
            self.return_connection(conn)

    def _classify_query(self, query: str) -> str:
        """Classificar tipo de query para métricas"""
        query_upper = query.strip().upper()

        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif 'CREATE' in query_upper:
            return 'DDL'
        elif 'ALTER' in query_upper or 'DROP' in query_upper:
            return 'DDL'
        else:
            return 'OTHER'

    def get_pool_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do pool"""
        if not self._pool:
            return {'status': 'not_initialized'}

        try:
            with self._lock:
                stats = dict(self.stats)
                stats.update({
                    'min_connections': self.min_connections,
                    'max_connections': self.max_connections,
                    'current_pool_size': self._pool._used + self._pool._rused,
                    'idle_connections': len(self._pool._pool),
                    'used_connections': self._pool._used,
                    'reserved_connections': self._pool._rused
                })
                return stats

        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas do pool: {e}")
            return {'error': str(e)}

    def add_connection_created_callback(self, callback: Callable):
        """Adicionar callback para criação de conexões"""
        self._connection_created_callbacks.append(callback)

    def add_connection_destroyed_callback(self, callback: Callable):
        """Adicionar callback para destruição de conexões"""
        self._connection_destroyed_callbacks.append(callback)

    def add_health_check_callback(self, callback: Callable):
        """Adicionar callback para health checks"""
        self._health_check_callbacks.append(callback)

    def shutdown(self):
        """Desligar pool de conexões"""
        self.logger.info("Desligando pool de conexões...")

        # Sinalizar shutdown para thread
        self._shutdown_event.set()

        # Aguardar thread terminar
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5.0)

        # Fechar pool
        if self._pool:
            try:
                self._pool.closeall()
                self.logger.info("Pool de conexões fechado")
            except Exception as e:
                self.logger.error(f"Erro ao fechar pool: {e}")

        self.stats['pool_status'] = 'shutdown'
        self.logger.info("✅ Pool de conexões desligado")

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do pool"""
        try:
            stats = self.get_pool_stats()

            # Verificar conectividade
            is_healthy = self._perform_health_check()

            result = {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'pool_stats': stats,
                'configuration': {
                    'min_connections': self.min_connections,
                    'max_connections': self.max_connections,
                    'connection_timeout': self.connection_timeout,
                    'command_timeout': self.command_timeout
                }
            }

            # Verificar se pool está sobrecarregado
            if stats.get('used_connections', 0) > self.max_connections * 0.9:
                result['warnings'] = ['Pool near capacity limit']

            return result

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Factory function para criar pool
def create_enterprise_pool(database_url: str, **kwargs) -> EnterpriseConnectionPool:
    """Factory para criar pool enterprise"""
    pool = EnterpriseConnectionPool(database_url, **kwargs)

    if pool.initialize():
        return pool
    else:
        raise Exception("Falha ao inicializar pool de conexões")


# Context manager para uso síncrono
@asynccontextmanager
async def get_db_connection(pool: EnterpriseConnectionPool):
    """Context manager para obter conexão do pool"""
    conn = None
    try:
        conn = await asyncio.get_event_loop().run_in_executor(None, pool.get_connection)
        yield conn
    finally:
        if conn:
            await asyncio.get_event_loop().run_in_executor(None, pool.return_connection, conn)
