# -*- coding: utf-8 -*-

"""
MULTI-MODEL AI ORCHESTRATOR
Sistema avançado de orchestration para múltiplos modelos de IA
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import threading
import queue

from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector


class AIModelType(Enum):
    """Tipos de modelos de IA disponíveis"""
    GPT4_VISION = "gpt4_vision"
    CLAUDE3 = "claude3"
    HUGGINGFACE_TRANSFORMER = "huggingface_transformer"
    CUSTOM_ML_MODEL = "custom_ml_model"
    COMPUTER_VISION = "computer_vision"
    SPEECH_RECOGNITION = "speech_recognition"


class AIProvider(Enum):
    """Provedores de IA suportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    CUSTOM = "custom"


@dataclass
class AIModelConfig:
    """Configuração de um modelo de IA"""
    model_type: AIModelType
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: float = 30.0
    retry_attempts: int = 3
    cost_per_token: float = 0.0
    rate_limit_per_minute: int = 60
    capabilities: List[str] = field(default_factory=list)


@dataclass
class AIRequest:
    """Requisição de IA"""
    id: str
    model_config: AIModelConfig
    prompt: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-10, higher = more priority
    timeout: Optional[float] = None
    callback: Optional[Callable] = None


@dataclass
class AIResponse:
    """Resposta de IA"""
    request_id: str
    success: bool
    content: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    latency: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiModelOrchestrator:
    """Orchestrator multi-model para IA enterprise"""

    def __init__(self):
        self.logger = get_logger(__name__)

        # Configurações de modelos
        self.model_configs: Dict[str, AIModelConfig] = {}
        self.active_models: Dict[str, Any] = {}

        # Controle de rate limiting
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}

        # Queue de processamento
        self.request_queue = queue.PriorityQueue()
        self.response_queue = queue.Queue()

        # Controle de threading
        self.is_running = False
        self.worker_threads: List[threading.Thread] = []
        self.num_workers = 4

        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_cost': 0.0,
            'average_latency': 0.0,
            'model_usage': {}
        }

        # Cache de modelos carregados
        self.model_cache: Dict[str, Any] = {}

        self.logger.info("MultiModelOrchestrator inicializado")

    def register_model(self, model_id: str, config: AIModelConfig):
        """Registrar um modelo de IA"""
        try:
            self.model_configs[model_id] = config

            # Inicializar rate limiter
            self.rate_limiters[model_id] = {
                'requests_this_minute': 0,
                'minute_start': time.time(),
                'lock': threading.Lock()
            }

            # Inicializar estatísticas
            self.stats['model_usage'][model_id] = {
                'requests': 0,
                'successful': 0,
                'failed': 0,
                'total_cost': 0.0,
                'total_latency': 0.0
            }

            self.logger.info(f"Modelo registrado: {model_id} ({config.model_type.value})")

        except Exception as e:
            self.logger.error(f"Erro ao registrar modelo {model_id}: {e}")

    def start_orchestrator(self):
        """Iniciar orchestrator"""
        if self.is_running:
            self.logger.warning("Orchestrator já está rodando")
            return

        self.is_running = True

        # Iniciar threads worker
        for i in range(self.num_workers):
            thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"AI-Worker-{i+1}"
            )
            thread.start()
            self.worker_threads.append(thread)

        # Iniciar thread de processamento de respostas
        response_thread = threading.Thread(
            target=self._response_processor_loop,
            daemon=True,
            name="Response-Processor"
        )
        response_thread.start()
        self.worker_threads.append(response_thread)

        self.logger.info(f"✅ Orchestrator iniciado com {self.num_workers} workers")

    def stop_orchestrator(self):
        """Parar orchestrator"""
        if not self.is_running:
            return

        self.is_running = False

        # Aguardar threads terminarem
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)

        self.worker_threads.clear()
        self.logger.info("✅ Orchestrator parado")

    async def process_request_async(self, request: AIRequest) -> AIResponse:
        """Processar requisição de IA de forma assíncrona"""
        if not self.is_running:
            return AIResponse(
                request_id=request.id,
                success=False,
                error_message="Orchestrator não está rodando"
            )

        # Verificar rate limiting
        if not self._check_rate_limit(request.model_config):
            return AIResponse(
                request_id=request.id,
                success=False,
                error_message="Rate limit excedido"
            )

        # Adicionar à fila
        self.request_queue.put((request.priority, time.time(), request))

        # Aguardar resposta (implementação simplificada)
        # Em produção, usaria asyncio.Queue ou similar
        start_time = time.time()
        while time.time() - start_time < (request.timeout or 60.0):
            try:
                response_request_id, response = self.response_queue.get_nowait()
                if response_request_id == request.id:
                    return response
            except queue.Empty:
                await asyncio.sleep(0.1)

        return AIResponse(
            request_id=request.id,
            success=False,
            error_message="Timeout aguardando resposta"
        )

    def _worker_loop(self):
        """Loop principal dos workers"""
        while self.is_running:
            try:
                # Obter próxima requisição
                priority, timestamp, request = self.request_queue.get(timeout=1.0)

                # Processar requisição
                response = self._process_ai_request(request)

                # Colocar resposta na fila
                self.response_queue.put((request.id, response))

                self.request_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Erro no worker loop: {e}")

    def _process_ai_request(self, request: AIRequest) -> AIResponse:
        """Processar uma requisição de IA"""
        start_time = time.time()

        try:
            self.stats['total_requests'] += 1

            # Selecionar e executar modelo
            model_response = self._execute_model(request)

            latency = time.time() - start_time

            # Calcular custo
            cost = self._calculate_cost(request.model_config, model_response.get('usage', {}))

            # Atualizar estatísticas
            model_id = f"{request.model_config.provider.value}_{request.model_config.model_name}"
            self._update_stats(model_id, model_response['success'], cost, latency)

            # Métricas Prometheus
            if model_response['success']:
                metrics_collector.record_external_service_call(
                    'ai_model',
                    True,
                    latency
                )
            else:
                metrics_collector.record_error('ai_model', 'ai_request_failed')

            return AIResponse(
                request_id=request.id,
                success=model_response['success'],
                content=model_response.get('content', ''),
                usage=model_response.get('usage', {}),
                cost=cost,
                latency=latency,
                metadata=model_response.get('metadata', {})
            )

        except Exception as e:
            latency = time.time() - start_time
            self.logger.error(f"Erro ao processar requisição {request.id}: {e}")

            return AIResponse(
                request_id=request.id,
                success=False,
                error_message=str(e),
                latency=latency
            )

    def _execute_model(self, request: AIRequest) -> Dict[str, Any]:
        """Executar modelo de IA"""
        config = request.model_config

        try:
            if config.model_type == AIModelType.GPT4_VISION:
                return self._execute_gpt4_vision(request)
            elif config.model_type == AIModelType.CLAUDE3:
                return self._execute_claude3(request)
            elif config.model_type == AIModelType.HUGGINGFACE_TRANSFORMER:
                return self._execute_huggingface(request)
            elif config.model_type == AIModelType.COMPUTER_VISION:
                return self._execute_computer_vision(request)
            else:
                return {
                    'success': False,
                    'error': f'Tipo de modelo não suportado: {config.model_type}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_gpt4_vision(self, request: AIRequest) -> Dict[str, Any]:
        """Executar GPT-4 Vision"""
        try:
            import openai

            client = openai.AsyncOpenAI(api_key=request.model_config.api_key)

            messages = [{"role": "user", "content": request.prompt}]

            # Adicionar imagem se fornecida
            if 'image_url' in request.input_data:
                messages[0]['content'] = [
                    {"type": "text", "text": request.prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": request.input_data['image_url']}
                    }
                ]

            response = asyncio.run(client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=request.model_config.max_tokens,
                temperature=request.model_config.temperature
            ))

            content = response.choices[0].message.content
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }

            return {
                'success': True,
                'content': content,
                'usage': usage,
                'metadata': {'model': 'gpt-4-vision-preview'}
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_claude3(self, request: AIRequest) -> Dict[str, Any]:
        """Executar Claude 3"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=request.model_config.api_key)

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=request.model_config.max_tokens,
                temperature=request.model_config.temperature,
                messages=[{"role": "user", "content": request.prompt}]
            )

            content = response.content[0].text
            usage = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }

            return {
                'success': True,
                'content': content,
                'usage': usage,
                'metadata': {'model': 'claude-3-sonnet'}
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_huggingface(self, request: AIRequest) -> Dict[str, Any]:
        """Executar modelo HuggingFace"""
        try:
            from transformers import pipeline

            # Cache de modelos
            model_key = f"hf_{request.model_config.model_name}"
            if model_key not in self.model_cache:
                self.model_cache[model_key] = pipeline(
                    "text-generation",
                    model=request.model_config.model_name,
                    device_map="auto"
                )

            pipe = self.model_cache[model_key]

            outputs = pipe(
                request.prompt,
                max_length=request.model_config.max_tokens,
                temperature=request.model_config.temperature,
                do_sample=True,
                pad_token_id=50256
            )

            content = outputs[0]['generated_text']
            usage = {'estimated_tokens': len(content.split())}

            return {
                'success': True,
                'content': content,
                'usage': usage,
                'metadata': {'model': request.model_config.model_name}
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_computer_vision(self, request: AIRequest) -> Dict[str, Any]:
        """Executar análise de computer vision"""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            import requests

            # Carregar imagem
            if 'image_url' in request.input_data:
                response = requests.get(request.input_data['image_url'])
                image = Image.open(io.BytesIO(response.content))
            elif 'image_path' in request.input_data:
                image = Image.open(request.input_data['image_path'])
            else:
                return {'success': False, 'error': 'Nenhuma imagem fornecida'}

            # Converter para OpenCV
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Análise básica (em produção usaria modelos mais avançados)
            height, width = opencv_image.shape[:2]

            # Detectar objetos (implementação simplificada)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            analysis = {
                'dimensions': f"{width}x{height}",
                'objects_detected': len(contours),
                'image_format': image.format,
                'color_mode': image.mode
            }

            return {
                'success': True,
                'content': json.dumps(analysis, indent=2),
                'usage': {'processing_time': 0.1},
                'metadata': {'analysis_type': 'basic_cv'}
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _check_rate_limit(self, config: AIModelConfig) -> bool:
        """Verificar rate limiting"""
        model_id = f"{config.provider.value}_{config.model_name}"
        limiter = self.rate_limiters.get(model_id)

        if not limiter:
            return True

        with limiter['lock']:
            current_time = time.time()
            minute_elapsed = current_time - limiter['minute_start']

            # Reset counter se passou 1 minuto
            if minute_elapsed >= 60:
                limiter['requests_this_minute'] = 0
                limiter['minute_start'] = current_time

            # Verificar limite
            if limiter['requests_this_minute'] >= config.rate_limit_per_minute:
                return False

            limiter['requests_this_minute'] += 1
            return True

    def _calculate_cost(self, config: AIModelConfig, usage: Dict[str, Any]) -> float:
        """Calcular custo da requisição"""
        total_tokens = usage.get('total_tokens', 0)
        return total_tokens * config.cost_per_token

    def _update_stats(self, model_id: str, success: bool, cost: float, latency: float):
        """Atualizar estatísticas"""
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1

        self.stats['total_cost'] += cost

        # Atualizar média de latência
        total_requests = self.stats['successful_requests'] + self.stats['failed_requests']
        if total_requests == 1:
            self.stats['average_latency'] = latency
        else:
            self.stats['average_latency'] = (
                (self.stats['average_latency'] * (total_requests - 1)) + latency
            ) / total_requests

        # Estatísticas por modelo
        if model_id not in self.stats['model_usage']:
            self.stats['model_usage'][model_id] = {
                'requests': 0, 'successful': 0, 'failed': 0,
                'total_cost': 0.0, 'total_latency': 0.0
            }

        model_stats = self.stats['model_usage'][model_id]
        model_stats['requests'] += 1
        if success:
            model_stats['successful'] += 1
        else:
            model_stats['failed'] += 1
        model_stats['total_cost'] += cost
        model_stats['total_latency'] += latency

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do orchestrator"""
        return dict(self.stats)

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do orchestrator"""
        try:
            stats = self.get_stats()

            return {
                'status': 'healthy' if self.is_running else 'stopped',
                'models_registered': len(self.model_configs),
                'active_workers': len([t for t in self.worker_threads if t.is_alive()]),
                'queue_size': self.request_queue.qsize(),
                'stats': stats
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Instância global
ai_orchestrator = MultiModelOrchestrator()


# Funções utilitárias
def register_ai_model(model_id: str, config: AIModelConfig):
    """Registrar modelo de IA globalmente"""
    ai_orchestrator.register_model(model_id, config)


def start_ai_orchestrator():
    """Iniciar orchestrator global"""
    ai_orchestrator.start_orchestrator()


def stop_ai_orchestrator():
    """Parar orchestrator global"""
    ai_orchestrator.stop_orchestrator()


async def process_ai_request(request: AIRequest) -> AIResponse:
    """Processar requisição de IA"""
    return await ai_orchestrator.process_request_async(request)
