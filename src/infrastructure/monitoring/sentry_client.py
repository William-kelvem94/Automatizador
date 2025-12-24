# -*- coding: utf-8 -*-

"""
SENTRY CLIENT - Error Tracking Enterprise
Integração com Sentry para monitoramento avançado de erros
"""

import os
import sys
from typing import Dict, Any, Optional, Callable
import traceback
import threading
import time

from ...shared.utils.logger import get_logger

# Tentativa de importar Sentry (opcional)
try:
    import sentry_sdk
    from sentry_sdk import capture_exception, capture_message, configure_scope
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.threading import ThreadingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None


class SentryErrorTracker:
    """Cliente Sentry para error tracking enterprise"""

    def __init__(self,
                 dsn: Optional[str] = None,
                 environment: str = "development",
                 release: str = "8.0.0",
                 sample_rate: float = 1.0):
        self.logger = get_logger(__name__)
        self.environment = environment
        self.release = release
        self.sample_rate = sample_rate
        self.initialized = False

        if not SENTRY_AVAILABLE:
            self.logger.warning("Sentry SDK não disponível. Instale com: pip install sentry-sdk")
            return

        if not dsn:
            dsn = os.environ.get('SENTRY_DSN')
            if not dsn:
                self.logger.warning("SENTRY_DSN não configurado. Error tracking desabilitado.")
                return

        try:
            # Configurações de integração
            integrations = [
                LoggingIntegration(
                    level="WARNING",  # Nível mínimo para logging
                    event_level="ERROR"  # Nível para eventos
                ),
                ThreadingIntegration(propagate_hub=True)
            ]

            # Inicializar Sentry
            sentry_sdk.init(
                dsn=dsn,
                environment=environment,
                release=f"automator-webia@{release}",
                sample_rate=sample_rate,
                integrations=integrations,

                # Configurações de performance
                traces_sample_rate=0.1 if environment == "production" else 1.0,
                profiles_sample_rate=0.1 if environment == "production" else 1.0,

                # Configurações de segurança
                send_default_pii=False,
                server_name=None,  # Não enviar nome do servidor

                # Configurações de antes envio
                before_send=self._before_send,
                before_breadcrumb=self._before_breadcrumb,

                # Configurações específicas da aplicação
                _experiments={
                    "profiles_sample_rate": 0.1,
                    "replays_session_sample_rate": 0.1 if environment == "production" else 0.0,
                    "replays_on_error_sample_rate": 1.0,
                }
            )

            self.initialized = True
            self.logger.info("✅ Sentry error tracking inicializado")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar Sentry: {e}")
            self.initialized = False

    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook executado antes de enviar evento"""
        try:
            # Adicionar contexto da aplicação
            if 'tags' not in event:
                event['tags'] = {}

            event['tags'].update({
                'service': 'automator-webia',
                'version': self.release,
                'environment': self.environment,
                'component': self._get_component_from_stack()
            })

            # Filtrar informações sensíveis
            if 'request' in event:
                request = event['request']
                if 'data' in request:
                    # Remover dados sensíveis de requests
                    self._sanitize_request_data(request['data'])

            # Adicionar métricas de sistema se erro crítico
            if event.get('level') == 'fatal':
                event['contexts'] = event.get('contexts', {})
                event['contexts']['system'] = self._get_system_context()

            return event

        except Exception as e:
            self.logger.debug(f"Erro no before_send hook: {e}")
            return event

    def _before_breadcrumb(self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook executado antes de adicionar breadcrumb"""
        try:
            # Filtrar breadcrumbs sensíveis
            if breadcrumb.get('category') == 'http':
                url = breadcrumb.get('data', {}).get('url', '')
                if any(sensitive in url.lower() for sensitive in ['password', 'token', 'secret']):
                    return None  # Não adicionar breadcrumb

            return breadcrumb

        except Exception:
            return breadcrumb

    def _sanitize_request_data(self, data: Any):
        """Remove dados sensíveis de requests"""
        if isinstance(data, dict):
            sensitive_keys = ['password', 'token', 'secret', 'key', 'authorization']
            for key in sensitive_keys:
                if key in data:
                    data[key] = '[REDACTED]'

    def _get_component_from_stack(self) -> str:
        """Identifica componente baseado na stack trace"""
        try:
            stack = traceback.extract_stack()
            for frame in reversed(stack):
                filename = frame.filename.lower()
                if 'infrastructure' in filename:
                    return 'infrastructure'
                elif 'domain' in filename:
                    return 'domain'
                elif 'application' in filename:
                    return 'application'
                elif 'presentation' in filename:
                    return 'presentation'
            return 'unknown'
        except Exception:
            return 'unknown'

    def _get_system_context(self) -> Dict[str, Any]:
        """Coleta contexto do sistema para erros críticos"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids())
            }
        except Exception:
            return {}

    def capture_exception(self, exc: Exception, **kwargs) -> Optional[str]:
        """Captura exceção"""
        if not self.initialized:
            return None

        try:
            # Adicionar contexto customizado
            with configure_scope() as scope:
                for key, value in kwargs.items():
                    if key == 'user':
                        scope.user = value
                    elif key == 'tags':
                        for tag_key, tag_value in value.items():
                            scope.set_tag(tag_key, tag_value)
                    elif key == 'extra':
                        for extra_key, extra_value in value.items():
                            scope.set_extra(extra_key, extra_value)
                    else:
                        scope.set_extra(key, value)

                return capture_exception(exc)

        except Exception as e:
            self.logger.debug(f"Erro ao capturar exception: {e}")
            return None

    def capture_message(self, message: str, level: str = "info", **kwargs) -> Optional[str]:
        """Captura mensagem customizada"""
        if not self.initialized:
            return None

        try:
            with configure_scope() as scope:
                # Configurar nível
                scope.level = level

                # Adicionar contexto
                for key, value in kwargs.items():
                    if key == 'tags':
                        for tag_key, tag_value in value.items():
                            scope.set_tag(tag_key, tag_value)
                    else:
                        scope.set_extra(key, value)

                return capture_message(message, level=level)

        except Exception as e:
            self.logger.debug(f"Erro ao capturar message: {e}")
            return None

    def capture_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Captura evento customizado"""
        if not self.initialized:
            return None

        try:
            # Usar Sentry SDK diretamente para eventos customizados
            return sentry_sdk.capture_event(event_data)
        except Exception as e:
            self.logger.debug(f"Erro ao capturar event: {e}")
            return None

    def set_user(self, user_id: str, email: Optional[str] = None, **kwargs):
        """Define usuário no contexto"""
        if not self.initialized:
            return

        try:
            with configure_scope() as scope:
                user_info = {'id': user_id}
                if email:
                    user_info['email'] = email
                user_info.update(kwargs)
                scope.user = user_info
        except Exception as e:
            self.logger.debug(f"Erro ao definir user: {e}")

    def set_tag(self, key: str, value: str):
        """Define tag no contexto"""
        if not self.initialized:
            return

        try:
            with configure_scope() as scope:
                scope.set_tag(key, value)
        except Exception as e:
            self.logger.debug(f"Erro ao definir tag: {e}")

    def set_extra(self, key: str, value: Any):
        """Define informação extra no contexto"""
        if not self.initialized:
            return

        try:
            with configure_scope() as scope:
                scope.set_extra(key, value)
        except Exception as e:
            self.logger.debug(f"Erro ao definir extra: {e}")

    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info", **kwargs):
        """Adiciona breadcrumb para contexto"""
        if not self.initialized:
            return

        try:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                **kwargs
            )
        except Exception as e:
            self.logger.debug(f"Erro ao adicionar breadcrumb: {e}")

    def flush(self, timeout: float = 2.0) -> bool:
        """Força envio de eventos pendentes"""
        if not self.initialized:
            return True

        try:
            return sentry_sdk.flush(timeout=timeout)
        except Exception as e:
            self.logger.debug(f"Erro no flush: {e}")
            return False

    def close(self):
        """Fecha cliente Sentry"""
        if not self.initialized:
            return

        try:
            sentry_sdk.close()
            self.initialized = False
            self.logger.info("Sentry client fechado")
        except Exception as e:
            self.logger.debug(f"Erro ao fechar Sentry: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do Sentry"""
        if not SENTRY_AVAILABLE:
            return {
                'status': 'unavailable',
                'message': 'Sentry SDK not installed'
            }

        if not self.initialized:
            return {
                'status': 'disabled',
                'message': 'Sentry not initialized'
            }

        try:
            # Test básico
            self.capture_message("Health check test", level="debug", tags={'test': 'health_check'})

            return {
                'status': 'healthy',
                'environment': self.environment,
                'release': self.release,
                'sample_rate': self.sample_rate
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Decorators para facilitar uso
def track_errors(**kwargs):
    """Decorator para trackear erros automaticamente"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs_inner):
            try:
                return func(*args, **kwargs_inner)
            except Exception as e:
                # Capturar erro com contexto
                error_tracker.capture_exception(
                    e,
                    function=func.__name__,
                    module=func.__module__,
                    **kwargs
                )
                raise
        return wrapper
    return decorator


def track_performance(operation: str, **kwargs):
    """Decorator para trackear performance"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs_inner):
            start_time = time.time()
            try:
                result = func(*args, **kwargs_inner)
                duration = time.time() - start_time

                # Adicionar métrica de performance
                error_tracker.capture_message(
                    f"Performance: {operation}",
                    level="info",
                    tags={'operation': operation, 'status': 'success'},
                    duration=duration,
                    **kwargs
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Capturar erro com métrica de performance
                error_tracker.capture_exception(
                    e,
                    operation=operation,
                    duration=duration,
                    **kwargs
                )
                raise
        return wrapper
    return decorator


# Instância global
error_tracker = SentryErrorTracker()


# Funções utilitárias para uso rápido
def init_sentry(dsn: Optional[str] = None, environment: str = "development", release: str = "8.0.0"):
    """Inicializa Sentry globalmente"""
    global error_tracker
    error_tracker = SentryErrorTracker(dsn=dsn, environment=environment, release=release)


def capture_error(exc: Exception, **kwargs):
    """Captura erro rapidamente"""
    return error_tracker.capture_exception(exc, **kwargs)


def capture_info(message: str, **kwargs):
    """Captura mensagem info"""
    return error_tracker.capture_message(message, level="info", **kwargs)


def capture_warning(message: str, **kwargs):
    """Captura mensagem warning"""
    return error_tracker.capture_message(message, level="warning", **kwargs)


def capture_error_msg(message: str, **kwargs):
    """Captura mensagem error"""
    return error_tracker.capture_message(message, level="error", **kwargs)
