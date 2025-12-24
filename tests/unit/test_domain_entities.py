# -*- coding: utf-8 -*-

"""
TESTES UNITÁRIOS - ENTIDADES DE DOMÍNIO
Testes para AutomationTask, Workflow, Step e Value Objects
"""

import pytest
from datetime import datetime, timedelta
from src.domain.entities.automation_task import (
    AutomationTask,
    AutomationWorkflow,
    AutomationStep,
    ExecutionResult,
    Selector,
    ActionType,
    BrowserConfig,
    ValidationRule
)


class TestSelector:
    """Testes para Value Object Selector"""

    def test_selector_creation(self):
        """Teste criação básica de seletor"""
        selector = Selector(
            value='input[name="username"]',
            selector_type='css',
            confidence=0.9
        )

        assert selector.value == 'input[name="username"]'
        assert selector.selector_type == 'css'
        assert selector.confidence == 0.9

    def test_selector_validation(self):
        """Teste validação de seletor"""
        # Seletor válido
        selector = Selector(value='#valid-id', selector_type='css')
        assert selector.value == '#valid-id'

        # Seletor vazio deve falhar
        with pytest.raises(ValueError):
            Selector(value='', selector_type='css')

    def test_selector_equality(self):
        """Teste igualdade de seletores"""
        selector1 = Selector(value='input[name="test"]', selector_type='css')
        selector2 = Selector(value='input[name="test"]', selector_type='css')
        selector3 = Selector(value='input[name="other"]', selector_type='css')

        assert selector1 == selector2
        assert selector1 != selector3


class TestActionType:
    """Testes para Value Object ActionType"""

    def test_valid_action_types(self):
        """Teste tipos de ação válidos"""
        valid_actions = ['click', 'type', 'wait', 'hover', 'select', 'scroll']

        for action in valid_actions:
            action_type = ActionType(action)
            assert action_type.value == action

    def test_invalid_action_type(self):
        """Teste tipo de ação inválido"""
        with pytest.raises(ValueError):
            ActionType('invalid_action')


class TestBrowserConfig:
    """Testes para Value Object BrowserConfig"""

    def test_browser_config_creation(self):
        """Teste criação de configuração de navegador"""
        config = BrowserConfig(
            headless=True,
            user_agent='Test Agent',
            viewport={'width': 1280, 'height': 720},
            timeout=30000
        )

        assert config.headless is True
        assert config.user_agent == 'Test Agent'
        assert config.viewport == {'width': 1280, 'height': 720}
        assert config.timeout == 30000

    def test_browser_config_defaults(self):
        """Teste valores padrão da configuração"""
        config = BrowserConfig()

        assert config.headless is True  # Default para testes
        assert config.timeout == 30000
        assert config.viewport is None


class TestValidationRule:
    """Testes para Value Object ValidationRule"""

    def test_validation_rule_creation(self):
        """Teste criação de regra de validação"""
        rule = ValidationRule(
            field='username',
            rule_type='required',
            value=True,
            message='Username is required'
        )

        assert rule.field == 'username'
        assert rule.rule_type == 'required'
        assert rule.value is True
        assert rule.message == 'Username is required'


class TestAutomationStep:
    """Testes para Entity AutomationStep"""

    def test_step_creation(self):
        """Teste criação de passo de automação"""
        step = AutomationStep(
            id='step-1',
            action_type='click',
            selector='button[type="submit"]',
            order=1,
            parameters={'delay': 1000}
        )

        assert step.id == 'step-1'
        assert step.action_type.value == 'click'
        assert step.selector == 'button[type="submit"]'
        assert step.order == 1
        assert step.parameters == {'delay': 1000}

    def test_step_validation(self):
        """Teste validação de passo"""
        # Passo sem action_type deve falhar
        with pytest.raises(ValueError):
            AutomationStep(id='step-1', selector='button')

        # Passo sem seletor deve falhar para ações que precisam
        with pytest.raises(ValueError):
            AutomationStep(id='step-1', action_type='click')


class TestExecutionResult:
    """Testes para Entity ExecutionResult"""

    def test_execution_result_creation(self):
        """Teste criação de resultado de execução"""
        result = ExecutionResult(
            task_id='task-123',
            success=True,
            execution_time=1.5,
            message='Task completed successfully',
            data={'output': 'test'},
            error_details=None
        )

        assert result.task_id == 'task-123'
        assert result.success is True
        assert result.execution_time == 1.5
        assert result.message == 'Task completed successfully'
        assert result.data == {'output': 'test'}
        assert result.error_details is None

    def test_execution_result_with_error(self):
        """Teste resultado com erro"""
        result = ExecutionResult(
            task_id='task-123',
            success=False,
            execution_time=0.5,
            message='Selector not found',
            error_details='Element input[name="username"] not found'
        )

        assert result.success is False
        assert result.error_details == 'Element input[name="username"] not found'


