# -*- coding: utf-8 -*-

"""
TESTES UNITÁRIOS - SERVIÇOS DE DOMÍNIO
Testes para Intelligence Services e Domain Services
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from src.domain.services.intelligence_services import (
    SelectorIntelligenceService,
    WorkflowOptimizerService,
    ExecutionPredictorService
)
from src.domain.entities.automation_task import (
    AutomationTask,
    AutomationWorkflow,
    AutomationStep,
    BrowserConfig
)


class TestSelectorIntelligenceService:
    """Testes para SelectorIntelligenceService"""

    @pytest.fixture
    def service(self, mock_intelligence_service, mock_automation_service):
        """Fixture do serviço"""
        return SelectorIntelligenceService(
            intelligence_service=mock_intelligence_service,
            automation_service=mock_automation_service
        )

    def test_enhance_selectors_success(self, service, mock_intelligence_service, mock_automation_service):
        """Teste melhoria de seletores com sucesso"""
        # Configurar mocks
        mock_automation_service.analyze_page.return_value = {
            'success': True,
            'recommendations': {
                'username': 'input[name="user"]',
                'password': 'input[name="pass"]',
                'submit': 'button[type="submit"]'
            }
        }

        # Criar tarefa com seletores genéricos
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username='user',
            password='pass',
            username_selector='input[type="email"]',  # Genérico
            password_selector='input[type="password"]',  # OK
            submit_selector='button[type="submit"]'  # OK
        )

        # Executar melhoria
        result = await service.enhance_selectors(task)

        # Verificar que seletor foi melhorado
        assert result.username_selector == 'input[name="user"]'
        assert result.password_selector == 'input[type="password"]'  # Não mudou
        assert result.submit_selector == 'button[type="submit"]'  # Não mudou

    def test_enhance_selectors_analysis_failure(self, service, mock_automation_service):
        """Teste melhoria quando análise falha"""
        mock_automation_service.analyze_page.return_value = {
            'success': False,
            'error': 'Analysis failed'
        }

        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username_selector='input[type="email"]'
        )

        result = await service.enhance_selectors(task)

        # Tarefa deve permanecer inalterada
        assert result.username_selector == 'input[type="email"]'

    def test_generate_smart_selector_success(self, service, mock_intelligence_service):
        """Teste geração de seletor inteligente"""
        mock_intelligence_service.generate_selector.return_value = 'input[name="smart-selector"]'

        result = await service.generate_smart_selector(
            description="Campo de usuário",
            context="Página de login"
        )

        assert result.value == 'input[name="smart-selector"]'
        assert result.selector_type == 'ai_generated'
        assert result.confidence == 0.9

    def test_generate_smart_selector_fallback(self, service, mock_intelligence_service):
        """Teste geração com fallback"""
        mock_intelligence_service.generate_selector.side_effect = Exception("AI failed")

        result = await service.generate_smart_selector(
            description="Campo de usuário",
            context="Página de login"
        )

        assert result.value == 'input[type="text"]'  # Fallback
        assert result.selector_type == 'fallback'
        assert result.confidence == 0.3

    def test_validate_selector_quality(self, service, mock_automation_service):
        """Teste validação de qualidade de seletor"""
        from src.domain.entities.automation_task import Selector

        mock_automation_service.validate_selectors.return_value = {
            'selectors': {
                'test': {'found': 1, 'visible': 1, 'valid': True}
            }
        }

        selector = Selector(value='input[name="test"]', confidence=0.8)
        task = AutomationTask(id='task-1', name='Test', url='https://example.com')

        result = await service.validate_selector_quality(selector, task)

        assert result['valid'] is True
        assert result['found'] == 1
        assert result['visible'] == 1
        assert result['confidence'] > 0.8  # Deve ter aumentado

    def test_validate_selector_not_found(self, service, mock_automation_service):
        """Teste validação quando seletor não é encontrado"""
        from src.domain.entities.automation_task import Selector

        mock_automation_service.validate_selectors.return_value = {
            'selectors': {
                'test': {'found': 0, 'visible': 0, 'valid': False}
            }
        }

        selector = Selector(value='input[name="nonexistent"]', confidence=0.8)
        task = AutomationTask(id='task-1', name='Test', url='https://example.com')

        result = await service.validate_selector_quality(selector, task)

        assert result['valid'] is False
        assert result['found'] == 0
        assert result['confidence'] < 0.8  # Deve ter diminuído


class TestWorkflowOptimizerService:
    """Testes para WorkflowOptimizerService"""

    @pytest.fixture
    def service(self, mock_intelligence_service):
        """Fixture do serviço"""
        return WorkflowOptimizerService(intelligence_service=mock_intelligence_service)

    def test_optimize_workflow_success(self, service, mock_intelligence_service):
        """Teste otimização de workflow com sucesso"""
        mock_intelligence_service.suggest_optimizations.return_value = [
            "Considere usar seletores mais específicos",
            "Adicione validações adicionais"
        ]

        workflow_data = {
            'id': 'wf-1',
            'name': 'Test Workflow',
            'steps': [
                {'id': '1', 'action_type': 'click', 'selector': 'button'},
                {'id': '2', 'action_type': 'type', 'selector': 'input', 'value': 'test'}
            ],
            'execution_history': [
                {'success': True, 'execution_time': 1.5},
                {'success': False, 'execution_time': 0.8}
            ]
        }

        result = await service.optimize_workflow(workflow_data)

        assert result['optimized_workflow'] == workflow_data
        assert len(result['optimizations']) > 0
        assert 'confidence' in result

    def test_optimize_workflow_no_history(self, service):
        """Teste otimização sem histórico"""
        workflow_data = {
            'id': 'wf-1',
            'name': 'Test Workflow',
            'steps': [{'id': '1', 'action_type': 'click', 'selector': 'button'}]
        }

        result = await service.optimize_workflow(workflow_data)

        assert len(result['optimizations']) == 1
        assert "Adicione mais execuções" in result['optimizations'][0]

    def test_find_similar_steps(self, service):
        """Teste detecção de passos similares"""
        steps = [
            {'id': '1', 'action_type': 'click', 'selector': 'button.submit'},
            {'id': '2', 'action_type': 'click', 'selector': 'button.submit'},  # Similar
            {'id': '3', 'action_type': 'type', 'selector': 'input[name="user"]'}
        ]

        similar = service._find_similar_steps(steps)

        assert len(similar) > 0
        assert "Passos 1 e 2" in similar[0]

    def test_analyze_step_order(self, service):
        """Teste análise de ordem dos passos"""
        steps = [
            {'id': '1', 'action_type': 'type', 'selector': 'input[name="user"]'},  # Digita sem focar
            {'id': '2', 'action_type': 'click', 'selector': 'button.submit'}
        ]

        issues = service._analyze_step_order(steps)

        assert len(issues) > 0
        assert "Passo 1" in issues[0]
        assert "foco" in issues[0].lower()


class TestExecutionPredictorService:
    """Testes para ExecutionPredictorService"""

    @pytest.fixture
    def service(self, mock_intelligence_service):
        """Fixture do serviço"""
        return ExecutionPredictorService(intelligence_service=mock_intelligence_service)

    def test_predict_execution_outcome_success(self, service, mock_intelligence_service):
        """Teste predição de resultado com sucesso"""
        mock_intelligence_service.predict_execution_success.return_value = 0.85

        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username='user',
            password='pass',
            execution_history=[
                MagicMock(success=True, execution_time=1.2),
                MagicMock(success=False, execution_time=0.8)
            ]
        )

        result = await service.predict_execution_outcome(task)

        assert 'success_probability' in result
        assert 'estimated_time' in result
        assert 'risk_factors' in result
        assert 'recommendations' in result
        assert result['success_probability'] == 0.85

    def test_predict_execution_outcome_no_history(self, service, mock_intelligence_service):
        """Teste predição sem histórico"""
        mock_intelligence_service.predict_execution_success.return_value = 0.6

        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com'
        )

        result = await service.predict_execution_outcome(task)

        assert result['success_probability'] == 0.6
        assert 'estimated_time' in result
        assert isinstance(result['risk_factors'], list)

    def test_identify_risk_factors(self, service):
        """Teste identificação de fatores de risco"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            username_selector='input[type="email"]',  # Genérico
            execution_history=[
                MagicMock(success=False),
                MagicMock(success=False)  # Duas falhas recentes
            ]
        )

        risks = service._identify_risk_factors(task)

        assert len(risks) > 0
        assert any("seletor" in risk.lower() for risk in risks)
        assert any("falhas recentes" in risk.lower() for risk in risks)

    def test_generate_recommendations(self, service):
        """Teste geração de recomendações"""
        task = AutomationTask(
            id='task-1',
            name='Test Task',
            url='https://example.com',
            execution_history=[MagicMock(success=True)] * 5  # Histórico bom
        )

        recommendations = service._generate_recommendations(0.9, task)

        # Com alta probabilidade e bom histórico, deve haver poucas recomendações
        assert isinstance(recommendations, list)

    def test_predict_success_fallback(self, service):
        """Teste predição fallback"""
        task_data = {
            'url': 'https://example.com',
            'username_selector': 'input[name="user"]',
            'password_selector': 'input[name="pass"]',
            'execution_history': [
                {'success': True, 'execution_time': 1.0},
                {'success': True, 'execution_time': 1.2}
            ]
        }

        probability = service._predict_success_fallback(task_data)

        assert 0.0 <= probability <= 1.0
        assert probability > 0.5  # Deve ser relativamente alta com bom histórico
