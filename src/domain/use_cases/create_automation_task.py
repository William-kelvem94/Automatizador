#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CASOS DE USO - CQRS PATTERN
Use Cases organizados em Commands, Queries e Handlers
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from ..entities.automation_task import (
    AutomationTask, AutomationWorkflow, AutomationStep,
    TaskStatus, BrowserConfig, ActionType, Selector,
    ExecutionResult, DomainEvent
)
from ..interfaces.automation_repository import (
    IAutomationRepository, IAutomationService
)


# ===== COMMANDS =====

class Command(ABC):
    """Base para comandos"""
    pass


@dataclass
class CreateAutomationTaskCommand(Command):
    """Comando: Criar nova tarefa de automação"""
    task_id: str
    name: str
    description: str = ""
    url: str = ""
    username: str = ""
    password: str = ""
    workflow_id: Optional[str] = None
    browser_config: Optional[Dict[str, Any]] = None
    created_by: str = "system"


@dataclass
class ExecuteAutomationCommand(Command):
    """Comando: Executar tarefa de automação"""
    task_id: str
    user_id: str = "system"


@dataclass
class UpdateWorkflowCommand(Command):
    """Comando: Atualizar workflow"""
    workflow_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None


@dataclass
class DeleteAutomationCommand(Command):
    """Comando: Excluir tarefa"""
    task_id: str
    user_id: str = "system"


# ===== QUERIES =====

class Query(ABC):
    """Base para queries"""
    pass


@dataclass
class GetAutomationTasksQuery(Query):
    """Query: Buscar tarefas de automação"""
    user_id: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetExecutionHistoryQuery(Query):
    """Query: Buscar histórico de execuções"""
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class GetWorkflowAnalyticsQuery(Query):
    """Query: Buscar analytics de workflow"""
    workflow_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


@dataclass
class GetSystemHealthQuery(Query):
    """Query: Verificar saúde do sistema"""
    include_details: bool = False


# ===== COMMAND HANDLERS =====

class CommandHandler(ABC):
    """Base para command handlers"""
    @abstractmethod
    async def handle(self, command: Command) -> Dict[str, Any]:
        pass


class CreateAutomationTaskHandler(CommandHandler):
    """Handler: Criar tarefa de automação"""

    def __init__(self, task_repository: IAutomationRepository):
        self.task_repository = task_repository

    async def handle(self, command: CreateAutomationTaskCommand) -> Dict[str, Any]:
        """Executa criação de tarefa"""

        # Cria configuração do navegador
        browser_config = BrowserConfig(
            browser_type=command.browser_config.get('browser_type', 'chrome') if command.browser_config else 'chrome',
            headless=command.browser_config.get('headless', False) if command.browser_config else False,
            timeout=command.browser_config.get('timeout', 30) if command.browser_config else 30
        )

        # Cria tarefa
        task = AutomationTask(
            id=command.task_id,
            name=command.name,
            description=command.description,
            url=command.url,
            username=command.username,
            password=command.password,
            browser_config=browser_config,
            created_by=command.created_by
        )

        # Salva tarefa
        success = await self.task_repository.save_task(task)
        if not success:
            raise RuntimeError("Falha ao salvar tarefa")

        # Coleta eventos de domínio
        events = task.clear_domain_events()

        return {
            'success': True,
            'task': task.to_dict(),
            'events': [event.__dict__ for event in events],
            'message': f"Tarefa '{task.name}' criada com sucesso"
        }


