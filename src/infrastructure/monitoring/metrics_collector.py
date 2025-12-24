# -*- coding: utf-8 -*-

"""
METRICS COLLECTOR - Prometheus Metrics Enterprise
Coleta abrangente de métricas técnicas e de negócio
"""

import time
import psutil
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from ...shared.utils.logger import get_logger


class MetricsCollector:
    """Coletor de métricas Prometheus enterprise"""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.logger = get_logger(__name__)
        self.registry = registry or CollectorRegistry()

        # Sistema operacional e hardware
        self._setup_system_metrics()

        # Aplicação e negócio
        self._setup_application_metrics()

        # Segurança
        self._setup_security_metrics()

        # Performance
        self._setup_performance_metrics()

        # Cache de métricas
        self._metrics_cache = {}
        self._last_collection = datetime.now()

        self.logger.info("MetricsCollector inicializado com sucesso")

    def _setup_system_metrics(self):
        """Métricas do sistema operacional"""
        # CPU
        self.cpu_usage = Gauge(
            'automator_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )

        self.cpu_count = Gauge(
            'automator_cpu_count',
            'Number of CPU cores',
            registry=self.registry
        )

        # Memória
        self.memory_total = Gauge(
            'automator_memory_total_bytes',
            'Total system memory in bytes',
            registry=self.registry
        )

        self.memory_used = Gauge(
            'automator_memory_used_bytes',
            'Used system memory in bytes',
            registry=self.registry
        )

        self.memory_percent = Gauge(
            'automator_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )

        # Disco
        self.disk_total = Gauge(
            'automator_disk_total_bytes',
            'Total disk space in bytes',
            registry=self.registry
        )

        self.disk_used = Gauge(
            'automator_disk_used_bytes',
            'Used disk space in bytes',
            registry=self.registry
        )

        self.disk_percent = Gauge(
            'automator_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )

        # Rede
        self.network_connections = Gauge(
            'automator_network_connections_total',
            'Total network connections',
            registry=self.registry
        )

        self.network_bytes_sent = Counter(
            'automator_network_bytes_sent_total',
            'Total bytes sent over network',
            registry=self.registry
        )

        self.network_bytes_recv = Counter(
            'automator_network_bytes_recv_total',
            'Total bytes received over network',
            registry=self.registry
        )

    def _setup_application_metrics(self):
        """Métricas da aplicação"""
        # Tarefas
        self.tasks_created_total = Counter(
            'automator_tasks_created_total',
            'Total number of tasks created',
            ['task_type'],
            registry=self.registry
        )

        self.tasks_executed_total = Counter(
            'automator_tasks_executed_total',
            'Total number of tasks executed',
            ['task_type', 'result'],
            registry=self.registry
        )

        self.tasks_active = Gauge(
            'automator_tasks_active',
            'Number of currently active tasks',
            registry=self.registry
        )

        self.tasks_execution_time = Histogram(
            'automator_tasks_execution_duration_seconds',
            'Task execution duration in seconds',
            ['task_type'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 300.0),
            registry=self.registry
        )

        # Workflows
        self.workflows_created_total = Counter(
            'automator_workflows_created_total',
            'Total number of workflows created',
            registry=self.registry
        )

        self.workflows_executed_total = Counter(
            'automator_workflows_executed_total',
            'Total number of workflows executed',
            ['result'],
            registry=self.registry
        )

        # APIs
        self.api_requests_total = Counter(
            'automator_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )

        self.api_request_duration = Histogram(
            'automator_api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0),
            registry=self.registry
        )

        # Usuários e sessões
        self.active_users = Gauge(
            'automator_active_users',
            'Number of active users',
            registry=self.registry
        )

        self.user_sessions_total = Counter(
            'automator_user_sessions_total',
            'Total user sessions',
            ['result'],
            registry=self.registry
        )

        # Cache
        self.cache_hits_total = Counter(
            'automator_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_misses_total = Counter(
            'automator_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_size = Gauge(
            'automator_cache_size_bytes',
            'Cache size in bytes',
            ['cache_type'],
            registry=self.registry
        )

    def _setup_security_metrics(self):
        """Métricas de segurança"""
        self.auth_attempts_total = Counter(
            'automator_auth_attempts_total',
            'Total authentication attempts',
            ['result'],
            registry=self.registry
        )

        self.security_incidents_total = Counter(
            'automator_security_incidents_total',
            'Total security incidents',
            ['incident_type', 'severity'],
            registry=self.registry
        )

        self.audit_events_total = Counter(
            'automator_audit_events_total',
            'Total audit events',
            ['event_type', 'severity'],
            registry=self.registry
        )

        self.vulnerabilities_found = Gauge(
            'automator_vulnerabilities_found',
            'Number of vulnerabilities found',
            ['severity'],
            registry=self.registry
        )

        self.encryption_operations_total = Counter(
            'automator_encryption_operations_total',
            'Total encryption/decryption operations',
            ['operation_type', 'result'],
            registry=self.registry
        )

    def _setup_performance_metrics(self):
        """Métricas de performance"""
        self.response_time = Summary(
            'automator_response_time_seconds',
            'Response time summary',
            ['operation_type'],
            registry=self.registry
        )

        self.error_rate = Counter(
            'automator_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        self.uptime_seconds = Gauge(
            'automator_uptime_seconds',
            'Application uptime in seconds',
            registry=self.registry
        )

        self.heap_memory_used = Gauge(
            'automator_heap_memory_used_bytes',
            'Heap memory used in bytes',
            registry=self.registry
        )

        self.gc_collections_total = Counter(
            'automator_gc_collections_total',
            'Total garbage collection runs',
            ['generation'],
            registry=self.registry
        )

        # Database
        self.db_connections_active = Gauge(
            'automator_db_connections_active',
            'Number of active database connections',
            registry=self.registry
        )

        self.db_query_duration = Histogram(
            'automator_db_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            buckets=(0.001, 0.01, 0.1, 1.0, 5.0),
            registry=self.registry
        )

        # External services
        self.external_service_calls_total = Counter(
            'automator_external_service_calls_total',
            'Total external service calls',
            ['service_name', 'result'],
            registry=self.registry
        )

        self.external_service_duration = Histogram(
            'automator_external_service_duration_seconds',
            'External service call duration',
            ['service_name'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
            registry=self.registry
        )

    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # CPU
            self.cpu_usage.set(psutil.cpu_percent(interval=1))
            self.cpu_count.set(psutil.cpu_count())

            # Memória
            memory = psutil.virtual_memory()
            self.memory_total.set(memory.total)
            self.memory_used.set(memory.used)
            self.memory_percent.set(memory.percent)

            # Disco
            disk = psutil.disk_usage('/')
            self.disk_total.set(disk.total)
            self.disk_used.set(disk.used)
            self.disk_percent.set(disk.percent)

            # Rede
            net_connections = len(psutil.net_connections())
            self.network_connections.set(net_connections)

            # Bytes de rede (desde o último restart)
            net_io = psutil.net_io_counters()
            self.network_bytes_sent._value.set(net_io.bytes_sent)
            self.network_bytes_recv._value.set(net_io.bytes_recv)

        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")

    def collect_application_metrics(self):
        """Coleta métricas da aplicação"""
        try:
            # Uptime (simulado - em produção seria calculado desde startup)
            import time as time_module
            self.uptime_seconds.set(time_module.time() - psutil.boot_time())

            # Memória heap (aproximado)
            process = psutil.Process()
            memory_info = process.memory_info()
            self.heap_memory_used.set(memory_info.rss)

        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas da aplicação: {e}")

    def collect_all_metrics(self):
        """Coleta todas as métricas"""
        self.collect_system_metrics()
        self.collect_application_metrics()

        self._last_collection = datetime.now()

    def get_metrics_text(self) -> str:
        """Retorna métricas no formato Prometheus"""
        return generate_latest(self.registry).decode('utf-8')

    def get_metrics_json(self) -> Dict[str, Any]:
        """Retorna métricas em formato JSON"""
        # Parse do formato Prometheus para JSON
        metrics_text = self.get_metrics_text()
        return self._parse_prometheus_metrics(metrics_text)

    def _parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """Parse métricas Prometheus para JSON"""
        result = {}
        current_metric = None

        for line in metrics_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.endswith('}'):
                # Métrica com labels
                parts = line.split('{')
                metric_name = parts[0]
                rest = parts[1].rstrip('}')

                label_part, value_part = rest.split('} ')
                labels = {}
                if label_part:
                    for label in label_part.split(','):
                        key, value = label.split('=')
                        labels[key.strip()] = value.strip('"')

                result.setdefault(metric_name, []).append({
                    'labels': labels,
                    'value': float(value_part)
                })
            else:
                # Métrica simples
                parts = line.split(' ')
                if len(parts) >= 2:
                    metric_name = parts[0]
                    value = float(parts[1])
                    result.setdefault(metric_name, []).append({
                        'labels': {},
                        'value': value
                    })

        return result

    # ===== MÉTODOS DE REGISTRO DE EVENTOS =====

    def record_task_created(self, task_type: str = 'automation'):
        """Registra criação de tarefa"""
        self.tasks_created_total.labels(task_type=task_type).inc()

    def record_task_executed(self, task_type: str, success: bool, duration: float):
        """Registra execução de tarefa"""
        result = 'success' if success else 'failure'
        self.tasks_executed_total.labels(task_type=task_type, result=result).inc()
        self.tasks_execution_time.labels(task_type=task_type).observe(duration)

        # Atualiza contador ativo (simulado)
        if success:
            self.tasks_active.dec()
        else:
            self.tasks_active.dec()

    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Registra requisição de API"""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_auth_attempt(self, success: bool):
        """Registra tentativa de autenticação"""
        result = 'success' if success else 'failure'
        self.auth_attempts_total.labels(result=result).inc()

    def record_security_incident(self, incident_type: str, severity: str):
        """Registra incidente de segurança"""
        self.security_incidents_total.labels(
            incident_type=incident_type,
            severity=severity
        ).inc()

    def record_error(self, error_type: str, component: str):
        """Registra erro"""
        self.error_rate.labels(error_type=error_type, component=component).inc()

    def record_cache_operation(self, cache_type: str, hit: bool):
        """Registra operação de cache"""
        if hit:
            self.cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_total.labels(cache_type=cache_type).inc()

    def record_external_service_call(self, service_name: str, success: bool, duration: float):
        """Registra chamada para serviço externo"""
        result = 'success' if success else 'failure'
        self.external_service_calls_total.labels(
            service_name=service_name,
            result=result
        ).inc()
        self.external_service_duration.labels(service_name=service_name).observe(duration)

    def set_gauge_value(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Define valor de um gauge customizado"""
        if labels:
            # Implementar lógica para gauges com labels se necessário
            pass
        else:
            # Para simplificar, usar um gauge existente ou criar um novo
            if hasattr(self, metric_name):
                getattr(self, metric_name).set(value)

    def increment_counter(self, metric_name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Incrementa contador customizado"""
        if labels:
            # Implementar lógica para counters com labels se necessário
            pass
        else:
            if hasattr(self, metric_name):
                getattr(self, metric_name).inc(value)

    def observe_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Observa valor em histograma customizado"""
        if labels:
            # Implementar lógica para histograms com labels se necessário
            pass
        else:
            if hasattr(self, metric_name):
                getattr(self, metric_name).observe(value)

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do coletor de métricas"""
        try:
            # Testa coleta de métricas
            self.collect_all_metrics()

            # Verifica se métricas foram coletadas
            metrics = self.get_metrics_json()
            metrics_count = len(metrics)

            return {
                'status': 'healthy',
                'metrics_collected': metrics_count,
                'last_collection': self._last_collection.isoformat(),
                'registry_size': len(list(self.registry._collector_to_names.keys()))
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Instância global do coletor
metrics_collector = MetricsCollector()
