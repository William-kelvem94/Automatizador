#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ENTIDADES DO DOMÍNIO - AUTOMATIZADOR IA v7.0
Entidades de negócio puras seguindo Domain-Driven Design (DDD)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from abc import ABC, abstractmethod


# ===== VALUE OBJECTS =====

@dataclass(frozen=True)
class Selector:
    """Value Object: Seletor CSS/XPath/AI-Generated"""
    value: str
    selector_type: str = "css"  # css, xpath, ai_generated
    confidence: float = 1.0

    def __post_init__(self):
        if not self.value:
            raise ValueError("Seletor não pode ser vazio")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confiança deve estar entre 0.0 e 1.0")


@dataclass(frozen=True)
class ActionType(Enum):
    """Value Object: Tipos de ação suportados"""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    ASSERT = "assert"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"


@dataclass(frozen=True)
class BrowserConfig:
    """Value Object: Configurações do navegador"""
    browser_type: str = "chrome"
    headless: bool = False
    user_agent: Optional[str] = None
    window_size: Optional[tuple] = None
    timeout: int = 30

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("Timeout deve ser positivo")


@dataclass(frozen=True)
class ValidationRule:
    """Value Object: Regras de validação"""
    rule_type: str  # element_exists, text_contains, url_matches
    value: str
    description: str = ""

    def validate(self, actual_value: str) -> bool:
        """Valida se o valor atual atende à regra"""
        if self.rule_type == "element_exists":
            return bool(actual_value)
        elif self.rule_type == "text_contains":
            return self.value in actual_value
        elif self.rule_type == "url_matches":
            return self.value in actual_value
        return True


# ===== DOMAIN EVENTS =====

@dataclass
class DomainEvent(ABC):
    """Base para eventos de domínio"""
    @abstractmethod
    def event_type(self) -> str:
        pass


@dataclass
class TaskCreatedEvent(DomainEvent):
    """Evento: Tarefa criada"""
    task_id: str
    task_name: str
    created_by: str
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")

    def event_type(self) -> str:
        return "task_created"


@dataclass
class TaskExecutedEvent(DomainEvent):
    """Evento: Tarefa executada"""
    task_id: str
    success: bool
    execution_time: float
    result_data: Dict[str, Any]
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")

    def event_type(self) -> str:
        return "task_executed"


@dataclass
class TaskFailedEvent(DomainEvent):
    """Evento: Tarefa falhou"""
    task_id: str
    error_message: str
    error_details: Optional[str] = None
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")

    def event_type(self) -> str:
        return "task_failed"


# ===== ENTITIES (AGGREGATE ROOTS) =====

class TaskStatus(Enum):
    """Status possíveis de uma tarefa de automação"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BrowserType(Enum):
    """Tipos de navegador suportados"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


@dataclass
class AutomationStep:
    """Entidade: Passo individual de automação"""
    id: str
    action_type: ActionType
    selector: Optional[Selector] = None
    value: Optional[str] = None
    description: str = ""
    order: int = 0
    timeout: int = 10
    validation_rules: List[ValidationRule] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            raise ValueError("ID do passo é obrigatório")

    def add_validation_rule(self, rule: ValidationRule):
        """Adiciona regra de validação"""
        self.validation_rules.append(rule)

    def validate_result(self, result_data: Dict[str, Any]) -> bool:
        """Valida resultado do passo"""
        for rule in self.validation_rules:
            if not rule.validate(str(result_data.get('result', ''))):
                return False
        return True


