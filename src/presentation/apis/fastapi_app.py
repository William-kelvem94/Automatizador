#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASTAPI APPLICATION
API REST completa para o Automatizador IA
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ...application.services.automation_orchestrator import AutomationOrchestrator
from ...infrastructure.external_services.intelligence_service import IntelligenceService
from ...shared.utils.logger import get_logger


# ===== Pydantic Models =====

class TaskCreateRequest(BaseModel):
    """Modelo para criação de tarefa"""
    name: str = Field(..., description="Nome da tarefa")
    description: str = Field("", description="Descrição da tarefa")
    url: str = Field(..., description="URL do site")
    username: str = Field("", description="Nome de usuário")
    password: str = Field("", description="Senha")
    browser_config: Optional[Dict[str, Any]] = Field(None, description="Configuração do navegador")


class TaskResponse(BaseModel):
    """Modelo de resposta para tarefa"""
    id: str
    name: str
    description: str
    url: str
    status: str
    created_at: str
    success_rate: float


class ExecutionResponse(BaseModel):
    """Modelo de resposta para execução"""
    success: bool
    task_id: str
    message: str
    execution_time: float
    result: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Modelo de resposta para análise"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, str]] = None
    message: str


class HealthResponse(BaseModel):
    """Modelo de resposta para health check"""
    status: str
    services: Dict[str, str]
    timestamp: str
    version: str = "7.0.0"


# ===== FastAPI Application =====

