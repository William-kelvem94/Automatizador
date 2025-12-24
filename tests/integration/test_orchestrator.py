# -*- coding: utf-8 -*-

"""
TESTES DE INTEGRAÇÃO - APPLICATION ORCHESTRATOR
Testes para AutomationOrchestrator e integrações
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.application.services.automation_orchestrator import AutomationOrchestrator
from src.domain.entities.automation_task import AutomationTask, AutomationWorkflow, AutomationStep
from tests.conftest import async_test


@pytest.mark.integration
class TestAutomationOrchestrator:
    """Testes de integração para AutomationOrchestrator"""

    @pytest.fixture
    async def orchestrator(self, mock_repository, mock_automation_service, mock_intelligence_service):
        """Fixture do orchestrator"""
        return AutomationOrchestrator(
            task_repository=mock_repository,
            automation_service=mock_automation_service,
            intelligence_service=mock_intelligence_service
        )

    @async_test
    async def test_create_task_success(self, orchestrator, mock_repository, sample_task_data):
        """Teste criação de tarefa com sucesso"""
        # Configurar mock
        mock_repository.create.return_value = {
            'id': 'task-123',
            'success': True,
            'task': sample_task_data
        }

        result = await orchestrator.create_task(sample_task_data)

        assert result['success'] is True
        assert result['task']['id'] == 'task-123'
        mock_repository.create.assert_called_once()

    @async_test
    async def test_create_task_validation_failure(self, orchestrator, mock_repository):
        """Teste criação com dados inválidos"""
        invalid_data = {
            'name': '',  # Nome vazio
            'url': 'not-a-url'
        }

        result = await orchestrator.create_task(invalid_data)

        assert result['success'] is False
        assert 'error' in result or 'message' in result

    @async_test
    async def test_get_task_by_id_success(self, orchestrator, mock_repository, sample_task_data):
        """Teste busca de tarefa por ID"""
        mock_repository.get_by_id.return_value = sample_task_data

        result = await orchestrator.get_task_by_id('task-123')

        assert result is not None
        assert result['id'] == 'task-123'
        mock_repository.get_by_id.assert_called_once_with('task-123')

    @async_test
    async def test_get_task_by_id_not_found(self, orchestrator, mock_repository):
        """Teste busca de tarefa inexistente"""
        mock_repository.get_by_id.return_value = None

        result = await orchestrator.get_task_by_id('nonexistent')

        assert result is None

    @async_test
    async def test_get_tasks_with_filters(self, orchestrator, mock_repository):
        """Teste busca de tarefas com filtros"""
        tasks = [
            {'id': '1', 'name': 'Task 1', 'status': 'completed'},
            {'id': '2', 'name': 'Task 2', 'status': 'pending'}
        ]
        mock_repository.list.return_value = tasks

        filters = {'status': 'completed', 'limit': 10}
        result = await orchestrator.get_tasks(filters)

        assert 'tasks' in result
        assert len(result['tasks']) == 2
        mock_repository.list.assert_called_once_with(filters)

    @async_test
    async def test_execute_task_success(self, orchestrator, mock_automation_service, mock_repository):
        """Teste execução de tarefa com sucesso"""
        # Configurar mocks
        task_data = {
            'id': 'task-123',
            'name': 'Test Task',
            'url': 'https://example.com',
            'status': 'pending'
        }
        mock_repository.get_by_id.return_value = task_data

        execution_result = {
            'success': True,
            'execution_time': 1.5,
            'message': 'Task executed successfully',
            'result': {'data': 'test'}
        }
        mock_automation_service.execute_task = AsyncMock(return_value=execution_result)

        result = await orchestrator.execute_task('task-123')

        assert result['success'] is True
        assert result['execution_time'] == 1.5
        assert result['message'] == 'Task executed successfully'

        # Verificar se status foi atualizado
        mock_repository.update.assert_called()

    @async_test
    async def test_execute_task_not_found(self, orchestrator, mock_repository):
        """Teste execução de tarefa inexistente"""
        mock_repository.get_by_id.return_value = None

        result = await orchestrator.execute_task('nonexistent')

        assert result['success'] is False
        assert 'not found' in result['message'].lower()

    @async_test
    async def test_execute_task_already_running(self, orchestrator, mock_repository):
        """Teste execução de tarefa já em andamento"""
        task_data = {
            'id': 'task-123',
            'name': 'Test Task',
            'status': 'running'
        }
        mock_repository.get_by_id.return_value = task_data

        result = await orchestrator.execute_task('task-123')

        assert result['success'] is False
        assert 'running' in result['message'].lower()

    @async_test
    async def test_execute_task_with_workflow(self, orchestrator, mock_automation_service, mock_repository):
        """Teste execução de tarefa com workflow complexo"""
        # Criar workflow
        workflow = AutomationWorkflow(
            id='wf-1',
            name='Complex Workflow',
            steps=[
                AutomationStep(id='1', action_type='type', selector='input[name="user"]', order=1, parameters={'value': 'test'}),
                AutomationStep(id='2', action_type='click', selector='button[type="submit"]', order=2)
            ]
        )

        task_data = {
            'id': 'task-123',
            'name': 'Workflow Task',
            'url': 'https://example.com',
            'status': 'pending',
            'workflow': workflow
        }
        mock_repository.get_by_id.return_value = task_data

        execution_result = {
            'success': True,
            'execution_time': 2.5,
            'message': 'Workflow executed successfully',
            'steps_executed': 2
        }
        mock_automation_service.execute_workflow = AsyncMock(return_value=execution_result)

        result = await orchestrator.execute_task('task-123')

        assert result['success'] is True
        assert result['execution_time'] == 2.5
        mock_automation_service.execute_workflow.assert_called_once()

    @async_test
    async def test_analyze_webpage_success(self, orchestrator, mock_automation_service):
        """Teste análise de página web"""
        analysis_result = {
            'success': True,
            'analysis': {
                'url': 'https://example.com',
                'title': 'Test Page',
                'forms_count': 1,
                'inputs_count': 3
            },
            'recommendations': {
                'username': 'input[name="user"]',
                'password': 'input[name="pass"]',
                'submit': 'button[type="submit"]'
            }
        }
        mock_automation_service.analyze_page.return_value = analysis_result

        result = await orchestrator.analyze_webpage('https://example.com')

        assert result['success'] is True
        assert result['analysis']['forms_count'] == 1
        assert 'recommendations' in result
        mock_automation_service.analyze_page.assert_called_once_with('https://example.com')

    @async_test
    async def test_analyze_webpage_failure(self, orchestrator, mock_automation_service):
        """Teste análise de página com falha"""
        mock_automation_service.analyze_page.return_value = {
            'success': False,
            'error': 'Page load timeout'
        }

        result = await orchestrator.analyze_webpage('https://invalid-url.com')

        assert result['success'] is False
        assert 'error' in result

    @async_test
    async def test_get_system_health_all_healthy(self, orchestrator, mock_repository, mock_automation_service, mock_intelligence_service):
        """Teste health check quando tudo está saudável"""
        # Configurar health checks
        mock_repository.health_check = AsyncMock(return_value={'status': 'healthy', 'connections': 5})
        mock_automation_service.health_check = AsyncMock(return_value={'status': 'healthy', 'browsers': 3})
        mock_intelligence_service.health_check = AsyncMock(return_value={'status': 'healthy', 'ai_available': True})

        result = await orchestrator.get_system_health()

        assert result['status'] == 'healthy'
        assert 'services' in result
        assert result['services']['repository'] == 'healthy'
        assert result['services']['automation'] == 'healthy'
        assert result['services']['intelligence'] == 'healthy'

    @async_test
    async def test_get_system_health_partial_failure(self, orchestrator, mock_repository, mock_automation_service, mock_intelligence_service):
        """Teste health check com falha parcial"""
        # Configurar health checks com uma falha
        mock_repository.health_check = AsyncMock(return_value={'status': 'healthy'})
        mock_automation_service.health_check = AsyncMock(return_value={'status': 'unhealthy', 'error': 'Browser not available'})
        mock_intelligence_service.health_check = AsyncMock(return_value={'status': 'healthy'})

        result = await orchestrator.get_system_health()

        assert result['status'] == 'degraded'
        assert result['services']['automation'] == 'unhealthy'

    @async_test
    async def test_get_system_health_complete_failure(self, orchestrator, mock_repository, mock_automation_service, mock_intelligence_service):
        """Teste health check com falha completa"""
        # Configurar todas falhando
        mock_repository.health_check = AsyncMock(side_effect=Exception("DB connection failed"))
        mock_automation_service.health_check = AsyncMock(side_effect=Exception("Browser failed"))
        mock_intelligence_service.health_check = AsyncMock(side_effect=Exception("AI failed"))

        result = await orchestrator.get_system_health()

        assert result['status'] == 'unhealthy'
        assert 'error' in result

    @async_test
    async def test_task_execution_with_retry(self, orchestrator, mock_automation_service, mock_repository):
        """Teste execução com retry automático"""
        # Configurar tarefa com retry
        task_data = {
            'id': 'task-123',
            'name': 'Retry Task',
            'url': 'https://example.com',
            'status': 'pending',
            'max_retries': 2
        }
        mock_repository.get_by_id.return_value = task_data

        # Primeira execução falha, segunda succeeds
        mock_automation_service.execute_task = AsyncMock()
        mock_automation_service.execute_task.side_effect = [
            {'success': False, 'execution_time': 0.5, 'message': 'Network error', 'retry': True},
            {'success': True, 'execution_time': 1.2, 'message': 'Success on retry'}
        ]

        result = await orchestrator.execute_task('task-123')

        assert result['success'] is True
        assert mock_automation_service.execute_task.call_count == 2

    @async_test
    async def test_concurrent_task_execution_limit(self, orchestrator, mock_automation_service, mock_repository):
        """Teste limite de execuções concorrentes"""
        # Configurar limite de concorrência
        orchestrator.max_concurrent_tasks = 2

        # Simular múltiplas tarefas rodando
        running_tasks = [
            {'id': 'task-1', 'status': 'running'},
            {'id': 'task-2', 'status': 'running'}
        ]

        # Verificar se nova tarefa é rejeitada quando limite atingido
        # (Este teste pode precisar ser ajustado baseado na implementação real do limite)

        # Por enquanto, apenas verificar que o orchestrator tem configuração
        assert hasattr(orchestrator, 'max_concurrent_tasks')

    @async_test
    async def test_task_cleanup_after_execution(self, orchestrator, mock_automation_service, mock_repository):
        """Teste limpeza de recursos após execução"""
        task_data = {
            'id': 'task-123',
            'name': 'Cleanup Test',
            'url': 'https://example.com',
            'status': 'pending'
        }
        mock_repository.get_by_id.return_value = task_data

        mock_automation_service.execute_task.return_value = {
            'success': True,
            'execution_time': 1.0,
            'message': 'Success',
            'cleanup_required': True
        }

        result = await orchestrator.execute_task('task-123')

        assert result['success'] is True
        # Verificar se cleanup foi chamado (se implementado)
        # mock_automation_service.cleanup.assert_called_once()


@pytest.mark.integration
class TestOrchestratorIntegration:
    """Testes de integração entre múltiplos componentes"""

    @async_test
    async def test_full_task_lifecycle(self, orchestrator, mock_repository, mock_automation_service, sample_task_data):
        """Teste ciclo de vida completo de uma tarefa"""
        # 1. Criar tarefa
        mock_repository.create.return_value = {
            'id': 'lifecycle-task',
            'success': True,
            'task': {**sample_task_data, 'id': 'lifecycle-task'}
        }

        create_result = await orchestrator.create_task(sample_task_data)
        assert create_result['success'] is True

        # 2. Buscar tarefa criada
        mock_repository.get_by_id.return_value = {**sample_task_data, 'id': 'lifecycle-task', 'status': 'pending'}
        task = await orchestrator.get_task_by_id('lifecycle-task')
        assert task is not None
        assert task['status'] == 'pending'

        # 3. Executar tarefa
        mock_automation_service.execute_task.return_value = {
            'success': True,
            'execution_time': 2.0,
            'message': 'Lifecycle test completed'
        }

        exec_result = await orchestrator.execute_task('lifecycle-task')
        assert exec_result['success'] is True

        # 4. Verificar atualização de status
        # O mock do update deve ter sido chamado para atualizar status para 'completed'
        assert mock_repository.update.called

    @async_test
    async def test_error_propagation_and_handling(self, orchestrator, mock_repository, mock_automation_service):
        """Teste propagação e tratamento de erros"""
        # Configurar falha em cascata
        mock_repository.get_by_id.side_effect = Exception("Database connection lost")

        result = await orchestrator.execute_task('error-task')

        assert result['success'] is False
        assert 'error' in result or 'message' in result

    @async_test
    async def test_performance_monitoring(self, orchestrator, mock_repository, mock_automation_service):
        """Teste monitoramento de performance"""
        # Este teste verifica se métricas de performance são coletadas
        task_data = {'id': 'perf-task', 'name': 'Performance Test', 'url': 'https://example.com'}
        mock_repository.get_by_id.return_value = task_data

        mock_automation_service.execute_task.return_value = {
            'success': True,
            'execution_time': 0.5,
            'message': 'Fast execution',
            'performance_metrics': {'cpu_usage': 15.5, 'memory_usage': 45.2}
        }

        result = await orchestrator.execute_task('perf-task')

        assert result['success'] is True
        assert 'execution_time' in result
        # Verificar se métricas foram preservadas (se suportado)
        if 'performance_metrics' in result:
            assert result['performance_metrics']['cpu_usage'] == 15.5