class ExecuteAutomationHandler(CommandHandler):
    """Handler: Executar tarefa de automação"""

    def __init__(self, task_repository: IAutomationRepository,
                 automation_service: IAutomationService):
        self.task_repository = task_repository
        self.automation_service = automation_service

    async def handle(self, command: ExecuteAutomationCommand) -> Dict[str, Any]:
        """Executa uma tarefa de automação"""

        # Busca tarefa
        task = await self.task_repository.get_task_by_id(command.task_id)
        if not task:
            raise ValueError(f"Tarefa {command.task_id} não encontrada")

        # Verifica se tarefa pode ser executada
        if task.status == TaskStatus.RUNNING:
            raise ValueError(f"Tarefa {command.task_id} já está em execução")

        if not task.can_execute():
            raise ValueError(f"Tarefa {command.task_id} não pode ser executada")

        try:
            # Marca como executando
            task.mark_as_running()
            await self.task_repository.save_task(task)

            # Executa automação
            result = await self.automation_service.execute_task(task)

            # Processa resultado
            if result['success']:
                task.mark_as_completed(result)
            else:
                task.mark_as_failed(result.get('message', 'Erro desconhecido'))

            # Salva tarefa atualizada
            await self.task_repository.save_task(task)

            # Coleta eventos
            events = task.clear_domain_events()

            return {
                'success': result['success'],
                'task_id': command.task_id,
                'result': result,
                'events': [event.__dict__ for event in events],
                'message': result.get('message', 'Execução concluída')
            }

        except Exception as e:
            # Marca como falha em caso de erro
            task.mark_as_failed(str(e))
            await self.task_repository.save_task(task)

            events = task.clear_domain_events()

            return {
                'success': False,
                'task_id': command.task_id,
                'error': str(e),
                'events': [event.__dict__ for event in events],
                'message': f"Erro na execução: {e}"
            }


# ===== QUERY HANDLERS =====

class QueryHandler(ABC):
    """Base para query handlers"""
    @abstractmethod
    async def handle(self, query: Query) -> Dict[str, Any]:
        pass


class AutomationTaskQueryHandler(QueryHandler):
    """Handler: Queries de tarefas de automação"""

    def __init__(self, task_repository: IAutomationRepository):
        self.task_repository = task_repository

    async def handle(self, query: GetAutomationTasksQuery) -> Dict[str, Any]:
        """Busca tarefas de automação"""

        # TODO: Implementar filtros por user_id e status
        tasks = await self.task_repository.get_all_tasks()

        # Aplica paginação
        start_idx = query.offset
        end_idx = start_idx + query.limit
        paginated_tasks = tasks[start_idx:end_idx]

        return {
            'tasks': [task.to_dict() for task in paginated_tasks],
            'total_count': len(tasks),
            'limit': query.limit,
            'offset': query.offset
        }


class ExecutionHistoryQueryHandler(QueryHandler):
    """Handler: Queries de histórico de execuções"""

    def __init__(self, task_repository: IAutomationRepository):
        self.task_repository = task_repository

    async def handle(self, query: GetExecutionHistoryQuery) -> Dict[str, Any]:
        """Busca histórico de execuções"""

        tasks = await self.task_repository.get_all_tasks()

        all_executions = []
        for task in tasks:
            # Filtra por task_id se especificado
            if query.task_id and task.id != query.task_id:
                continue

            for execution in task.execution_history:
                all_executions.append({
                    'task_id': task.id,
                    'task_name': task.name,
                    **execution.__dict__
                })

        # Ordena por timestamp (mais recente primeiro)
        all_executions.sort(key=lambda x: x['timestamp'], reverse=True)

        # Aplica paginação
        start_idx = query.offset
        end_idx = start_idx + query.limit
        paginated_executions = all_executions[start_idx:end_idx]

        return {
            'executions': paginated_executions,
            'total_count': len(all_executions),
            'limit': query.limit,
            'offset': query.offset
        }


class HealthCheckQueryHandler(QueryHandler):
    """Handler: Verificação de saúde do sistema"""

    def __init__(self, task_repository: IAutomationRepository):
        self.task_repository = task_repository

    async def handle(self, query: GetSystemHealthQuery) -> Dict[str, Any]:
        """Verifica saúde do sistema"""

        try:
            # Verifica conectividade com banco
            tasks = await self.task_repository.get_all_tasks()
            db_status = "healthy" if tasks is not None else "unhealthy"

            # Estatísticas básicas
            total_tasks = len(tasks) if tasks else 0
            running_tasks = sum(1 for task in tasks if task.status == TaskStatus.RUNNING) if tasks else 0

            health_data = {
                'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': db_status,
                    'automation_service': 'healthy'  # TODO: Implementar verificação real
                },
                'metrics': {
                    'total_tasks': total_tasks,
                    'running_tasks': running_tasks
                }
            }

            if query.include_details:
                health_data['details'] = {
                    'uptime': 'unknown',  # TODO: Implementar
                    'memory_usage': 'unknown',  # TODO: Implementar
                    'cpu_usage': 'unknown'  # TODO: Implementar
                }

            return health_data

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# ===== USE CASE ORCHESTRATORS =====

