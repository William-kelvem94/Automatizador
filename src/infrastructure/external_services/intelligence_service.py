#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SERVIÇO DE INTELIGÊNCIA ARTIFICIAL
Integração com OpenAI, Claude e modelos de ML
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
import anthropic
from ...domain.interfaces.automation_repository import IIntelligenceService
from ...shared.utils.logger import get_logger


class OpenAIService:
    """Serviço de integração com OpenAI GPT-4"""

    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.logger = get_logger(__name__)

    async def generate_selector(self, element_description: str, page_context: str) -> str:
        """Gera seletor inteligente baseado em descrição"""
        try:
            prompt = f"""
            Você é um especialista em automação web. Preciso de um seletor CSS/XPath preciso para o elemento descrito.

            Contexto da página: {page_context}

            Descrição do elemento: {element_description}

            Regras:
            1. Prefira seletores CSS quando possível
            2. Use XPath apenas quando necessário
            3. Considere atributos únicos (id, name, data-*)
            4. Evite seletores frágeis
            5. Retorne apenas o seletor, sem explicações

            Seletor recomendado:
            """

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )

            selector = response.choices[0].message.content.strip()
            self.logger.info(f"Seletor gerado para '{element_description}': {selector}")
            return selector

        except Exception as e:
            self.logger.error(f"Erro ao gerar seletor com OpenAI: {e}")
            return ""

    async def analyze_form_structure(self, form_html: str) -> Dict[str, Any]:
        """Analisa estrutura de formulário"""
        try:
            prompt = f"""
            Analise este formulário HTML e identifique os campos importantes:

            HTML: {form_html[:2000]}...

            Retorne um JSON com:
            {{
                "username_fields": ["seletor1", "seletor2"],
                "password_fields": ["seletor3"],
                "submit_buttons": ["seletor4"],
                "confidence": 0.85
            }}

            Foque em campos de login e botões de submit.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )

            result = json.loads(response.choices[0].message.content.strip())
            self.logger.info(f"Análise de formulário concluída: {len(result.get('username_fields', []))} campos usuário")
            return result

        except Exception as e:
            self.logger.error(f"Erro na análise de formulário: {e}")
            return {"username_fields": [], "password_fields": [], "submit_buttons": [], "confidence": 0.0}


class ClaudeService:
    """Serviço de integração com Anthropic Claude"""

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.logger = get_logger(__name__)

    async def predict_execution_success(self, task_data: Dict[str, Any]) -> float:
        """Prediz probabilidade de sucesso da execução"""
        try:
            prompt = f"""
            Analise esta tarefa de automação e estime a probabilidade de sucesso (0.0 a 1.0).

            Dados da tarefa:
            - URL: {task_data.get('url', '')}
            - Tipo de navegador: {task_data.get('browser_type', 'chrome')}
            - Seletores: {task_data.get('username_selector', '')}, {task_data.get('password_selector', '')}
            - Histórico: {len(task_data.get('execution_history', []))} execuções anteriores

            Considere fatores como:
            - Estabilidade da URL
            - Qualidade dos seletores
            - Histórico de execuções
            - Complexidade da página

            Retorne apenas um número entre 0.0 e 1.0 representando a confiança.
            """

            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=50,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            confidence = float(response.content[0].text.strip())
            confidence = max(0.0, min(1.0, confidence))  # Clamp to valid range

            self.logger.info(f"Predição de sucesso: {confidence:.2f}")
            return confidence

        except Exception as e:
            self.logger.error(f"Erro na predição: {e}")
            return 0.5  # Default confidence


class IntelligenceService(IIntelligenceService):
    """Serviço principal de inteligência artificial"""

    def __init__(self, openai_key: Optional[str] = None, claude_key: Optional[str] = None):
        self.logger = get_logger(__name__)

        # Initialize AI services
        self.openai_service = OpenAIService(openai_key) if openai_key else None
        self.claude_service = ClaudeService(claude_key) if claude_key else None

        # Fallback para quando APIs não estão disponíveis
        self._fallback_mode = not (self.openai_service or self.claude_service)

        if self._fallback_mode:
            self.logger.warning("Modo fallback ativado - APIs de IA não configuradas")
        else:
            self.logger.info("Serviços de IA inicializados")

    async def generate_selector(self, element_description: str, page_context: str) -> str:
        """Gera seletor inteligente"""
        if self.openai_service:
            return await self.openai_service.generate_selector(element_description, page_context)
        elif self.claude_service:
            # Claude pode gerar seletores também
            return await self._generate_selector_fallback(element_description, page_context)
        else:
            return self._generate_selector_fallback(element_description, page_context)

    async def analyze_form_structure(self, form_html: str) -> Dict[str, Any]:
        """Analisa estrutura de formulário"""
        if self.openai_service:
            return await self.openai_service.analyze_form_structure(form_html)
        else:
            return self._analyze_form_fallback(form_html)

    async def predict_execution_success(self, task_data: Dict[str, Any]) -> float:
        """Prediz probabilidade de sucesso"""
        if self.claude_service:
            return await self.claude_service.predict_execution_success(task_data)
        else:
            return self._predict_success_fallback(task_data)

    async def suggest_optimizations(self, execution_history: List[Dict[str, Any]]) -> List[str]:
        """Sugere otimizações baseadas no histórico"""
        if not execution_history:
            return ["Adicione mais execuções para gerar sugestões"]

        # Análise básica do histórico
        total_executions = len(execution_history)
        successful_executions = sum(1 for exec in execution_history if exec.get('success', False))
        success_rate = successful_executions / total_executions if total_executions > 0 else 0

        suggestions = []

        if success_rate < 0.8:
            suggestions.append("Taxa de sucesso baixa. Considere revisar os seletores.")

        # Análise de tempo de execução
        execution_times = [exec.get('execution_time', 0) for exec in execution_history if exec.get('execution_time', 0) > 0]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            if avg_time > 10:
                suggestions.append(".2f")

        # Análise de padrões de falha
        failure_reasons = [exec.get('error_details', '') for exec in execution_history if not exec.get('success', False)]
        if failure_reasons:
            common_failures = self._find_common_patterns(failure_reasons)
            suggestions.extend(common_failures)

        return suggestions

    # ===== MÉTODOS DE FALLBACK =====

    async def _generate_selector_fallback(self, element_description: str, page_context: str) -> str:
        """Geração de seletor em modo fallback"""
        desc_lower = element_description.lower()

        # Regras básicas de geração
        if 'usuário' in desc_lower or 'email' in desc_lower or 'login' in desc_lower:
            return 'input[type="email"], input[name*="user"], input[name*="email"]'
        elif 'senha' in desc_lower or 'password' in desc_lower:
            return 'input[type="password"]'
        elif 'entrar' in desc_lower or 'login' in desc_lower or 'submit' in desc_lower:
            return 'button[type="submit"], input[type="submit"]'
        else:
            return 'input[type="text"]'  # Fallback genérico

    def _analyze_form_fallback(self, form_html: str) -> Dict[str, Any]:
        """Análise de formulário em modo fallback"""
        # Análise básica baseada em padrões
        username_selectors = []
        password_selectors = []
        submit_selectors = []

        # Padrões comuns
        if 'type="email"' in form_html or 'name="email"' in form_html:
            username_selectors.append('input[type="email"]')
        if 'name="username"' in form_html or 'name="user"' in form_html:
            username_selectors.append('input[name="username"]')

        if 'type="password"' in form_html:
            password_selectors.append('input[type="password"]')

        if 'type="submit"' in form_html:
            submit_selectors.append('input[type="submit"], button[type="submit"]')

        return {
            "username_fields": username_selectors,
            "password_fields": password_selectors,
            "submit_buttons": submit_selectors,
            "confidence": 0.6  # Confiança menor no modo fallback
        }

    def _predict_success_fallback(self, task_data: Dict[str, Any]) -> float:
        """Predição de sucesso em modo fallback"""
        confidence = 0.5  # Base

        # Ajustes baseados nos dados
        if task_data.get('url') and 'http' in task_data['url']:
            confidence += 0.1

        if task_data.get('username_selector') and task_data.get('password_selector'):
            confidence += 0.2

        execution_history = task_data.get('execution_history', [])
        if execution_history:
            success_rate = sum(1 for exec in execution_history if exec.get('success', False)) / len(execution_history)
            confidence = confidence * 0.7 + success_rate * 0.3

        return max(0.0, min(1.0, confidence))

    def _find_common_patterns(self, failure_reasons: List[str]) -> List[str]:
        """Encontra padrões comuns em falhas"""
        patterns = []

        reasons_text = ' '.join(failure_reasons).lower()

        if 'timeout' in reasons_text or 'time' in reasons_text:
            patterns.append("Timeouts frequentes. Considere aumentar o tempo limite.")

        if 'selector' in reasons_text or 'element' in reasons_text:
            patterns.append("Problemas com seletores. Considere usar seletores mais específicos.")

        if 'network' in reasons_text or 'connection' in reasons_text:
            patterns.append("Problemas de rede. Considere adicionar retry logic.")

        return patterns

    # ===== MÉTODOS DE CONFIGURAÇÃO =====

    def is_ai_available(self) -> bool:
        """Verifica se serviços de IA estão disponíveis"""
        return not self._fallback_mode

    def get_available_services(self) -> List[str]:
        """Retorna lista de serviços disponíveis"""
        services = []
        if self.openai_service:
            services.append("OpenAI GPT-4")
        if self.claude_service:
            services.append("Anthropic Claude")
        return services

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde dos serviços de IA"""
        health = {
            "service": "IntelligenceService",
            "status": "healthy" if not self._fallback_mode else "degraded",
            "fallback_mode": self._fallback_mode,
            "available_services": self.get_available_services(),
            "timestamp": datetime.now().isoformat()
        }

        # Test básico de conectividade
        try:
            if self.openai_service:
                health["openai_status"] = "available"
            if self.claude_service:
                health["claude_status"] = "available"
        except Exception as e:
            health["error"] = str(e)
            health["status"] = "unhealthy"

        return health
