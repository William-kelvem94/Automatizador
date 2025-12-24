# -*- coding: utf-8 -*-

"""
GRAPHQL SCHEMA - Enterprise GraphQL API
Schema GraphQL completo para Automator Web IA v8.0
"""

import strawberry
from strawberry import Schema
from strawberry.types import Info
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Imports da aplicação
from ...domain.entities.automation_task import (
    AutomationTask, AutomationWorkflow, AutomationStep,
    Selector, ActionType, BrowserConfig
)
from ...application.services.automation_orchestrator import AutomationOrchestrator
from ...infrastructure.monitoring.metrics_collector import metrics_collector
from ...infrastructure.ai.multi_model_orchestrator import ai_orchestrator


# ===== GRAPHQL TYPES =====

@strawberry.type
class TaskMetrics:
    """Métricas de uma tarefa"""
    success_rate: float
    execution_count: int
    average_execution_time: float
    last_execution: Optional[str]
    total_cost: float


@strawberry.type
class SelectorInfo:
    """Informações de seletor"""
    value: str
    type: str
    confidence: float


@strawberry.type
class BrowserConfiguration:
    """Configuração do navegador"""
    headless: bool
    user_agent: Optional[str]
    viewport_width: Optional[int]
    viewport_height: Optional[int]
    timeout: int


@strawberry.type
class AutomationStepType:
    """Passo de automação"""
    id: str
    action_type: str
    selector: Optional[str]
    selector_info: Optional[SelectorInfo]
    order: int
    parameters: strawberry.scalars.JSON
    created_at: str


@strawberry.type
class AutomationWorkflowType:
    """Workflow de automação"""
    id: str
    name: str
    description: str
    steps: List[AutomationStepType]
    created_by: str
    created_at: str
    updated_at: str
    is_active: bool


@strawberry.type
class AutomationTaskType:
    """Tarefa de automação"""
    id: str
    name: str
    description: str
    url: str
    username: Optional[str]
    password: Optional[str]  # Nunca exposto, sempre None
    username_selector: Optional[str]
    password_selector: Optional[str]
    submit_selector: Optional[str]
    workflow: Optional[AutomationWorkflowType]
    status: str
    max_retries: int
    timeout: int
    browser_config: BrowserConfiguration
    tags: List[str]
    created_at: str
    updated_at: str
    metrics: TaskMetrics


@strawberry.type
class ExecutionResultType:
    """Resultado de execução"""
    success: bool
    execution_time: float
    message: str
    result_data: Optional[strawberry.scalars.JSON]
    error_message: Optional[str]
    timestamp: str


@strawberry.type
class SystemHealth:
    """Saúde do sistema"""
    status: str
    services: strawberry.scalars.JSON
    metrics: strawberry.scalars.JSON
    timestamp: str


@strawberry.type
class AIModelInfo:
    """Informações de modelo de IA"""
    id: str
    model_type: str
    provider: str
    model_name: str
    capabilities: List[str]
    status: str
    usage_stats: strawberry.scalars.JSON


@strawberry.type
class AnalyticsData:
    """Dados de analytics"""
    period: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_execution_time: float
    cost_breakdown: strawberry.scalars.JSON
    top_workflows: List[strawberry.scalars.JSON]


# ===== INPUT TYPES =====

@strawberry.input
class CreateTaskInput:
    """Input para criar tarefa"""
    name: str
    description: str
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    workflow_id: Optional[str] = None
    max_retries: Optional[int] = 3
    timeout: Optional[int] = 30000
    tags: Optional[List[str]] = None


@strawberry.input
class UpdateTaskInput:
    """Input para atualizar tarefa"""
    name: Optional[str] = None
    description: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    max_retries: Optional[int] = None
    timeout: Optional[int] = None
    tags: Optional[List[str]] = None


@strawberry.input
class CreateWorkflowInput:
    """Input para criar workflow"""
    name: str
    description: str
    steps: List[strawberry.scalars.JSON]


@strawberry.input
class AnalyzeWebpageInput:
    """Input para análise de página"""
    url: str
    include_screenshot: Optional[bool] = False
    analysis_types: Optional[List[str]] = None


@strawberry.input
class AIRequestInput:
    """Input para requisição de IA"""
    model_id: str
    prompt: str
    input_data: Optional[strawberry.scalars.JSON] = None
    priority: Optional[int] = 1


# ===== QUERY RESOLVERS =====