class ExecuteAutomationTaskUseCase:
    """Caso de uso: Executar tarefa de automação (compatibilidade)"""

    def __init__(self, task_repository: IAutomationRepository,
                 automation_service: IAutomationService, user_id: str, logger):
        self.task_repository = task_repository
        self.automation_service = automation_service
        self.user_id = user_id
        self.logger = logger

        # Usa o command handler
        self.execute_handler = ExecuteAutomationHandler(task_repository, automation_service)

    async def execute(self, task_id: str) -> Dict[str, Any]:
        """Executa uma tarefa de automação"""
        command = ExecuteAutomationCommand(task_id=task_id, user_id=self.user_id)
        return await self.execute_handler.handle(command)


class AnalyzeWebPageUseCase:
    """Caso de uso: Analisar página web"""

    def __init__(self, automation_service: IAutomationService, logger):
        self.automation_service = automation_service
        self.logger = logger

    async def execute(self, url: str) -> Dict[str, Any]:
        """Analisa uma página web"""

        if not url:
            raise ValueError("URL é obrigatória")

        try:
            self.logger.info(f"Iniciando análise da página: {url}")
            analysis = await self.automation_service.analyze_page(url)

            # Gera recomendações
            recommendations = analysis.generate_recommendations()

            result = {
                'success': True,
                'analysis': analysis.to_dict(),
                'recommendations': recommendations,
                'message': f"Análise concluída para {url}"
            }

            self.logger.info(f"Análise concluída: {len(analysis.potential_username_fields)} campos usuário, "
                           f"{len(analysis.potential_password_fields)} campos senha, "
                           f"{len(analysis.potential_submit_buttons)} botões submit")

            return result

        except Exception as e:
            self.logger.error(f"Erro na análise da página {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Falha na análise: {e}"
            }


class GetTaskStatisticsUseCase:
    """Caso de uso: Obter estatísticas das tarefas"""

    def __init__(self, task_repository: IAutomationRepository):
        self.task_repository = task_repository

    async def execute(self) -> Dict[str, Any]:
        """Calcula estatísticas das tarefas"""

        tasks = await self.task_repository.get_all_tasks()

        stats = {
            'total_tasks': len(tasks),
            'tasks_by_status': {},
            'success_rate': 0.0,
            'average_execution_time': 0.0,
            'total_executions': 0,
            'recent_executions': []
        }

        # Conta por status
        for task in tasks:
            status = task.status.value
            stats['tasks_by_status'][status] = stats['tasks_by_status'].get(status, 0) + 1

            # Estatísticas de execução
            if task.execution_history:
                stats['total_executions'] += len(task.execution_history)

                # Últimas execuções
                for result in task.execution_history[-5:]:  # Últimas 5 por tarefa
                    stats['recent_executions'].append({
                        'task_id': task.id,
                        'task_name': task.name,
                        'success': result.success,
                        'timestamp': result.timestamp.isoformat(),
                        'execution_time': result.execution_time
                    })

        # Taxa de sucesso global
        if stats['total_executions'] > 0:
            successful_executions = sum(1 for task in tasks
                                      for result in task.execution_history
                                      if result.success)
            stats['success_rate'] = (successful_executions / stats['total_executions']) * 100

        # Tempo médio de execução
        execution_times = [result.execution_time
                          for task in tasks
                          for result in task.execution_history
                          if result.execution_time > 0]

        if execution_times:
            stats['average_execution_time'] = sum(execution_times) / len(execution_times)

        # Ordena execuções recentes por timestamp
        stats['recent_executions'].sort(key=lambda x: x['timestamp'], reverse=True)
        stats['recent_executions'] = stats['recent_executions'][:20]  # Top 20

        return stats