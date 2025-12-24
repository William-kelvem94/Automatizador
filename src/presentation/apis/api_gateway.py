# -*- coding: utf-8 -*-

"""
API GATEWAY - Enterprise API Gateway
Gateway unificado para múltiplas APIs (REST, GraphQL, WebSockets)
"""

import asyncio
import httpx
import json
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector
from ...infrastructure.security.rbac import rbac_manager, AccessRequest, Permission


logger = get_logger(__name__)


class APIEndpoint:
    """Configuração de endpoint da API"""

    def __init__(self,
                 path: str,
                 target_url: str,
                 methods: List[str] = None,
                 auth_required: bool = True,
                 permissions: List[Permission] = None,
                 rate_limit: Optional[Dict[str, Any]] = None,
                 cache_enabled: bool = False):
        self.path = path
        self.target_url = target_url
        self.methods = methods or ["GET", "POST", "PUT", "DELETE"]
        self.auth_required = auth_required
        self.permissions = permissions or []
        self.rate_limit = rate_limit
        self.cache_enabled = cache_enabled


class APIGateway:
    """API Gateway enterprise"""

    def __init__(self):
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.app = self._create_app()
        self.client = httpx.AsyncClient(timeout=30.0)

        # Rate limiting (simplificado)
        self.rate_limits: Dict[str, Dict[str, Any]] = {}

        logger.info("API Gateway inicializado")

    def _create_app(self) -> FastAPI:
        """Criar aplicação FastAPI do gateway"""

        app = FastAPI(
            title="Automator Web IA - API Gateway",
            description="Enterprise API Gateway for unified access",
            version="8.0.0"
        )

        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Middleware de logging e métricas
        @app.middleware("http")
        async def gateway_middleware(request: Request, call_next):
            start_time = time.time()

            # Log da requisição
            logger.info(f"Gateway: {request.method} {request.url.path}")

            # Verificar rate limiting
            client_ip = self._get_client_ip(request)
            if not self._check_rate_limit(client_ip, request.url.path):
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"}
                )

            # Verificar autenticação/autorização
            if not await self._authenticate_request(request):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Authentication required"}
                )

            # Processar requisição
            response = await call_next(request)

            # Métricas
            duration = time.time() - start_time
            metrics_collector.record_api_request(
                "gateway", request.url.path, response.status_code, duration
            )

            return response

        # Route genérica para proxy
        @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        async def proxy_request(request: Request, path: str):
            return await self._proxy_request(request, path)

        # Health check
        @app.get("/health")
        async def health():
            return await self._health_check()

        # Métricas
        @app.get("/metrics")
        async def metrics():
            return Response(
                content=metrics_collector.get_metrics_text(),
                media_type="text/plain"
            )

        # Routes específicas da API
        @app.get("/api/v1/tasks")
        async def get_tasks():
            """Proxy para API REST de tarefas"""
            return await self._proxy_to_service("rest-api", "/tasks", "GET")

        @app.post("/api/v1/tasks")
        async def create_task():
            """Proxy para criação de tarefa"""
            return await self._proxy_to_service("rest-api", "/tasks", "POST")

        @app.post("/api/v1/tasks/{task_id}/execute")
        async def execute_task(task_id: str):
            """Proxy para execução de tarefa"""
            return await self._proxy_to_service("rest-api", f"/tasks/{task_id}/execute", "POST")

        @app.post("/api/v1/analyze")
        async def analyze_webpage():
            """Proxy para análise de página"""
            return await self._proxy_to_service("rest-api", "/analyze", "POST")

        return app

    def register_endpoint(self, endpoint: APIEndpoint):
        """Registrar endpoint no gateway"""
        self.endpoints[endpoint.path] = endpoint
        logger.info(f"Endpoint registrado: {endpoint.path} -> {endpoint.target_url}")

    def register_service(self, name: str, base_url: str, endpoints: List[Dict[str, Any]]):
        """Registrar serviço completo"""
        for endpoint_config in endpoints:
            endpoint = APIEndpoint(
                path=endpoint_config['path'],
                target_url=f"{base_url}{endpoint_config['path']}",
                methods=endpoint_config.get('methods', ['GET']),
                auth_required=endpoint_config.get('auth_required', True),
                permissions=endpoint_config.get('permissions', []),
                rate_limit=endpoint_config.get('rate_limit'),
                cache_enabled=endpoint_config.get('cache_enabled', False)
            )
            self.register_endpoint(endpoint)

        logger.info(f"Serviço registrado: {name} ({len(endpoints)} endpoints)")

    async def _proxy_request(self, request: Request, path: str) -> Response:
        """Proxy genérico para requisições"""
        # Encontrar endpoint correspondente
        endpoint = self._find_endpoint(path, request.method)
        if not endpoint:
            raise HTTPException(status_code=404, detail="Endpoint not found")

        # Construir URL de destino
        target_url = self._build_target_url(endpoint, request)

        try:
            # Preparar requisição
            headers = self._prepare_headers(request, endpoint)
            body = await self._get_request_body(request)

            # Fazer requisição
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )

            # Retornar resposta
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get('content-type')
            )

        except httpx.RequestError as e:
            logger.error(f"Gateway proxy error: {e}")
            raise HTTPException(status_code=502, detail="Service unavailable")

    async def _proxy_to_service(self, service_name: str, path: str, method: str) -> Response:
        """Proxy para serviço específico"""
        # Mapeamento de serviços (em produção, seria configurável)
        service_urls = {
            "rest-api": "http://automator-webia:8000",
            "graphql-api": "http://automator-webia:8002",
            "websocket-api": "ws://automator-webia:8001"
        }

        if service_name not in service_urls:
            raise HTTPException(status_code=404, detail="Service not found")

        target_url = f"{service_urls[service_name]}{path}"

        try:
            response = await self.client.request(method, target_url)
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

        except httpx.RequestError as e:
            logger.error(f"Service proxy error for {service_name}: {e}")
            raise HTTPException(status_code=502, detail="Service unavailable")

    def _find_endpoint(self, path: str, method: str) -> Optional[APIEndpoint]:
        """Encontrar endpoint correspondente"""
        # Verificar match exato primeiro
        if path in self.endpoints:
            endpoint = self.endpoints[path]
            if method in endpoint.methods:
                return endpoint

        # Verificar patterns (simplificado)
        for endpoint_path, endpoint in self.endpoints.items():
            if self._path_matches(endpoint_path, path) and method in endpoint.methods:
                return endpoint

        return None

    def _path_matches(self, pattern: str, path: str) -> bool:
        """Verificar se path corresponde ao pattern"""
        # Conversão simples de {param} para regex
        regex_pattern = re.sub(r'{[^}]+}', r'[^/]+', pattern)
        return bool(re.match(f"^{regex_pattern}$", path))

    def _build_target_url(self, endpoint: APIEndpoint, request: Request) -> str:
        """Construir URL de destino"""
        target_url = endpoint.target_url

        # Substituir parâmetros de path
        path_params = request.path_params
        for param, value in path_params.items():
            target_url = target_url.replace(f"{{{param}}}", str(value))

        return target_url

    def _prepare_headers(self, request: Request, endpoint: APIEndpoint) -> Dict[str, str]:
        """Preparar headers para requisição proxied"""
        headers = {}

        # Copiar headers relevantes
        headers_to_copy = [
            'content-type',
            'authorization',
            'x-user-id',
            'x-session-id',
            'x-request-id'
        ]

        for header_name in headers_to_copy:
            header_value = request.headers.get(header_name)
            if header_value:
                headers[header_name] = header_value

        # Adicionar headers do gateway
        headers['x-gateway'] = 'automator-webia'
        headers['x-forwarded-for'] = self._get_client_ip(request)
        headers['x-forwarded-host'] = request.headers.get('host', '')
        headers['x-forwarded-proto'] = request.headers.get('x-forwarded-proto', 'http')

        return headers

    async def _get_request_body(self, request: Request) -> Optional[bytes]:
        """Obter corpo da requisição"""
        try:
            return await request.body()
        except Exception:
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Obter IP do cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        # Fallback para remote address
        return request.client.host if request.client else 'unknown'

    def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """Verificar rate limiting (simplificado)"""
        # Implementação básica - em produção usaria Redis
        key = f"{client_ip}:{path}"
        current_time = time.time()

        if key not in self.rate_limits:
            self.rate_limits[key] = {'count': 0, 'window_start': current_time}

        limit_data = self.rate_limits[key]

        # Reset window se passou 1 minuto
        if current_time - limit_data['window_start'] > 60:
            limit_data['count'] = 0
            limit_data['window_start'] = current_time

        # Verificar limite (100 requests por minuto)
        if limit_data['count'] >= 100:
            return False

        limit_data['count'] += 1
        return True

    async def _authenticate_request(self, request: Request) -> bool:
        """Autenticar requisição"""
        # Verificar se endpoint requer autenticação
        endpoint = self._find_endpoint(request.url.path, request.method)
        if endpoint and not endpoint.auth_required:
            return True

        # Verificar token de autenticação
        auth_header = request.headers.get('authorization', '')
        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header[7:]  # Remover 'Bearer '

        # Validar token (simplificado - em produção usaria JWT)
        if not self._validate_token(token):
            return False

        # Extrair user ID do token
        user_id = self._extract_user_from_token(token)
        if not user_id:
            return False

        # Verificar permissões se especificadas
        if endpoint and endpoint.permissions:
            user = rbac_manager.get_user(user_id)
            if not user:
                return False

            access_request = AccessRequest(
                user=user,
                resource=endpoint.path,
                action=request.method.lower(),
                context={'gateway': True}
            )

            return rbac_manager.check_access(access_request)

        return True

    def _validate_token(self, token: str) -> bool:
        """Validar token de autenticação (simplificado)"""
        # Em produção, validar JWT ou API key
        return len(token) > 10  # Validação básica

    def _extract_user_from_token(self, token: str) -> Optional[str]:
        """Extrair user ID do token (simplificado)"""
        # Em produção, decodificar JWT
        return "user_123"  # Mock

    async def _health_check(self) -> Dict[str, Any]:
        """Health check do gateway"""
        try:
            # Testar conectividade com serviços
            services_status = {}

            # Testar REST API
            try:
                response = await self.client.get("http://automator-webia:8000/health", timeout=5.0)
                services_status['rest-api'] = 'healthy' if response.status_code == 200 else 'unhealthy'
            except Exception:
                services_status['rest-api'] = 'unreachable'

            # Testar GraphQL API
            try:
                response = await self.client.get("http://automator-webia:8002/health", timeout=5.0)
                services_status['graphql-api'] = 'healthy' if response.status_code == 200 else 'unhealthy'
            except Exception:
                services_status['graphql-api'] = 'unreachable'

            overall_status = 'healthy' if all(s == 'healthy' for s in services_status.values()) else 'degraded'

            return {
                'status': overall_status,
                'service': 'api-gateway',
                'version': '8.0.0',
                'services': services_status,
                'endpoints_registered': len(self.endpoints),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Gateway health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def close(self):
        """Fechar gateway"""
        await self.client.aclose()
        logger.info("API Gateway fechado")


# Instância global
api_gateway = APIGateway()


# Configuração padrão de serviços
DEFAULT_SERVICES = {
    "rest-api": {
        "base_url": "http://automator-webia:8000",
        "endpoints": [
            {
                "path": "/tasks",
                "methods": ["GET", "POST"],
                "permissions": [Permission.TASK_READ, Permission.TASK_CREATE]
            },
            {
                "path": "/tasks/{task_id}",
                "methods": ["GET", "PUT", "DELETE"],
                "permissions": [Permission.TASK_READ, Permission.TASK_UPDATE, Permission.TASK_DELETE]
            },
            {
                "path": "/tasks/{task_id}/execute",
                "methods": ["POST"],
                "permissions": [Permission.TASK_EXECUTE]
            },
            {
                "path": "/analyze",
                "methods": ["POST"],
                "permissions": [Permission.TASK_READ]
            }
        ]
    },
    "graphql-api": {
        "base_url": "http://automator-webia:8002",
        "endpoints": [
            {
                "path": "/graphql",
                "methods": ["GET", "POST"],
                "permissions": [Permission.API_ACCESS]
            }
        ]
    }
}


def configure_gateway():
    """Configurar gateway com serviços padrão"""
    for service_name, service_config in DEFAULT_SERVICES.items():
        api_gateway.register_service(
            service_name,
            service_config["base_url"],
            service_config["endpoints"]
        )


def run_gateway_server(host: str = "0.0.0.0", port: int = 8003):
    """Executar servidor do API Gateway"""
    import uvicorn

    configure_gateway()

    logger.info(f"🚀 Iniciando API Gateway em http://{host}:{port}")

    uvicorn.run(
        api_gateway.app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Automator Web IA - API Gateway')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind gateway')
    parser.add_argument('--port', type=int, default=8003, help='Port to bind gateway')

    args = parser.parse_args()
    run_gateway_server(args.host, args.port)
