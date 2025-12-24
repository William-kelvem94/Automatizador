# -*- coding: utf-8 -*-

"""
CONFIGURAÇÕES GLOBAIS DE TESTE
Fixtures e configurações compartilhadas para todos os testes
"""

import os
import sys
import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

# Adiciona src ao path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"

for path in [str(project_root), str(src_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Configurações de ambiente para testes
os.environ['AUTOMATOR_ENV'] = 'testing'
os.environ['AUTOMATOR_VERSION'] = '8.0.0-test'
os.environ['LOGURU_LEVEL'] = 'WARNING'  # Reduz logs durante testes

# Imports da aplicação
from src.shared.utils.logger import get_logger

# Logger para testes
test_logger = get_logger(__name__)


# ===== FIXTURES BÁSICAS =====

@pytest.fixture(scope="session")
def event_loop():
    """Evento loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir():
    """Diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_config():
    """Configuração base para testes"""
    return {
        'version': '8.0.0-test',
        'environment': 'testing',
        'database_url': 'sqlite:///:memory:',
        'redis_url': None,  # Mocked
        'log_level': 'WARNING',
        'debug': False,
        'max_concurrent_tasks': 2,
        'browser_timeout': 10000,  # Reduzido para testes
        'cache_enabled': False,  # Desabilitado para testes
    }


# ===== FIXTURES DE MOCK =====

@pytest.fixture
def mock_cache():
    """Mock do serviço de cache"""
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.exists = AsyncMock(return_value=False)
    cache.clear = AsyncMock(return_value=True)
    cache.health_check = AsyncMock(return_value={'status': 'healthy'})
    return cache


@pytest.fixture
def mock_event_bus():
    """Mock do event bus"""
    bus = MagicMock()
    bus.publish = AsyncMock(return_value=None)
    bus.subscribe = AsyncMock(return_value=None)
    bus.start = AsyncMock(return_value=None)
    bus.stop = AsyncMock(return_value=None)
    bus.is_running = MagicMock(return_value=True)
    bus.health_check = AsyncMock(return_value={'status': 'healthy'})
    return bus


@pytest.fixture
def mock_intelligence_service():
    """Mock do serviço de inteligência"""
    intelligence = MagicMock()
    intelligence.generate_selector = AsyncMock(return_value='input[name="test"]')
    intelligence.analyze_form_structure = AsyncMock(return_value={
        'username_fields': ['input[name="username"]'],
        'password_fields': ['input[name="password"]'],
        'submit_buttons': ['button[type="submit"]'],
        'confidence': 0.9
    })
    intelligence.predict_execution_success = AsyncMock(return_value=0.8)
    intelligence.is_ai_available = MagicMock(return_value=False)
    intelligence.health_check = AsyncMock(return_value={'status': 'healthy'})
    return intelligence


@pytest.fixture
def mock_automation_service():
    """Mock do serviço de automação"""
    service = MagicMock()
    service.analyze_page = AsyncMock(return_value={
        'success': True,
        'analysis': {'forms_count': 1, 'inputs_count': 2},
        'recommendations': {'username': 'input[name="user"]'}
    })
    service.validate_selectors = AsyncMock(return_value={
        'selectors': {'test': {'found': 1, 'visible': 1, 'valid': True}}
    })
    service.test_connection = AsyncMock(return_value={
        'success': True,
        'response_time': 0.5
    })
    return service


# ===== FIXTURES DE BANCO DE DADOS =====

@pytest.fixture
def mock_repository():
    """Mock de repositório"""
    repo = MagicMock()
    repo.create = AsyncMock(return_value={'id': 'test-id', 'success': True})
    repo.get_by_id = AsyncMock(return_value={'id': 'test-id', 'name': 'Test Task'})
    repo.update = AsyncMock(return_value=True)
    repo.delete = AsyncMock(return_value=True)
    repo.list = AsyncMock(return_value=[{'id': 'test-id', 'name': 'Test Task'}])
    return repo


# ===== FIXTURES DE APLICAÇÃO =====

@pytest.fixture
async def mock_orchestrator(mock_repository, mock_automation_service, mock_intelligence_service):
    """Mock do orchestrator"""
    from src.application.services.automation_orchestrator import AutomationOrchestrator

    orchestrator = MagicMock(spec=AutomationOrchestrator)
    orchestrator.task_repository = mock_repository
    orchestrator.automation_service = mock_automation_service

    # Métodos mockados
    orchestrator.create_task = AsyncMock(return_value={
        'success': True,
        'task': {'id': 'test-task-id', 'name': 'Test Task'}
    })
    orchestrator.get_task_by_id = AsyncMock(return_value={
        'id': 'test-task-id', 'name': 'Test Task', 'status': 'pending'
    })
    orchestrator.execute_task = AsyncMock(return_value={
        'success': True,
        'execution_time': 1.5,
        'message': 'Task executed successfully'
    })
    orchestrator.analyze_webpage = AsyncMock(return_value={
        'success': True,
        'analysis': {'url': 'https://example.com'},
        'recommendations': {}
    })
    orchestrator.get_system_health = AsyncMock(return_value={
        'status': 'healthy',
        'services': {'orchestrator': 'healthy'}
    })

    return orchestrator


# ===== FIXTURES DE ENTIDADES =====

@pytest.fixture
def sample_task_data():
    """Dados de exemplo para uma tarefa"""
    return {
        'id': 'test-task-123',
        'name': 'Test Automation Task',
        'description': 'A test automation task',
        'url': 'https://example.com/login',
        'username': 'testuser',
        'password': 'testpass123',
        'username_selector': 'input[name="username"]',
        'password_selector': 'input[name="password"]',
        'submit_selector': 'button[type="submit"]',
        'status': 'pending',
        'created_at': '2025-01-15T10:00:00Z',
        'max_retries': 3,
        'timeout': 30000,
        'browser_config': {
            'headless': True,
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'viewport': {'width': 1280, 'height': 720}
        }
    }


@pytest.fixture
def sample_workflow_data():
    """Dados de exemplo para um workflow"""
    return {
        'id': 'test-workflow-123',
        'name': 'Test Workflow',
        'description': 'A test automation workflow',
        'steps': [
            {
                'id': 'step-1',
                'action_type': 'type',
                'selector': 'input[name="username"]',
                'value': 'testuser',
                'order': 1
            },
            {
                'id': 'step-2',
                'action_type': 'type',
                'selector': 'input[name="password"]',
                'value': 'testpass123',
                'order': 2
            },
            {
                'id': 'step-3',
                'action_type': 'click',
                'selector': 'button[type="submit"]',
                'order': 3
            }
        ],
        'created_at': '2025-01-15T10:00:00Z'
    }


# ===== UTILITÁRIOS DE TESTE =====

def async_test(coro):
    """Decorator para testes assíncronos"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


class TestHelper:
    """Utilitários para testes"""

    @staticmethod
    def create_mock_response(status_code=200, json_data=None, text=""):
        """Criar mock de resposta HTTP"""
        response = MagicMock()
        response.status_code = status_code
        response.json = AsyncMock(return_value=json_data or {})
        response.text = text
        return response

    @staticmethod
    def create_mock_browser_page():
        """Criar mock de página do Playwright"""
        page = AsyncMock()
        page.url = "https://example.com"
        page.title = AsyncMock(return_value="Test Page")
        page.query_selector = AsyncMock(return_value=AsyncMock())
        page.query_selector_all = AsyncMock(return_value=[])
        page.fill = AsyncMock(return_value=None)
        page.click = AsyncMock(return_value=None)
        page.wait_for_load_state = AsyncMock(return_value=None)
        page.wait_for_timeout = AsyncMock(return_value=None)
        return page

    @staticmethod
    def assert_task_structure(task_dict: Dict[str, Any]):
        """Verificar estrutura de dados de tarefa"""
        required_fields = ['id', 'name', 'url', 'status', 'created_at']
        for field in required_fields:
            assert field in task_dict, f"Campo obrigatório faltando: {field}"

    @staticmethod
    def assert_execution_result(result: Dict[str, Any]):
        """Verificar estrutura de resultado de execução"""
        assert 'success' in result
        assert 'execution_time' in result
        assert 'message' in result

# Tornar TestHelper disponível globalmente
@pytest.fixture
def test_helper():
    """Fixture para utilitários de teste"""
    return TestHelper()
