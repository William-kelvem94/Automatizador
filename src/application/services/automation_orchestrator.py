#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ORQUESTRADOR DE AUTOMAÇÃO - CQRS IMPLEMENTATION
Coordena commands, queries e event handlers
"""

from typing import Dict, Any, Optional, List, Callable
from ...domain.use_cases.create_automation_task import (
    Command, Query, CommandHandler, QueryHandler,
    CreateAutomationTaskCommand, ExecuteAutomationCommand,
    GetAutomationTasksQuery, GetExecutionHistoryQuery, GetSystemHealthQuery,
    CreateAutomationTaskHandler, ExecuteAutomationHandler,
    AutomationTaskQueryHandler, ExecutionHistoryQueryHandler, HealthCheckQueryHandler
)
from ...domain.interfaces.automation_repository import (
    IAutomationRepository, IAutomationService, IEventBus
)
from ...shared.utils.logger import get_logger


class AutomationOrchestrator:
    """Orquestrador principal com CQRS"""

    def __init__(self,
                 task_repository: IAutomationRepository,
                 automation_service: IAutomationService,
                 event_bus: Optional[IEventBus] = None):
        self.task_repository = task_repository
        self.automation_service = automation_service
        self.event_bus = event_bus
        self.logger = get_logger(__name__)

        # Command Handlers
        self.command_handlers: Dict[type, CommandHandler] = {
            CreateAutomationTaskCommand: CreateAutomationTaskHandler(task_repository),
            ExecuteAutomationCommand: ExecuteAutomationHandler(task_repository, automation_service)
        }

        # Query Handlers
        self.query_handlers: Dict[type, QueryHandler] = {
            GetAutomationTasksQuery: AutomationTaskQueryHandler(task_repository),
            GetExecutionHistoryQuery: ExecutionHistoryQueryHandler(task_repository),
            GetSystemHealthQuery: HealthCheckQueryHandler(task_repository)
        }

        # Event Handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            'task_created': [self._handle_task_created],
            'task_executed': [self._handle_task_executed],
            'task_failed': [self._handle_task_failed]
        }

        # Registra event handlers no bus
        if self.event_bus:
            self._register_event_handlers()

    async def send_command(self, command: Command) -> Dict[str, Any]:
        """Envia comando para execução"""
        try:
            handler_class = type(command)
            if handler_class not in self.command_handlers:
                raise ValueError(f"Handler não encontrado para comando: {handler_class.__name__}")

            handler = self.command_handlers[handler_class]
            result = await handler.handle(command)

            # Publica eventos se houver
            if 'events' in result and self.event_bus:
                for event_data in result['events']:
                    await self.event_bus.publish(event_data['event_type'], event_data)

            return result

        except Exception as e:
            self.logger.error(f"Erro ao processar comando {type(command).__name__}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro no comando: {e}"
            }

    async def send_query(self, query: Query) -> Dict[str, Any]:
        """Envia query para execução"""
        try:
            handler_class = type(query)
            if handler_class not in self.query_handlers:
                raise ValueError(f"Handler não encontrado para query: {handler_class.__name__}")

            handler = self.query_handlers[handler_class]
            return await handler.handle(query)

        except Exception as e:
            self.logger.error(f"Erro ao processar query {type(query).__name__}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro na query: {e}"
            }

    # ===== COMMAND METHODS =====

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova tarefa através de comando"""
        command = CreateAutomationTaskCommand(
            task_id=task_data.get('id') or f"task_{len(await self.task_repository.get_all_tasks()) + 1}",
            name=task_data['name'],
            description=task_data.get('description', ''),
            url=task_data.get('url', ''),
            username=task_data.get('username', ''),
            password=task_data.get('password', ''),
            browser_config=task_data.get('browser_config'),
            created_by=task_data.get('created_by', 'system')
        )
        return await self.send_command(command)

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Executa tarefa através de comando"""
        command = ExecuteAutomationCommand(task_id=task_id)
        return await self.send_command(command)

    # ===== QUERY METHODS =====

    async def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Busca tarefas através de query"""
        query = GetAutomationTasksQuery(
            user_id=filters.get('user_id') if filters else None,
            status=filters.get('status') if filters else None,
            limit=filters.get('limit', 50) if filters else 50,
            offset=filters.get('offset', 0) if filters else 0
        )
        return await self.send_query(query)

    async def get_execution_history(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Busca histórico de execuções"""
        query = GetExecutionHistoryQuery(
            task_id=filters.get('task_id') if filters else None,
            user_id=filters.get('user_id') if filters else None,
            limit=filters.get('limit', 100) if filters else 100,
            offset=filters.get('offset', 0) if filters else 0
        )
        return await self.send_query(query)

    async def get_system_health(self, include_details: bool = False) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        query = GetSystemHealthQuery(include_details=include_details)
        return await self.send_query(query)

    # ===== EVENT HANDLERS =====

    def _register_event_handlers(self):
        """Registra handlers de eventos no event bus"""
        for event_type, handlers in self.event_handlers.items():
            for handler in handlers:
                self.event_bus.subscribe(event_type, handler)

    async def _handle_task_created(self, event_data: Dict[str, Any]):
        """Handler para evento de tarefa criada"""
        self.logger.info(f"Tarefa criada: {event_data['task_id']} por {event_data['created_by']}")
        # TODO: Implementar lógica adicional (notificações, analytics, etc.)

    async def _handle_task_executed(self, event_data: Dict[str, Any]):
        """Handler para evento de tarefa executada"""
        success = event_data['success']
        execution_time = event_data['execution_time']
        status = "com sucesso" if success else "com falha"

        self.logger.info(f"Tarefa {event_data['task_id']} executada {status} em {execution_time:.2f}s")
        # TODO: Implementar analytics, notificações, etc.

    async def _handle_task_failed(self, event_data: Dict[str, Any]):
        """Handler para evento de tarefa falhada"""
        self.logger.error(f"Tarefa {event_data['task_id']} falhou: {event_data['error_message']}")
        # TODO: Implementar retry logic, alertas, etc.

    # ===== LEGACY COMPATIBILITY =====

    async def analyze_webpage(self, url: str) -> Dict[str, Any]:
        """Análise de página web (compatibilidade)"""
        try:
            analysis = await self.automation_service.analyze_page(url)
            return {
                'success': True,
                'analysis': analysis.to_dict(),
                'message': f"Análise concluída para {url}"
            }
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro na análise: {e}"
            }

    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Testa conexão (compatibilidade)"""
        try:
            result = await self.automation_service.test_connection(url)
            return result
        except Exception as e:
            self.logger.error(f"Erro no teste de conexão: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro no teste: {e}"
            }