app = FastAPI(
    title="Automator Web IA API",
    description="API REST para Automatizador Web IA v7.0",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = get_logger(__name__)

# Serviços (serão injetados)
orchestrator: Optional[AutomationOrchestrator] = None
intelligence: Optional[IntelligenceService] = None


def get_orchestrator() -> AutomationOrchestrator:
    """Dependency injection para orchestrator"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator não inicializado")
    return orchestrator


def get_intelligence() -> IntelligenceService:
    """Dependency injection para intelligence service"""
    if intelligence is None:
        raise HTTPException(status_code=503, detail="Intelligence service não inicializado")
    return intelligence


# ===== ROTAS =====

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Automator Web IA v7.0 API",
        "version": "7.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check da aplicação"""
    try:
        # Verifica serviços
        services_status = {}

        if orchestrator:
            health_data = await orchestrator.get_system_health()
            services_status["orchestrator"] = health_data.get("status", "unknown")
        else:
            services_status["orchestrator"] = "not_initialized"

        if intelligence:
            health_data = await intelligence.health_check()
            services_status["intelligence"] = health_data.get("status", "unknown")
        else:
            services_status["intelligence"] = "not_initialized"

        # Status geral
        overall_status = "healthy"
        if "unhealthy" in services_status.values() or "not_initialized" in services_status.values():
            overall_status = "degraded"
        if all(status in ["not_initialized", "unhealthy"] for status in services_status.values()):
            overall_status = "unhealthy"

        return HealthResponse(
            status=overall_status,
            services=services_status,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


# ===== TASKS ENDPOINTS =====

@app.post("/tasks", response_model=Dict[str, Any])
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Cria uma nova tarefa de automação"""
    try:
        logger.info(f"Criando tarefa: {request.name}")

        # Cria tarefa
        result = await orch.create_task(request.dict())

        if result["success"]:
            # Background: melhorar seletores com IA
            if intelligence and intelligence.is_ai_available():
                background_tasks.add_task(improve_task_selectors, result["task"]["id"], orch)

            return {
                "success": True,
                "task": result["task"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Lista tarefas de automação"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if limit:
            filters["limit"] = limit
        if offset:
            filters["offset"] = offset

        result = await orch.get_tasks(filters)

        if "tasks" in result:
            return result["tasks"]
        else:
            raise HTTPException(status_code=500, detail="Erro ao buscar tarefas")

    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Busca tarefa específica"""
    try:
        result = await orch.get_task_by_id(task_id)

        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar tarefa {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.post("/tasks/{task_id}/execute", response_model=ExecutionResponse)
async def execute_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Executa uma tarefa de automação"""
    try:
        logger.info(f"Executando tarefa: {task_id}")

        # Executa tarefa
        result = await orch.execute_task(task_id)

        if result["success"] is not None:  # Result pode ser None em caso de erro
            # Background: analisar resultado e sugerir melhorias
            background_tasks.add_task(analyze_execution_result, task_id, result, orch)

            return ExecutionResponse(
                success=result["success"],
                task_id=task_id,
                message=result.get("message", "Execução concluída"),
                execution_time=result.get("execution_time", 0.0),
                result=result.get("result")
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Erro na execução"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar tarefa {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Exclui uma tarefa"""
    try:
        # TODO: Implementar delete_task no orchestrator
        return {"message": f"Tarefa {task_id} excluída (simulado)"}

    except Exception as e:
        logger.error(f"Erro ao excluir tarefa {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


# ===== ANALYSIS ENDPOINTS =====

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_webpage(
    url: str,
    orch: AutomationOrchestrator = Depends(get_orchestrator)
):
    """Analisa uma página web"""
    try:
        if not url:
            raise HTTPException(status_code=400, detail="URL é obrigatória")

        logger.info(f"Analisando página: {url}")
        result = await orch.analyze_webpage(url)

        if result["success"]:
            return AnalysisResponse(
                success=True,
                analysis=result.get("analysis"),
                recommendations=result.get("recommendations"),
                message=result.get("message", "Análise concluída")
            )
        else:
            return AnalysisResponse(
                success=False,
                message=result.get("message", "Erro na análise")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise de {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.get("/analyze/test-connection")
async def test_connection(url: str, orch: AutomationOrchestrator = Depends(get_orchestrator)):
    """Testa conexão com um site"""
    try:
        result = await orch.test_connection(url)
        return result

    except Exception as e:
        logger.error(f"Erro no teste de conexão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


# ===== INTELLIGENCE ENDPOINTS =====

@app.post("/intelligence/generate-selector")
async def generate_smart_selector(
    description: str,
    context: str = "",
    intel: IntelligenceService = Depends(get_intelligence)
):
    """Gera seletor inteligente usando IA"""
    try:
        if not intel.is_ai_available():
            raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")

        selector = await intel.generate_selector(description, context)

        return {
            "success": True,
            "selector": selector,
            "description": description,
            "context": context
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar seletor: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.post("/intelligence/analyze-form")
async def analyze_form(
    form_html: str,
    intel: IntelligenceService = Depends(get_intelligence)
):
    """Analisa formulário usando IA"""
    try:
        if not intel.is_ai_available():
            raise HTTPException(status_code=503, detail="Serviços de IA não disponíveis")

        analysis = await intel.analyze_form_structure(form_html)

        return {
            "success": True,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise de formulário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.get("/intelligence/health")
async def intelligence_health(intel: IntelligenceService = Depends(get_intelligence)):
    """Verifica saúde dos serviços de IA"""
    try:
        health = await intel.health_check()
        return health

    except Exception as e:
        logger.error(f"Erro no health check da IA: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


# ===== BACKGROUND TASKS =====

async def improve_task_selectors(task_id: str, orch: AutomationOrchestrator):
    """Melhora seletores de uma tarefa usando IA (background)"""
    try:
        logger.info(f"Melhorando seletores da tarefa {task_id} em background")

        # Busca tarefa
        task_data = await orch.get_task_by_id(task_id)
        if not task_data or not task_data.get("url"):
            return

        # Usa análise para melhorar seletores
        analysis_result = await orch.analyze_webpage(task_data["url"])
        if analysis_result["success"]:
            recommendations = analysis_result.get("recommendations", {})

            # TODO: Atualizar tarefa com melhores seletores
            logger.info(f"Seletores melhorados para tarefa {task_id}: {recommendations}")

    except Exception as e:
        logger.error(f"Erro ao melhorar seletores da tarefa {task_id}: {e}")


async def analyze_execution_result(task_id: str, execution_result: Dict[str, Any], orch: AutomationOrchestrator):
    """Analisa resultado de execução e gera insights (background)"""
    try:
        logger.info(f"Analisando resultado da execução da tarefa {task_id}")

        # TODO: Implementar análise de padrões de falha/sucesso
        # TODO: Gerar sugestões de melhoria baseadas no histórico

        if execution_result.get("success"):
            logger.info(f"Execução da tarefa {task_id} foi bem-sucedida")
        else:
            logger.warning(f"Execução da tarefa {task_id} falhou: {execution_result.get('message', 'Erro desconhecido')}")

    except Exception as e:
        logger.error(f"Erro ao analisar resultado da tarefa {task_id}: {e}")


# ===== ERROR HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat()
        }
    )


# ===== LIFECYCLE =====

async def initialize_services():
    """Inicializa serviços da aplicação"""
    global orchestrator, intelligence

    try:
        logger.info("Inicializando serviços da API...")

        # TODO: Injetar configurações reais
        from ...infrastructure.persistence.sqlalchemy_task_repository import SQLAlchemyTaskRepository
        from ...infrastructure.external_services.playwright_automation_service import PlaywrightAutomationService

        # Inicializa serviços
        task_repo = SQLAlchemyTaskRepository()
        automation_service = PlaywrightAutomationService()

        # Inicializa serviços assíncronos
        await task_repo._ensure_initialized()
        await automation_service._ensure_initialized()

        # Cria orchestrator
        orchestrator = AutomationOrchestrator(
            task_repository=task_repo,
            automation_service=automation_service
        )

        # Inicializa inteligência (sem APIs por enquanto)
        intelligence = IntelligenceService()

        logger.info("Serviços da API inicializados com sucesso")

    except Exception as e:
        logger.error(f"Erro na inicialização dos serviços: {e}")
        # Continua sem serviços - endpoints retornarão 503


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação"""
    await initialize_services()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento da aplicação"""
    try:
        if intelligence:
            # Cleanup se necessário
            pass

        logger.info("API encerrada com sucesso")

    except Exception as e:
        logger.error(f"Erro no shutdown: {e}")


# ===== MAIN =====

if __name__ == "__main__":
    import uvicorn

    logger.info("Iniciando FastAPI server...")
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
