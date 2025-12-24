#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
INTERFACES DO DOMÍNIO - PORTS
Contratos abstratos para comunicação entre camadas
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.automation_task import AutomationTask, AutomationWorkflow, WebPageAnalysis, ExecutionResult


class IAutomationRepository(ABC):
    """Interface para persistência de tarefas de automação"""

    @abstractmethod
    async def save_task(self, task: AutomationTask) -> bool:
        """Salva uma tarefa de automação"""
        pass

    @abstractmethod
    async def get_task_by_id(self, task_id: str) -> Optional[AutomationTask]:
        """Busca tarefa por ID"""
        pass

    @abstractmethod
    async def get_all_tasks(self) -> List[AutomationTask]:
        """Retorna todas as tarefas"""
        pass

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """Remove uma tarefa"""
        pass

    @abstractmethod
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Atualiza status de uma tarefa"""
        pass

    @abstractmethod
    async def get_tasks_by_status(self, status: str) -> List[AutomationTask]:
        """Busca tarefas por status"""
        pass

    @abstractmethod
    async def get_recent_executions(self, limit: int = 50) -> List[ExecutionResult]:
        """Busca execuções recentes"""
        pass


class IWorkflowRepository(ABC):
    """Interface para persistência de workflows"""

    @abstractmethod
    async def save_workflow(self, workflow: AutomationWorkflow) -> bool:
        """Salva um workflow"""
        pass

    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> Optional[AutomationWorkflow]:
        """Busca workflow por ID"""
        pass

    @abstractmethod
    async def get_all_workflows(self) -> List[AutomationWorkflow]:
        """Retorna todos os workflows"""
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Remove um workflow"""
        pass


class IExecutionHistoryRepository(ABC):
    """Interface para persistência de histórico de execuções"""

    @abstractmethod
    async def save_execution_result(self, result: ExecutionResult) -> bool:
        """Salva resultado de execução"""
        pass

    @abstractmethod
    async def get_execution_by_id(self, execution_id: str) -> Optional[ExecutionResult]:
        """Busca execução por ID"""
        pass

    @abstractmethod
    async def get_executions_by_task_id(self, task_id: str) -> List[ExecutionResult]:
        """Busca execuções por tarefa"""
        pass

    @abstractmethod
    async def get_recent_executions(self, limit: int = 100) -> List[ExecutionResult]:
        """Busca execuções recentes"""
        pass


class IAutomationService(ABC):
    """Interface para serviços de automação web"""

    @abstractmethod
    async def execute_task(self, task: AutomationTask) -> Dict[str, Any]:
        """Executa uma tarefa de automação completa"""
        pass

    @abstractmethod
    async def execute_workflow_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um passo individual do workflow"""
        pass

    @abstractmethod
    async def analyze_page(self, url: str) -> WebPageAnalysis:
        """Analisa uma página web para identificar elementos"""
        pass

    @abstractmethod
    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Testa conexão básica com um site"""
        pass

    @abstractmethod
    async def validate_selectors(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Valida se os seletores funcionam na página"""
        pass

    @abstractmethod
    async def capture_screenshot(self, url: str, selector: Optional[str] = None) -> bytes:
        """Captura screenshot da página ou elemento"""
        pass


class IIntelligenceService(ABC):
    """Interface para serviços de inteligência artificial"""

    @abstractmethod
    async def generate_selector(self, element_description: str, page_context: str) -> str:
        """Gera seletor inteligente baseado em descrição"""
        pass

    @abstractmethod
    async def analyze_form_structure(self, form_html: str) -> Dict[str, Any]:
        """Analisa estrutura de formulário"""
        pass

    @abstractmethod
    async def predict_execution_success(self, task_data: Dict[str, Any]) -> float:
        """Prediz probabilidade de sucesso da execução"""
        pass

    @abstractmethod
    async def suggest_optimizations(self, execution_history: List[Dict[str, Any]]) -> List[str]:
        """Sugere otimizações baseadas no histórico"""
        pass


class IEventBus(ABC):
    """Interface para sistema de eventos assíncrono"""

    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publica um evento"""
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler) -> None:
        """Inscreve um handler para um tipo de evento"""
        pass

    @abstractmethod
    async def unsubscribe(self, event_type: str, handler) -> None:
        """Remove inscrição de um handler"""
        pass


class ICacheService(ABC):
    """Interface para serviço de cache"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define valor no cache"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Limpa todo o cache"""
        pass


class ILogger(ABC):
    """Interface para sistema de logging"""

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug"""
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log informativo"""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso"""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log de erro"""
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """Log crítico"""
        pass