@dataclass
class AutomationWorkflow:
    """Entidade: Workflow completo de automação"""
    id: str
    name: str
    description: str = ""
    steps: List[AutomationStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.id:
            raise ValueError("ID do workflow é obrigatório")
        if not self.name:
            raise ValueError("Nome do workflow é obrigatório")

    def add_step(self, step: AutomationStep):
        """Adiciona passo ao workflow"""
        step.order = len(self.steps)
        self.steps.append(step)
        self.updated_at = datetime.now()

    def get_step_by_id(self, step_id: str) -> Optional[AutomationStep]:
        """Busca passo por ID"""
        return next((step for step in self.steps if step.id == step_id), None)

    def validate_workflow(self) -> List[str]:
        """Valida integridade do workflow"""
        errors = []
        if not self.steps:
            errors.append("Workflow deve ter pelo menos um passo")

        step_ids = set()
        for step in self.steps:
            if step.id in step_ids:
                errors.append(f"Passo duplicado: {step.id}")
            step_ids.add(step.id)

        return errors


@dataclass
class ExecutionResult:
    """Entidade: Resultado de uma execução"""
    id: str
    task_id: str
    workflow_id: str
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error_details: Optional[str] = None
    step_results: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            raise ValueError("ID do resultado é obrigatório")
        if not self.task_id:
            raise ValueError("ID da tarefa é obrigatório")

    def add_step_result(self, step_id: str, success: bool, result: Any, duration: float):
        """Adiciona resultado de um passo"""
        self.step_results.append({
            'step_id': step_id,
            'success': success,
            'result': str(result) if result is not None else None,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })

    def get_step_results(self) -> List[Dict[str, Any]]:
        """Retorna resultados dos passos"""
        return self.step_results.copy()


@dataclass
class AutomationTask:
    """AGGREGATE ROOT: Entidade principal de tarefa de automação"""
    id: str
    name: str
    description: str = ""
    url: str = ""
    username: str = ""
    password: str = ""

    # Relacionamentos
    workflow: Optional[AutomationWorkflow] = None

    # Configurações
    browser_config: BrowserConfig = field(default_factory=BrowserConfig)
    max_retries: int = 3
    retry_delay: int = 5

    # Status e controle
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    last_execution: Optional[datetime] = None

    # Histórico
    execution_history: List[ExecutionResult] = field(default_factory=list)

    # Eventos de domínio
    domain_events: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self):
        """Validações pós-inicialização"""
        if not self.id:
            raise ValueError("ID da tarefa é obrigatório")
        if not self.name:
            raise ValueError("Nome da tarefa é obrigatório")
        if not self.url:
            raise ValueError("URL é obrigatória")

        # Adiciona evento de criação
        self.add_domain_event(TaskCreatedEvent(
            task_id=self.id,
            task_name=self.name,
            created_by=self.created_by
        ))

    def assign_workflow(self, workflow: AutomationWorkflow):
        """Atribui workflow à tarefa"""
        self.workflow = workflow
        self.updated_at = datetime.now()

    def mark_as_running(self):
        """Marca tarefa como em execução"""
        self.status = TaskStatus.RUNNING
        self.updated_at = datetime.now()

    def mark_as_completed(self, result: ExecutionResult):
        """Marca tarefa como concluída"""
        self.status = TaskStatus.COMPLETED
        self.last_execution = datetime.now()
        self.updated_at = datetime.now()
        self.execution_history.append(result)

        # Adiciona evento
        self.add_domain_event(TaskExecutedEvent(
            task_id=self.id,
            success=True,
            execution_time=result.execution_time,
            result_data=result.data
        ))

    def mark_as_failed(self, error_message: str, error_details: Optional[str] = None):
        """Marca tarefa como falhada"""
        self.status = TaskStatus.FAILED
        self.last_execution = datetime.now()
        self.updated_at = datetime.now()

        result = ExecutionResult(
            id=f"result_{datetime.now().timestamp()}",
            task_id=self.id,
            workflow_id=self.workflow.id if self.workflow else "",
            success=False,
            message=f"Falha na execução: {error_message}",
            error_details=error_details,
            execution_time=0.0
        )
        self.execution_history.append(result)

        # Adiciona evento
        self.add_domain_event(TaskFailedEvent(
            task_id=self.id,
            error_message=error_message,
            error_details=error_details
        ))

    def can_execute(self) -> bool:
        """Verifica se a tarefa pode ser executada"""
        return (self.status in [TaskStatus.PENDING, TaskStatus.FAILED] and
                self.workflow is not None and
                len(self.workflow.steps) > 0)

    def get_last_result(self) -> Optional[ExecutionResult]:
        """Retorna o último resultado de execução"""
        return self.execution_history[-1] if self.execution_history else None

    def get_success_rate(self) -> float:
        """Calcula taxa de sucesso baseada no histórico"""
        if not self.execution_history:
            return 0.0

        successful = sum(1 for result in self.execution_history if result.success)
        return (successful / len(self.execution_history)) * 100

    def add_domain_event(self, event: DomainEvent):
        """Adiciona evento de domínio"""
        self.domain_events.append(event)

    def clear_domain_events(self) -> List[DomainEvent]:
        """Retorna e limpa eventos de domínio"""
        events = self.domain_events.copy()
        self.domain_events.clear()
        return events

    def to_dict(self) -> Dict[str, Any]:
        """Converte entidade para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'username': self.username,
            'password': self.password,
            'workflow_id': self.workflow.id if self.workflow else None,
            'browser_config': {
                'browser_type': self.browser_config.browser_type,
                'headless': self.browser_config.headless,
                'timeout': self.browser_config.timeout
            },
            'max_retries': self.max_retries,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': len(self.execution_history),
            'success_rate': self.get_success_rate()
        }


@dataclass
class WebPageAnalysis:
    """Entidade: Resultado da análise de uma página web"""
    id: str
    url: str
    title: str = ""
    forms_count: int = 0
    inputs_count: int = 0
    buttons_count: int = 0
    links_count: int = 0

    # Elementos identificados
    potential_username_fields: List[Dict[str, Any]] = field(default_factory=list)
    potential_password_fields: List[Dict[str, Any]] = field(default_factory=list)
    potential_submit_buttons: List[Dict[str, Any]] = field(default_factory=list)

    # Metadados da análise
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_duration: float = 0.0

    # Sugestões automáticas
    recommended_selectors: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            raise ValueError("ID da análise é obrigatório")
        if not self.url:
            raise ValueError("URL é obrigatória")

    def add_username_field(self, field_data: Dict[str, Any]):
        """Adiciona campo de usuário identificado"""
        self.potential_username_fields.append(field_data)

    def add_password_field(self, field_data: Dict[str, Any]):
        """Adiciona campo de senha identificado"""
        self.potential_password_fields.append(field_data)

    def add_submit_button(self, button_data: Dict[str, Any]):
        """Adiciona botão submit identificado"""
        self.potential_submit_buttons.append(button_data)

    def generate_recommendations(self):
        """Gera recomendações automáticas baseadas na análise"""
        recommendations = {}

        # Recomendação para usuário
        if self.potential_username_fields:
            best_user = max(self.potential_username_fields,
                          key=lambda x: x.get('confidence', 0))
            recommendations['username'] = best_user.get('selector', '')

        # Recomendação para senha
        if self.potential_password_fields:
            best_pass = max(self.potential_password_fields,
                          key=lambda x: x.get('confidence', 0))
            recommendations['password'] = best_pass.get('selector', '')

        # Recomendação para submit
        if self.potential_submit_buttons:
            best_submit = max(self.potential_submit_buttons,
                            key=lambda x: x.get('confidence', 0))
            recommendations['submit'] = best_submit.get('selector', '')

        self.recommended_selectors = recommendations
        return recommendations

    def to_dict(self) -> Dict[str, Any]:
        """Converte análise para dicionário"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'forms_count': self.forms_count,
            'inputs_count': self.inputs_count,
            'buttons_count': self.buttons_count,
            'links_count': self.links_count,
            'potential_username_fields': self.potential_username_fields,
            'potential_password_fields': self.potential_password_fields,
            'potential_submit_buttons': self.potential_submit_buttons,
            'analyzed_at': self.analyzed_at.isoformat(),
            'analysis_duration': self.analysis_duration,
            'recommended_selectors': self.recommended_selectors
        }
