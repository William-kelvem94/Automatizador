#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SERVIÇO DE AUTOMAÇÃO - PLAYWRIGHT
Implementação da interface IAutomationService usando Playwright
"""

import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from ...domain.entities.automation_task import AutomationTask, WebPageAnalysis, AutomationResult
from ...domain.interfaces.automation_repository import IAutomationService
from ...shared.utils.logger import get_logger


class PlaywrightAutomationService(IAutomationService):
    """Serviço de automação implementado com Playwright"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.playwright = None
        self.browser = None
        self.context = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Garante que o Playwright está inicializado"""
        if not self._initialized:
            await self._initialize()
            self._initialized = True

    async def _initialize(self):
        """Inicializa Playwright e navegador"""
        try:
            self.logger.info("Inicializando Playwright...")
            self.playwright = await async_playwright().start()

            # Lança navegador (por enquanto sempre Chromium/Chrome)
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Temporariamente visível para desenvolvimento
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Carrega mais rápido
                    '--window-size=1200,800'
                ]
            )

            # Cria contexto
            self.context = await self.browser.new_context(
                viewport={'width': 1200, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.logger.info("Playwright inicializado com sucesso")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar Playwright: {e}")
            raise

    async def cleanup(self):
        """Limpa recursos"""
        try:
            if self.context:
                await self.context.close()
                self.context = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self._initialized = False
            self.logger.info("Recursos do Playwright liberados")

        except Exception as e:
            self.logger.error(f"Erro ao limpar recursos: {e}")

    async def execute_task(self, task: AutomationTask) -> Dict[str, Any]:
        """Executa uma tarefa de automação completa"""
        await self._ensure_initialized()

        start_time = asyncio.get_event_loop().time()
        page = None

        try:
            self.logger.info(f"Executando tarefa: {task.name} ({task.id})")

            # Cria nova página
            page = await self.context.new_page()

            # Navega para URL
            self.logger.debug(f"Navegando para: {task.url}")
            await page.goto(task.url, wait_until='domcontentloaded', timeout=task.timeout * 1000)

            # Aguarda carregamento
            await page.wait_for_load_state('networkidle', timeout=10000)

            # Preenche formulário
            await self._fill_login_form(page, task)

            # Submete formulário
            await self._submit_form(page, task)

            # Verifica resultado
            success = await self._verify_login_success(page)

            execution_time = asyncio.get_event_loop().time() - start_time

            result = AutomationResult(
                success=success,
                message="Login executado com sucesso" if success else "Falha no login",
                execution_time=execution_time,
                data={
                    'url': task.url,
                    'final_url': page.url,
                    'title': await page.title()
                }
            )

            self.logger.info(f"Tarefa {task.id} {'concluída' if success else 'falhou'} em {execution_time:.2f}s")
            return result.to_dict()

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Erro na execução: {str(e)}"

            self.logger.error(f"Tarefa {task.id} falhou: {error_msg}")

            result = AutomationResult(
                success=False,
                message=error_msg,
                execution_time=execution_time,
                error_details=str(e)
            )
            return result.to_dict()

        finally:
            if page:
                await page.close()

    async def _fill_login_form(self, page: Page, task: AutomationTask):
        """Preenche o formulário de login"""
        try:
            # Preenche usuário
            if task.username_selector and task.username:
                self.logger.debug(f"Preenchendo usuário: {task.username_selector}")
                await page.fill(task.username_selector, task.username)
                await page.wait_for_timeout(500)  # Pequena pausa

            # Preenche senha
            if task.password_selector and task.password:
                self.logger.debug(f"Preenchendo senha: {task.password_selector}")
                await page.fill(task.password_selector, task.password)
                await page.wait_for_timeout(500)  # Pequena pausa

        except Exception as e:
            self.logger.warning(f"Erro ao preencher formulário: {e}")
            raise

    async def _submit_form(self, page: Page, task: AutomationTask):
        """Submete o formulário"""
        try:
            if task.submit_selector:
                self.logger.debug(f"Clicando em submit: {task.submit_selector}")

                # Tenta clicar no botão
                await page.click(task.submit_selector)

                # Aguarda navegação ou mudança de estado
                try:
                    await page.wait_for_load_state('networkidle', timeout=10000)
                except:
                    # Se não houve navegação, aguarda um pouco
                    await page.wait_for_timeout(2000)

        except Exception as e:
            self.logger.warning(f"Erro ao submeter formulário: {e}")
            raise

    async def _verify_login_success(self, page: Page) -> bool:
        """Verifica se o login foi bem-sucedido"""
        try:
            current_url = page.url
            title = await page.title()

            # Estratégias para verificar sucesso:

            # 1. Verifica se URL mudou (redirecionamento após login)
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                return True

            # 2. Procura por elementos que indicam logout/sair
            logout_selectors = [
                'a[href*="logout"]',
                'a[href*="sair"]',
                'button[title*="sair"]',
                'a:has-text("Sair")',
                'button:has-text("Logout")'
            ]

            for selector in logout_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        return True
                except:
                    continue

            # 3. Verifica se campos de login ainda existem
            login_fields = await page.query_selector_all('input[type="password"]')
            if not login_fields:  # Se não há mais campos de senha
                return True

            # 4. Procura mensagens de sucesso
            success_indicators = [
                'text=Bem-vindo',
                'text=Login realizado',
                'text=Autenticado',
                '.success',
                '.alert-success'
            ]

            for indicator in success_indicators:
                try:
                    element = await page.query_selector(indicator)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            return True
                except:
                    continue

            # Se chegou aqui, assume que não foi bem-sucedido
            return False

        except Exception as e:
            self.logger.warning(f"Erro ao verificar sucesso do login: {e}")
            return False

    async def analyze_page(self, url: str) -> WebPageAnalysis:
        """Analisa uma página web para identificar elementos"""
        await self._ensure_initialized()

        page = None
        start_time = asyncio.get_event_loop().time()

        try:
            self.logger.info(f"Analisando página: {url}")

            page = await self.context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_load_state('networkidle', timeout=10000)

            # Coleta informações básicas
            title = await page.title()
            forms_count = len(await page.query_selector_all('form'))
            inputs_count = len(await page.query_selector_all('input'))
            buttons_count = len(await page.query_selector_all('button'))
            links_count = len(await page.query_selector_all('a'))

            # Analisa campos de formulário
            username_fields = await self._analyze_username_fields(page)
            password_fields = await self._analyze_password_fields(page)
            submit_buttons = await self._analyze_submit_buttons(page)

            # Gera recomendações
            recommended_selectors = self._generate_recommendations(username_fields, password_fields, submit_buttons)

            analysis_duration = asyncio.get_event_loop().time() - start_time

            return WebPageAnalysis(
                url=url,
                title=title,
                forms_count=forms_count,
                inputs_count=inputs_count,
                buttons_count=buttons_count,
                links_count=links_count,
                potential_username_fields=username_fields,
                potential_password_fields=password_fields,
                potential_submit_buttons=submit_buttons,
                analysis_duration=analysis_duration,
                recommended_selectors=recommended_selectors
            )

        except Exception as e:
            self.logger.error(f"Erro na análise da página {url}: {e}")
            analysis_duration = asyncio.get_event_loop().time() - start_time

            return WebPageAnalysis(
                url=url,
                analysis_duration=analysis_duration
            )

        finally:
            if page:
                await page.close()

    async def _analyze_username_fields(self, page: Page) -> List[Dict[str, Any]]:
        """Analisa campos que podem ser de usuário/e-mail"""
        selectors = [
            'input[type="email"]',
            'input[name*="user"]',
            'input[name*="email"]',
            'input[name*="login"]',
            'input[id*="user"]',
            'input[id*="email"]',
            'input[id*="login"]',
            'input[placeholder*="email"]',
            'input[placeholder*="usuário"]',
            'input[placeholder*="login"]',
            'input[placeholder*="user"]'
        ]

        fields = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        tag_name = await element.evaluate('el => el.tagName')
                        input_type = await element.get_attribute('type') or 'text'
                        name = await element.get_attribute('name') or ''
                        element_id = await element.get_attribute('id') or ''
                        placeholder = await element.get_attribute('placeholder') or ''

                        confidence = self._calculate_field_confidence(
                            selector, input_type, name, element_id, placeholder
                        )

                        fields.append({
                            'selector': selector,
                            'tag': tag_name,
                            'type': input_type,
                            'name': name,
                            'id': element_id,
                            'placeholder': placeholder,
                            'confidence': confidence,
                            'description': f'Campo {input_type} identificado'
                        })

            except Exception as e:
                self.logger.debug(f"Erro ao analisar seletor {selector}: {e}")
                continue

        # Remove duplicatas e ordena por confiança
        unique_fields = []
        seen_selectors = set()

        for field in sorted(fields, key=lambda x: x['confidence'], reverse=True):
            if field['selector'] not in seen_selectors:
                unique_fields.append(field)
                seen_selectors.add(field['selector'])

        return unique_fields[:10]  # Top 10

    async def _analyze_password_fields(self, page: Page) -> List[Dict[str, Any]]:
        """Analisa campos que podem ser de senha"""
        selectors = [
            'input[type="password"]',
            'input[name*="pass"]',
            'input[name*="senha"]',
            'input[id*="pass"]',
            'input[id*="senha"]',
            'input[placeholder*="senha"]',
            'input[placeholder*="password"]'
        ]

        fields = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        tag_name = await element.evaluate('el => el.tagName')
                        input_type = await element.get_attribute('type') or 'text'
                        name = await element.get_attribute('name') or ''
                        element_id = await element.get_attribute('id') or ''
                        placeholder = await element.get_attribute('placeholder') or ''

                        confidence = self._calculate_password_confidence(
                            selector, input_type, name, element_id, placeholder
                        )

                        fields.append({
                            'selector': selector,
                            'tag': tag_name,
                            'type': input_type,
                            'name': name,
                            'id': element_id,
                            'placeholder': placeholder,
                            'confidence': confidence,
                            'description': f'Campo senha identificado'
                        })

            except Exception as e:
                self.logger.debug(f"Erro ao analisar seletor {selector}: {e}")
                continue

        # Remove duplicatas e ordena por confiança
        unique_fields = []
        seen_selectors = set()

        for field in sorted(fields, key=lambda x: x['confidence'], reverse=True):
            if field['selector'] not in seen_selectors:
                unique_fields.append(field)
                seen_selectors.add(field['selector'])

        return unique_fields[:5]  # Top 5

    async def _analyze_submit_buttons(self, page: Page) -> List[Dict[str, Any]]:
        """Analisa botões que podem ser de submit"""
        selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button[name*="login"]',
            'button[name*="entrar"]',
            'button[id*="login"]',
            'button[id*="entrar"]',
            'button:has-text("Entrar")',
            'button:has-text("Login")',
            'button:has-text("Acessar")',
            'input[value*="entrar"]',
            'input[value*="login"]'
        ]

        buttons = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        tag_name = await element.evaluate('el => el.tagName')
                        button_type = await element.get_attribute('type') or ''
                        name = await element.get_attribute('name') or ''
                        element_id = await element.get_attribute('id') or ''
                        text_content = await element.inner_text() or ''

                        confidence = self._calculate_button_confidence(
                            selector, button_type, name, element_id, text_content
                        )

                        buttons.append({
                            'selector': selector,
                            'tag': tag_name,
                            'type': button_type,
                            'name': name,
                            'id': element_id,
                            'text': text_content,
                            'confidence': confidence,
                            'description': f'Botão submit identificado'
                        })

            except Exception as e:
                self.logger.debug(f"Erro ao analisar seletor {selector}: {e}")
                continue

        # Remove duplicatas e ordena por confiança
        unique_buttons = []
        seen_selectors = set()

        for button in sorted(buttons, key=lambda x: x['confidence'], reverse=True):
            if button['selector'] not in seen_selectors:
                unique_buttons.append(button)
                seen_selectors.add(button['selector'])

        return unique_buttons[:10]  # Top 10

    def _calculate_field_confidence(self, selector: str, input_type: str, name: str,
                                  element_id: str, placeholder: str) -> int:
        """Calcula confiança de um campo ser de usuário/e-mail"""
        confidence = 0

        # Tipo de input
        if input_type == 'email':
            confidence += 50

        # Nome do campo
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in ['user', 'email', 'login', 'mail']):
            confidence += 30

        # ID do elemento
        id_lower = element_id.lower()
        if any(keyword in id_lower for keyword in ['user', 'email', 'login', 'mail']):
            confidence += 25

        # Placeholder
        placeholder_lower = placeholder.lower()
        if any(keyword in placeholder_lower for keyword in ['email', 'usuário', 'user', 'login', 'e-mail']):
            confidence += 20

        return min(confidence, 100)

    def _calculate_password_confidence(self, selector: str, input_type: str, name: str,
                                     element_id: str, placeholder: str) -> int:
        """Calcula confiança de um campo ser de senha"""
        confidence = 0

        # Tipo de input
        if input_type == 'password':
            confidence += 80

        # Nome do campo
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in ['pass', 'senha', 'password', 'pwd']):
            confidence += 40

        # ID do elemento
        id_lower = element_id.lower()
        if any(keyword in id_lower for keyword in ['pass', 'senha', 'password', 'pwd']):
            confidence += 35

        # Placeholder
        placeholder_lower = placeholder.lower()
        if any(keyword in placeholder_lower for keyword in ['senha', 'password', 'pwd']):
            confidence += 25

        return min(confidence, 100)

    def _calculate_button_confidence(self, selector: str, button_type: str, name: str,
                                   element_id: str, text: str) -> int:
        """Calcula confiança de um botão ser de submit"""
        confidence = 0

        # Tipo do botão
        if button_type == 'submit':
            confidence += 60

        # Nome do botão
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in ['login', 'entrar', 'submit', 'acessar']):
            confidence += 30

        # ID do elemento
        id_lower = element_id.lower()
        if any(keyword in id_lower for keyword in ['login', 'entrar', 'submit']):
            confidence += 25

        # Texto do botão
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['entrar', 'login', 'acessar', 'entrar', 'submit']):
            confidence += 35

        return min(confidence, 100)

    def _generate_recommendations(self, username_fields: List, password_fields: List,
                                submit_buttons: List) -> Dict[str, str]:
        """Gera recomendações de seletores"""
        recommendations = {}

        # Recomendação para usuário
        if username_fields:
            best_user = max(username_fields, key=lambda x: x['confidence'])
            recommendations['username'] = best_user['selector']

        # Recomendação para senha
        if password_fields:
            best_pass = max(password_fields, key=lambda x: x['confidence'])
            recommendations['password'] = best_pass['selector']

        # Recomendação para submit
        if submit_buttons:
            best_submit = max(submit_buttons, key=lambda x: x['confidence'])
            recommendations['submit'] = best_submit['selector']

        return recommendations

    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Testa conexão básica com o site"""
        await self._ensure_initialized()

        page = None

        try:
            self.logger.info(f"Testando conexão com: {url}")

            page = await self.context.new_page()

            # Testa carregamento da página
            start_time = asyncio.get_event_loop().time()
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            load_time = asyncio.get_event_loop().time() - start_time

            # Aguarda um pouco mais
            await page.wait_for_load_state('networkidle', timeout=10000)

            title = await page.title()
            current_url = page.url

            return {
                'success': True,
                'http_status': response.status if response else None,
                'page_title': title,
                'current_url': current_url,
                'load_time': round(load_time, 2),
                'message': 'Conexão estabelecida com sucesso'
            }

        except Exception as e:
            self.logger.error(f"Erro na conexão com {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro na conexão: {e}'
            }

        finally:
            if page:
                await page.close()

    async def validate_selectors(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Valida se os seletores funcionam na página"""
        await self._ensure_initialized()

        page = None

        try:
            self.logger.info(f"Validando seletores em: {url}")

            page = await self.context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            results = {}

            for field_name, selector in selectors.items():
                try:
                    elements = await page.query_selector_all(selector)
                    visible_elements = 0

                    for element in elements:
                        if await element.is_visible():
                            visible_elements += 1

                    results[field_name] = {
                        'found': len(elements),
                        'visible': visible_elements,
                        'valid': visible_elements > 0
                    }

                except Exception as e:
                    results[field_name] = {
                        'found': 0,
                        'visible': 0,
                        'valid': False,
                        'error': str(e)
                    }

            return {
                'success': True,
                'selectors': results,
                'message': 'Validação concluída'
            }

        except Exception as e:
            self.logger.error(f"Erro na validação de seletores: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro na validação: {e}'
            }

        finally:
            if page:
                await page.close()
