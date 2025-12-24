# -*- coding: utf-8 -*-

"""
GRAPHQL SERVER - Enterprise GraphQL API Server
Servidor GraphQL integrado com FastAPI e Strawberry
"""

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .graphql_schema import schema
from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector
from ...application.services.automation_orchestrator import AutomationOrchestrator


logger = get_logger(__name__)


class GraphQLContext:
    """Contexto GraphQL com dependências injetadas"""

    def __init__(self, orchestrator: Optional[AutomationOrchestrator] = None):
        self.orchestrator = orchestrator
        self.request_time = datetime.now()
        self.user_id = None
        self.session_id = None


def get_graphql_context(request: Request) -> GraphQLContext:
    """Factory para contexto GraphQL"""
    # Em produção, injetar orchestrator e outras dependências
    # Por enquanto, contexto básico
    context = GraphQLContext()

    # Extrair informações da requisição
    context.user_id = request.headers.get("X-User-ID")
    context.session_id = request.headers.get("X-Session-ID")

    return context


class EnterpriseGraphQLRouter(GraphQLRouter):
    """GraphQL Router com funcionalidades enterprise"""

    def __init__(self, schema: strawberry.Schema, **kwargs):
        super().__init__(schema, **kwargs)
        self.request_count = 0
        self.error_count = 0

    async def execute_graphql_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Any] = None,
        operation_name: Optional[str] = None,
    ) -> ExecutionResult:
        """Executar query GraphQL com monitoramento"""
        start_time = time.time()
        self.request_count += 1

        try:
            result = await super().execute_graphql_query(
                query=query,
                variables=variables,
                context=context,
                operation_name=operation_name
            )

            # Verificar erros
            if result.errors:
                self.error_count += 1
                for error in result.errors:
                    logger.warning(f"GraphQL Error: {error}")

            execution_time = time.time() - start_time

            # Métricas
            metrics_collector.observe_histogram(
                'automator_graphql_query_duration_seconds',
                execution_time
            )

            if result.errors:
                metrics_collector.record_error("graphql", "query_execution")
            else:
                metrics_collector.record_api_request(
                    "graphql", "query", 200, execution_time
                )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1

            logger.error(f"GraphQL execution failed: {e}")
            metrics_collector.record_error("graphql", "execution_failed")

            # Retornar erro GraphQL
            return ExecutionResult(
                data=None,
                errors=[{
                    "message": "Internal server error",
                    "locations": [],
                    "path": []
                }]
            )


def create_graphql_app(orchestrator: Optional[AutomationOrchestrator] = None) -> FastAPI:
    """Criar aplicação FastAPI com GraphQL"""

    app = FastAPI(
        title="Automator Web IA - GraphQL API",
        description="Enterprise GraphQL API for Web Automation",
        version="8.0.0",
        docs_url="/graphql/docs",
        redoc_url="/graphql/redoc"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar origens
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"GraphQL API: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        return response

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check da API GraphQL"""
        return {
            "status": "healthy",
            "service": "graphql-api",
            "version": "8.0.0",
            "timestamp": datetime.now().isoformat()
        }

    # Métricas Prometheus
    @app.get("/metrics")
    async def get_metrics():
        """Expor métricas Prometheus"""
        return Response(
            content=metrics_collector.get_metrics_text(),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )

    # Schema GraphQL
    @app.get("/schema")
    async def get_graphql_schema():
        """Obter schema GraphQL em SDL"""
        sdl = schema.as_str()
        return Response(content=sdl, media_type="text/plain")

    # Playground GraphQL
    @app.get("/playground")
    async def graphql_playground():
        """GraphQL Playground interface"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Automator Web IA - GraphQL Playground</title>
            <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
            <link rel="shortcut icon" href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
            <script src="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
        </head>
        <body>
            <div id="root"></div>
            <script>
                window.addEventListener('load', function (event) {
                    GraphQLPlayground.init(document.getElementById('root'), {
                        endpoint: '/graphql',
                        settings: {
                            'editor.theme': 'dark',
                            'request.credentials': 'same-origin'
                        }
                    })
                })
            </script>
        </body>
        </html>
        """
        return Response(content=html, media_type="text/html")

    # GraphQL Router
    graphql_router = EnterpriseGraphQLRouter(
        schema,
        context_getter=get_graphql_context,
        graphiql=True
    )

    app.include_router(graphql_router, prefix="/graphql")

    # Middleware de autenticação (simplificado)
    @app.middleware("http")
    async def authenticate_request(request: Request, call_next):
        # Em produção, implementar autenticação JWT/OAuth
        # Por enquanto, permitir tudo
        response = await call_next(request)
        return response

    # Error handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        metrics_collector.record_error("graphql_api", "unhandled_exception")

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }
        )

    logger.info("✅ GraphQL API criada com sucesso")
    return app


# Função para executar servidor GraphQL standalone
def run_graphql_server(host: str = "0.0.0.0", port: int = 8002):
    """Executar servidor GraphQL standalone"""
    import uvicorn

    app = create_graphql_app()

    logger.info(f"🚀 Iniciando GraphQL server em http://{host}:{port}")
    logger.info(f"📊 GraphQL Playground: http://{host}:{port}/playground")
    logger.info(f"📖 GraphQL Docs: http://{host}:{port}/graphql/docs")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )


# Exemplo de queries GraphQL
GRAPHQL_EXAMPLES = {
    "get_tasks": """
    query GetTasks {
      tasks(limit: 10) {
        id
        name
        status
        metrics {
          successRate
          executionCount
          averageExecutionTime
        }
      }
    }
    """,

    "create_task": """
    mutation CreateTask($input: CreateTaskInput!) {
      createTask(input: $input) {
        id
        name
        status
        createdAt
      }
    }
    """,

    "execute_task": """
    mutation ExecuteTask($taskId: String!) {
      executeTask(taskId: $taskId) {
        success
        executionTime
        message
        resultData
      }
    }
    """,

    "system_health": """
    query SystemHealth {
      systemHealth {
        status
        services
        metrics
        timestamp
      }
    }
    """,

    "ai_models": """
    query AIModels {
      aiModels {
        id
        modelType
        provider
        modelName
        capabilities
        status
        usageStats
      }
    }
    """
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Automator Web IA - GraphQL API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind server')
    parser.add_argument('--port', type=int, default=8002, help='Port to bind server')

    args = parser.parse_args()
    run_graphql_server(args.host, args.port)