class TestAutomationWorkflow:
    """Testes para Entity AutomationWorkflow"""

    def test_workflow_creation(self):
        """Teste criação de workflow"""
        steps = [
            AutomationStep(id='1', action_type='type', selector='input[name="user"]', order=1, parameters={'value': 'test'}),
            AutomationStep(id='2', action_type='click', selector='button[type="submit"]', order=2)
        ]

        workflow = AutomationWorkflow(
            id='workflow-1',
            name='Login Workflow',
            description='Automated login process',
            steps=steps,
            created_by='user-123'
        )

        assert workflow.id == 'workflow-1'
        assert workflow.name == 'Login Workflow'
        assert len(workflow.steps) == 2
        assert workflow.created_by == 'user-123'

    def test_workflow_validation(self):
        """Teste validação de workflow"""
        # Workflow sem nome deve falhar
        with pytest.raises(ValueError):
            AutomationWorkflow(id='wf-1', steps=[])

        # Workflow sem passos deve ser válido (pode ser template)
        workflow = AutomationWorkflow(id='wf-1', name='Empty Workflow', steps=[])
        assert workflow.name == 'Empty Workflow'


class TestAutomationTask:
    """Testes para Entity AutomationTask"""

    def test_task_creation_minimal(self):
        """Teste criação mínima de tarefa"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username='testuser',
            password='testpass'
        )

        assert task.id == 'task-1'
        assert task.name == 'Test Task'
        assert task.url == 'https://example.com'
        assert task.username == 'testuser'
        assert task.password == 'testpass'
        assert task.status == 'pending'  # Default

    def test_task_creation_complete(self):
        """Teste criação completa de tarefa"""
        workflow = AutomationWorkflow(
            id='wf-1',
            name='Test Workflow',
            steps=[
                AutomationStep(id='1', action_type='click', selector='button', order=1)
            ]
        )

        task = AutomationTask(
            id='task-1',
            name='Complete Test Task',
            description='A complete test task',
            url='https://example.com/login',
            username='testuser',
            password='testpass123',
            username_selector='input[name="username"]',
            password_selector='input[name="password"]',
            submit_selector='button[type="submit"]',
            workflow=workflow,
            max_retries=3,
            timeout=30000,
            browser_config=BrowserConfig(headless=False, viewport={'width': 1920, 'height': 1080}),
            tags=['login', 'test'],
            metadata={'source': 'test_suite'}
        )

        assert task.description == 'A complete test task'
        assert task.username_selector == 'input[name="username"]'
        assert task.workflow == workflow
        assert task.max_retries == 3
        assert task.browser_config.headless is False
        assert task.tags == ['login', 'test']
        assert task.metadata == {'source': 'test_suite'}

    def test_task_validation(self):
        """Teste validação de tarefa"""
        # Tarefa sem nome deve falhar
        with pytest.raises(ValueError):
            AutomationTask(id='task-1', url='https://example.com')

        # Tarefa sem URL deve falhar
        with pytest.raises(ValueError):
            AutomationTask(id='task-1', name='Test Task')

        # Tarefa com URL inválida deve falhar
        with pytest.raises(ValueError):
            AutomationTask(id='task-1', name='Test Task', url='not-a-url')

    def test_task_status_transitions(self):
        """Teste transições de status"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com'
        )

        # Status inicial
        assert task.status == 'pending'

        # Simular mudança de status (normalmente feito pelo application layer)
        task._status = 'running'
        assert task.status == 'running'

        task._status = 'completed'
        assert task.status == 'completed'

    def test_task_execution_history(self):
        """Teste histórico de execuções"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com'
        )

        # Adicionar resultados de execução
        result1 = ExecutionResult(
            task_id='task-1',
            success=True,
            execution_time=1.2,
            message='Success'
        )

        result2 = ExecutionResult(
            task_id='task-1',
            success=False,
            execution_time=0.8,
            message='Failed',
            error_details='Element not found'
        )

        task.execution_history = [result1, result2]

        # Verificar estatísticas
        assert len(task.execution_history) == 2
        assert task.get_success_rate() == 0.5  # 50% success rate
        assert task.get_last_execution() == result2
        assert task.get_average_execution_time() == 1.0

    def test_task_to_dict(self):
        """Teste conversão para dicionário"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username='user',
            password='pass',
            description='Test description'
        )

        data = task.to_dict()

        assert data['id'] == 'task-1'
        assert data['name'] == 'Test Task'
        assert data['url'] == 'https://example.com'
        assert data['username'] == 'user'
        assert data['password'] == 'pass'
        assert data['description'] == 'Test description'
        assert 'created_at' in data
        assert 'status' in data

    def test_task_from_dict(self):
        """Teste criação a partir de dicionário"""
        data = {
            'id': 'task-1',
            'name': 'Test Task',
            'url': 'https://example.com',
            'username': 'user',
            'password': 'pass',
            'status': 'completed',
            'description': 'Test description',
            'created_at': datetime.now().isoformat(),
            'max_retries': 2
        }

        task = AutomationTask.from_dict(data)

        assert task.id == 'task-1'
        assert task.name == 'Test Task'
        assert task.status == 'completed'
        assert task.max_retries == 2