@strawberry.type
class Query:
    """Queries GraphQL"""

    @strawberry.field
    async def tasks(
        self,
        info: Info,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[AutomationTaskType]:
        """Buscar tarefas com filtros"""
        start_time = time.time()

        try:
            # Obter orchestrator do contexto
            orchestrator = info.context.get("orchestrator")
            if not orchestrator:
                raise Exception("Orchestrator not available")

            # Aplicar filtros
            filters = {}
            if status:
                filters["status"] = status
            if limit:
                filters["limit"] = limit
            if offset:
                filters["offset"] = offset
            if tags:
                filters["tags"] = tags

            result = await orchestrator.get_tasks(filters)
            tasks_data = result.get("tasks", [])

            # Converter para tipos GraphQL
            tasks = []
            for task_data in tasks_data:
                task = self._convert_task_to_graphql(task_data)
                tasks.append(task)

            # Métricas
            metrics_collector.record_api_request(
                "graphql", "tasks", 200, time.time() - start_time
            )

            return tasks

        except Exception as e:
            metrics_collector.record_error("graphql", "query_tasks")
            raise

    @strawberry.field
    async def task(self, info: Info, id: str) -> Optional[AutomationTaskType]:
        """Buscar tarefa específica"""
        try:
            orchestrator = info.context.get("orchestrator")
            if not orchestrator:
                raise Exception("Orchestrator not available")

            task_data = await orchestrator.get_task_by_id(id)
            if not task_data:
                return None

            return self._convert_task_to_graphql(task_data)

        except Exception as e:
            metrics_collector.record_error("graphql", "query_task")
            raise

    @strawberry.field
    async def workflows(self, info: Info) -> List[AutomationWorkflowType]:
        """Buscar workflows"""
        try:
            # Implementação simplificada - em produção teria service dedicado
            return []
        except Exception as e:
            raise

    @strawberry.field
    async def system_health(self, info: Info) -> SystemHealth:
        """Saúde do sistema"""
        try:
            orchestrator = info.context.get("orchestrator")
            if orchestrator:
                health_data = await orchestrator.get_system_health()
            else:
                health_data = {"status": "unknown", "services": {}}

            return SystemHealth(
                status=health_data.get("status", "unknown"),
                services=health_data.get("services", {}),
                metrics=metrics_collector.get_metrics_json(),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise

    @strawberry.field
    async def ai_models(self, info: Info) -> List[AIModelInfo]:
        """Modelos de IA disponíveis"""
        try:
            models = []
            for model_id, config in ai_orchestrator.model_configs.items():
                model_info = AIModelInfo(
                    id=model_id,
                    model_type=config.model_type.value,
                    provider=config.provider.value,
                    model_name=config.model_name,
                    capabilities=config.capabilities,
                    status="available" if ai_orchestrator.is_running else "offline",
                    usage_stats=ai_orchestrator.stats.get('model_usage', {}).get(model_id, {})
                )
                models.append(model_info)

            return models

        except Exception as e:
            raise

    @strawberry.field
    async def analytics(
        self,
        info: Info,
        period_days: Optional[int] = 7
    ) -> AnalyticsData:
        """Dados de analytics"""
        try:
            # Implementação simplificada - em produção teria analytics service
            return AnalyticsData(
                period=f"{period_days} days",
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                average_execution_time=0.0,
                cost_breakdown={},
                top_workflows=[]
            )

        except Exception as e:
            raise

    def _convert_task_to_graphql(self, task_data: Dict[str, Any]) -> AutomationTaskType:
        """Converter dados de tarefa para tipo GraphQL"""
        # Workflow (simplificado)
        workflow = None
        if task_data.get("workflow"):
            workflow_data = task_data["workflow"]
            workflow = AutomationWorkflowType(
                id=workflow_data.get("id", ""),
                name=workflow_data.get("name", ""),
                description=workflow_data.get("description", ""),
                steps=[],  # Implementar conversão se necessário
                created_by=workflow_data.get("created_by", ""),
                created_at=workflow_data.get("created_at", ""),
                updated_at=workflow_data.get("updated_at", ""),
                is_active=True
            )

        # Browser config
        browser_data = task_data.get("browser_config", {})
        browser_config = BrowserConfiguration(
            headless=browser_data.get("headless", True),
            user_agent=browser_data.get("user_agent"),
            viewport_width=browser_data.get("viewport", {}).get("width"),
            viewport_height=browser_data.get("viewport", {}).get("height"),
            timeout=task_data.get("timeout", 30000)
        )

        # Metrics (simplificado)
        metrics = TaskMetrics(
            success_rate=task_data.get("success_rate", 0.0),
            execution_count=task_data.get("execution_count", 0),
            average_execution_time=task_data.get("average_execution_time", 0.0),
            last_execution=task_data.get("last_execution"),
            total_cost=task_data.get("total_cost", 0.0)
        )

        return AutomationTaskType(
            id=task_data.get("id", ""),
            name=task_data.get("name", ""),
            description=task_data.get("description", ""),
            url=task_data.get("url", ""),
            username=task_data.get("username"),
            password=None,  # Nunca expor senha
            username_selector=task_data.get("username_selector"),
            password_selector=task_data.get("password_selector"),
            submit_selector=task_data.get("submit_selector"),
            workflow=workflow,
            status=task_data.get("status", "pending"),
            max_retries=task_data.get("max_retries", 3),
            timeout=task_data.get("timeout", 30000),
            browser_config=browser_config,
            tags=task_data.get("tags", []),
            created_at=task_data.get("created_at", ""),
            updated_at=task_data.get("updated_at", ""),
            metrics=metrics
        )


# ===== MUTATION RESOLVERS =====

@strawberry.type
class Mutation:
    """Mutations GraphQL"""

    @strawberry.mutation
    async def create_task(self, info: Info, input: CreateTaskInput) -> AutomationTaskType:
        """Criar nova tarefa"""
        start_time = time.time()

        try:
            orchestrator = info.context.get("orchestrator")
            if not orchestrator:
                raise Exception("Orchestrator not available")

            # Preparar dados
            task_data = {
                "name": input.name,
                "description": input.description,
                "url": input.url,
                "username": input.username,
                "password": input.password,
                "max_retries": input.max_retries,
                "timeout": input.timeout,
                "tags": input.tags or []
            }

            # Criar tarefa
            result = await orchestrator.create_task(task_data)

            if not result.get("success"):
                raise Exception(result.get("message", "Failed to create task"))

            # Obter tarefa criada
            task_id = result.get("task", {}).get("id")
            if not task_id:
                raise Exception("Task created but no ID returned")

            task_data_full = await orchestrator.get_task_by_id(task_id)
            if not task_data_full:
                raise Exception("Task created but not found")

            # Métricas
            metrics_collector.record_api_request(
                "graphql", "create_task", 201, time.time() - start_time
            )

            return Query()._convert_task_to_graphql(task_data_full)

        except Exception as e:
            metrics_collector.record_error("graphql", "mutation_create_task")
            raise

    @strawberry.mutation
    async def execute_task(self, info: Info, task_id: str) -> ExecutionResultType:
        """Executar tarefa"""
        start_time = time.time()

        try:
            orchestrator = info.context.get("orchestrator")
            if not orchestrator:
                raise Exception("Orchestrator not available")

            result = await orchestrator.execute_task(task_id)

            execution_time = time.time() - start_time

            # Métricas
            metrics_collector.record_api_request(
                "graphql", "execute_task", 200, execution_time
            )

            return ExecutionResultType(
                success=result.get("success", False),
                execution_time=result.get("execution_time", execution_time),
                message=result.get("message", ""),
                result_data=result.get("result"),
                error_message=result.get("error"),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            metrics_collector.record_error("graphql", "mutation_execute_task")
            raise

    @strawberry.mutation
    async def analyze_webpage(
        self,
        info: Info,
        input: AnalyzeWebpageInput
    ) -> strawberry.scalars.JSON:
        """Analisar página web"""
        start_time = time.time()

        try:
            orchestrator = info.context.get("orchestrator")
            if not orchestrator:
                raise Exception("Orchestrator not available")

            result = await orchestrator.analyze_webpage(input.url)

            # Métricas
            metrics_collector.record_api_request(
                "graphql", "analyze_webpage", 200, time.time() - start_time
            )

            return result

        except Exception as e:
            metrics_collector.record_error("graphql", "mutation_analyze_webpage")
            raise

    @strawberry.mutation
    async def process_ai_request(
        self,
        info: Info,
        input: AIRequestInput
    ) -> strawberry.scalars.JSON:
        """Processar requisição de IA"""
        start_time = time.time()

        try:
            from ...infrastructure.ai.multi_model_orchestrator import AIRequest

            ai_request = AIRequest(
                id=f"graphql_{int(time.time() * 1000000)}",
                model_config=ai_orchestrator.model_configs.get(input.model_id),
                prompt=input.prompt,
                input_data=input.input_data or {},
                priority=input.priority
            )

            if not ai_request.model_config:
                raise Exception(f"Model {input.model_id} not found")

            result = await ai_orchestrator.process_request_async(ai_request)

            # Métricas
            metrics_collector.record_api_request(
                "graphql", "process_ai_request", 200, time.time() - start_time
            )

            return {
                "request_id": result.request_id,
                "success": result.success,
                "content": result.content,
                "usage": result.usage,
                "cost": result.cost,
                "latency": result.latency,
                "error_message": result.error_message
            }

        except Exception as e:
            metrics_collector.record_error("graphql", "mutation_ai_request")
            raise


# ===== SCHEMA =====

schema = strawberry.Schema(query=Query, mutation=Mutation)


# ===== UTILITIES =====

import time  # Import necessário para métricas
