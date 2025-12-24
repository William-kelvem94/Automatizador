#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SERVIÇOS DE DOMÍNIO - INTELIGÊNCIA
Serviços de negócio para inteligência artificial
"""

from typing import Dict, Any, List, Optional
from ..entities.automation_task import AutomationTask, Selector, ValidationRule
from ..interfaces.automation_repository import IIntelligenceService, IAutomationService
from ...shared.utils.logger import get_logger


class SelectorIntelligenceService:
    """Serviço de domínio: Inteligência para geração de seletores"""

    def __init__(self, intelligence_service: IIntelligenceService, automation_service: IAutomationService):
        self.intelligence = intelligence_service
        self.automation = automation_service
        self.logger = get_logger(__name__)

    async def enhance_selectors(self, task: AutomationTask) -> AutomationTask:
        """Melhora os seletores da tarefa usando IA"""
        try:
            self.logger.info(f"Melhorando seletores para tarefa {task.id}")

            # Analisa a página para gerar seletores inteligentes
            if task.url:
                analysis = await self.automation.analyze_page(task.url)

                # Sugere seletores baseados na análise
                if analysis.recommended_selectors:
                    recommendations = analysis.recommended_selectors

                    # Atualiza seletores se não estiverem definidos ou forem genéricos
                    if not task.username_selector or task.username_selector == 'input[type="email"]':
                        if recommendations.get('username'):
                            task.username_selector = recommendations['username']
                            self.logger.info(f"Seletor usuário melhorado: {task.username_selector}")

                    if not task.password_selector or task.password_selector == 'input[type="password"]':
                        if recommendations.get('password'):
                            task.password_selector = recommendations['password']
                            self.logger.info(f"Seletor senha melhorado: {task.password_selector}")

                    if not task.submit_selector or task.submit_selector == 'button[type="submit"]':
                        if recommendations.get('submit'):
                            task.submit_selector = recommendations['submit']
                            self.logger.info(f"Seletor submit melhorado: {task.submit_selector}")

            return task

        except Exception as e:
            self.logger.error(f"Erro ao melhorar seletores: {e}")
            return task

    async def generate_smart_selector(self, description: str, context: str) -> Selector:
        """Gera seletor inteligente com IA"""
        try:
            selector_value = await self.intelligence.generate_selector(description, context)

            # Cria objeto Selector com confiança baseada na IA
            confidence = 0.9 if self.intelligence.is_ai_available() else 0.7

            selector = Selector(
                value=selector_value,
                selector_type="ai_generated",
                confidence=confidence
            )

            self.logger.info(f"Seletor inteligente gerado: {selector_value} (confiança: {confidence})")
            return selector

        except Exception as e:
            self.logger.error(f"Erro ao gerar seletor inteligente: {e}")
            # Fallback para seletor básico
            return Selector(
                value="input[type='text']",
                selector_type="fallback",
                confidence=0.3
            )

    async def validate_selector_quality(self, selector: Selector, task: AutomationTask) -> Dict[str, Any]:
        """Valida qualidade de um seletor"""
        try:
            if not task.url:
                return {"valid": False, "confidence": 0.0, "reason": "URL não definida"}

            # Testa o seletor na página
            result = await self.automation.validate_selectors(task.url, {"test": selector.value})

            selector_result = result.get("selectors", {}).get("test", {})
            found = selector_result.get("found", 0)
            visible = selector_result.get("visible", 0)
            valid = selector_result.get("valid", False)

            # Calcula confiança baseada nos resultados
            confidence = selector.confidence
            if found == 0:
                confidence *= 0.3  # Seletor não encontrou nada
            elif visible == 0:
                confidence *= 0.7  # Elementos encontrados mas não visíveis
            elif found == 1 and visible == 1:
                confidence *= 1.2  # Perfeito - um elemento visível
                confidence = min(confidence, 1.0)

            return {
                "valid": valid,
                "confidence": confidence,
                "found": found,
                "visible": visible,
                "selector": selector.value
            }

        except Exception as e:
            self.logger.error(f"Erro ao validar seletor: {e}")
            return {
                "valid": False,
                "confidence": 0.0,
                "error": str(e)
            }


class WorkflowOptimizerService:
    """Serviço de domínio: Otimização de workflows"""

    def __init__(self, intelligence_service: IIntelligenceService):
        self.intelligence = intelligence_service
        self.logger = get_logger(__name__)

    async def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Otimiza workflow baseado em IA"""
        try:
            self.logger.info("Otimizando workflow com IA")

            # Análise básica do workflow
            steps = workflow_data.get('steps', [])
            optimizations = []

            # Verifica se há passos redundantes
            if len(steps) > 1:
                # Agrupa passos similares
                similar_steps = self._find_similar_steps(steps)
                if similar_steps:
                    optimizations.append(f"Passos similares encontrados: {similar_steps}")

            # Verifica ordem dos passos
            order_issues = self._analyze_step_order(steps)
            if order_issues:
                optimizations.append(f"Possíveis problemas de ordem: {order_issues}")

            # Sugestões de melhoria
            improvement_suggestions = await self.intelligence.suggest_optimizations(
                workflow_data.get('execution_history', [])
            )
            optimizations.extend(improvement_suggestions)

            return {
                "optimized_workflow": workflow_data,
                "optimizations": optimizations,
                "confidence": 0.8 if self.intelligence.is_ai_available() else 0.6
            }

        except Exception as e:
            self.logger.error(f"Erro na otimização do workflow: {e}")
            return {
                "optimized_workflow": workflow_data,
                "optimizations": ["Erro na análise - manter workflow atual"],
                "confidence": 0.0
            }

    def _find_similar_steps(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Encontra passos similares que podem ser consolidados"""
        similar_groups = []

        for i, step1 in enumerate(steps):
            for j, step2 in enumerate(steps[i+1:], i+1):
                if self._steps_are_similar(step1, step2):
                    similar_groups.append(f"Passos {i+1} e {j+1}")

        return similar_groups

    def _steps_are_similar(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> bool:
        """Verifica se dois passos são similares"""
        # Lógica simplificada - passos com mesmo tipo e seletores similares
        return (step1.get('action_type') == step2.get('action_type') and
                step1.get('selector') == step2.get('selector'))

    def _analyze_step_order(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Analisa ordem dos passos"""
        issues = []

        # Verifica se há interação com campo antes de preenchê-lo
        for i, step in enumerate(steps):
            if step.get('action_type') == 'type':
                # Verifica se há um passo de foco/clique antes
                has_prep_step = any(
                    prev_step.get('action_type') in ['click', 'hover'] and
                    prev_step.get('selector') == step.get('selector')
                    for prev_step in steps[:i]
                )
                if not has_prep_step:
                    issues.append(f"Passo {i+1}: Considerar adicionar foco antes de digitar")

        return issues


class ExecutionPredictorService:
    """Serviço de domínio: Predição de execução"""

    def __init__(self, intelligence_service: IIntelligenceService):
        self.intelligence = intelligence_service
        self.logger = get_logger(__name__)

    async def predict_execution_outcome(self, task: AutomationTask) -> Dict[str, Any]:
        """Prediz resultado da execução"""
        try:
            task_data = task.to_dict()

            # Usa IA para predição se disponível
            if self.intelligence.is_ai_available():
                success_probability = await self.intelligence.predict_execution_success(task_data)
            else:
                success_probability = self._predict_success_fallback(task_data)

            # Análise adicional baseada no histórico
            historical_analysis = self._analyze_historical_data(task)

            # Estimativa de tempo
            estimated_time = self._estimate_execution_time(task)

            prediction = {
                "success_probability": success_probability,
                "estimated_time": estimated_time,
                "risk_factors": self._identify_risk_factors(task),
                "recommendations": self._generate_recommendations(success_probability, task),
                "confidence": historical_analysis['confidence']
            }

            self.logger.info(f"Predição para tarefa {task.id}: {success_probability:.1%} chance de sucesso")
            return prediction

        except Exception as e:
            self.logger.error(f"Erro na predição: {e}")
            return {
                "success_probability": 0.5,
                "estimated_time": 30.0,
                "risk_factors": ["Erro na análise"],
                "recommendations": ["Executar teste manual primeiro"],
                "confidence": 0.0
            }

    def _predict_success_fallback(self, task_data: Dict[str, Any]) -> float:
        """Predição de sucesso em modo fallback"""
        confidence = 0.5

        # Fatores positivos
        if task_data.get('url'):
            confidence += 0.1
        if task_data.get('username_selector') and task_data.get('password_selector'):
            confidence += 0.2
        if task_data.get('execution_history'):
            success_rate = sum(1 for exec in task_data['execution_history'] if exec.get('success', False))
            success_rate = success_rate / len(task_data['execution_history'])
            confidence = confidence * 0.7 + success_rate * 0.3

        # Fatores negativos
        if not task_data.get('username') or not task_data.get('password'):
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def _analyze_historical_data(self, task: AutomationTask) -> Dict[str, Any]:
        """Analisa dados históricos da tarefa"""
        history = task.execution_history

        if not history:
            return {"confidence": 0.5, "trend": "unknown"}

        success_rate = task.get_success_rate()

        # Tendência
        recent_executions = history[-5:]  # Últimas 5
        recent_success_rate = sum(1 for exec in recent_executions if exec.success) / len(recent_executions)

        if recent_success_rate > success_rate + 0.1:
            trend = "improving"
        elif recent_success_rate < success_rate - 0.1:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "confidence": min(0.9, 0.5 + len(history) * 0.1),  # Confiança aumenta com histórico
            "trend": trend,
            "success_rate": success_rate
        }

    def _estimate_execution_time(self, task: AutomationTask) -> float:
        """Estima tempo de execução"""
        base_time = 10.0  # Tempo base

        # Ajustes baseados na complexidade
        if task.workflow and task.workflow.steps:
            base_time += len(task.workflow.steps) * 2.0  # 2s por passo

        # Ajustes baseados no histórico
        if task.execution_history:
            avg_time = sum(exec.execution_time for exec in task.execution_history if exec.execution_time > 0)
            avg_time /= len([exec for exec in task.execution_history if exec.execution_time > 0])
            if avg_time > 0:
                base_time = (base_time + avg_time) / 2  # Média entre estimativa e histórico

        return round(base_time, 1)

    def _identify_risk_factors(self, task: AutomationTask) -> List[str]:
        """Identifica fatores de risco"""
        risks = []

        # Riscos relacionados aos seletores
        if not task.username_selector or task.username_selector == 'input[type="email"]':
            risks.append("Seletor de usuário genérico - pode falhar")

        if not task.password_selector or task.password_selector == 'input[type="password"]':
            risks.append("Seletor de senha genérico - pode falhar")

        # Riscos relacionados ao histórico
        if task.execution_history:
            recent_failures = sum(1 for exec in task.execution_history[-3:] if not exec.success)
            if recent_failures >= 2:
                risks.append("Múltiplas falhas recentes")

        # Riscos relacionados à configuração
        if task.max_retries == 0:
            risks.append("Sem tentativas de retry configuradas")

        return risks

    def _generate_recommendations(self, success_probability: float, task: AutomationTask) -> List[str]:
        """Gera recomendações baseadas na predição"""
        recommendations = []

        if success_probability < 0.5:
            recommendations.append("Executar teste manual primeiro")
            recommendations.append("Melhorar seletores usando análise de página")

        if success_probability < 0.7:
            recommendations.append("Considerar aumentar max_retries")
            recommendations.append("Adicionar validações adicionais")

        # Recomendações baseadas no histórico
        if task.execution_history and len(task.execution_history) > 3:
            success_rate = task.get_success_rate()
            if success_rate < 0.8:
                recommendations.append("Revisar e atualizar seletores")

        return recommendations
