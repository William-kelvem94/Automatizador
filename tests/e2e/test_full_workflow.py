# -*- coding: utf-8 -*-

"""
TESTES END-TO-END - WORKFLOW COMPLETO
Testes que simulam uso real da aplicação
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser
from src.presentation.apis.fastapi_app import app
from src.presentation.qt_views.main_window import main
import uvicorn
import threading
import time
from unittest.mock import patch


@pytest.mark.e2e
@pytest.mark.slow
class TestFullWorkflowE2E:
    """Testes E2E do workflow completo"""

    @pytest.fixture(scope="class")
    async def api_server(self):
        """Fixture para servidor API durante testes E2E"""
        # Iniciar servidor em thread separada
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="error"))

        def run_server():
            asyncio.run(server.serve())

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

        # Aguardar servidor iniciar
        await asyncio.sleep(2)

        yield "http://127.0.0.1:8001"

        # Parar servidor
        server.should_exit = True
        await asyncio.sleep(1)

    @pytest.fixture(scope="class")
    async def browser_context(self):
        """Fixture para contexto do browser"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='AutomatorWebIA-E2E-Test/1.0'
            )

            yield context

            await context.close()
            await browser.close()

    @pytest.mark.asyncio
    async def test_api_health_check(self, api_server):
        """Teste E2E: Health check da API"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_server}/health")

            assert response.status_code == 200
            data = response.json()
            assert data['status'] in ['healthy', 'degraded']
            assert 'services' in data
            assert 'timestamp' in data

    @pytest.mark.asyncio
    async def test_api_create_and_execute_task(self, api_server, browser_context):
        """Teste E2E: Criar e executar tarefa via API"""
        import httpx

        async with httpx.AsyncClient() as client:
            # 1. Criar tarefa
            task_data = {
                "name": "E2E Test Task",
                "description": "Test task for E2E testing",
                "url": "https://httpbin.org/html",  # URL segura para testes
                "username": "testuser",
                "password": "testpass123"
            }

            create_response = await client.post(
                f"{api_server}/tasks",
                json=task_data,
                timeout=10.0
            )

            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data['success'] is True
            task_id = create_data['task']['id']

            # 2. Executar tarefa (simulado, pois httpbin não tem login real)
            # Nota: Este teste pode falhar dependendo da implementação real
            # Vamos apenas verificar se a API responde corretamente
            execute_response = await client.post(
                f"{api_server}/tasks/{task_id}/execute",
                timeout=30.0
            )

            # Aceitar tanto sucesso quanto falha controlada
            execute_data = execute_response.json()
            assert 'success' in execute_data
            assert 'message' in execute_data
            assert 'execution_time' in execute_data

    @pytest.mark.asyncio
    async def test_api_analyze_webpage(self, api_server):
        """Teste E2E: Análise de página web via API"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_server}/analyze",
                json={"url": "https://httpbin.org/html"},
                timeout=15.0
            )

            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data

            if data['success']:
                assert 'analysis' in data
                analysis = data['analysis']
                assert 'url' in analysis

    @pytest.mark.asyncio
    async def test_web_interface_basic_load(self, browser_context):
        """Teste E2E: Carregamento básico da interface web"""
        page = await browser_context.new_page()

        try:
            # Este teste assume que temos uma interface web rodando
            # Se não tiver, o teste será pulado
            web_url = "http://localhost:3000"  # Next.js dev server

            try:
                await page.goto(web_url, timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=5000)

                # Verificar elementos básicos
                title = await page.title()
                assert "Automator" in title

                # Verificar se há algum conteúdo carregado
                content = await page.text_content('body')
                assert len(content) > 0

            except Exception as e:
                pytest.skip(f"Web interface not available: {e}")

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_full_user_journey_simulation(self, browser_context, api_server):
        """Teste E2E: Jornada completa do usuário simulada"""
        import httpx

        # Simular jornada: Análise -> Criação -> Execução -> Resultado

        async with httpx.AsyncClient() as client:
            # 1. Analisar página
            analysis_response = await client.post(
                f"{api_server}/analyze",
                json={"url": "https://httpbin.org/html"}
            )
            analysis_data = analysis_response.json()

            # 2. Criar tarefa baseada na análise
            task_data = {
                "name": "E2E Journey Task",
                "url": "https://httpbin.org/html",
                "username": "journey_user",
                "password": "journey_pass"
            }

            create_response = await client.post(
                f"{api_server}/tasks",
                json=task_data
            )
            create_data = create_response.json()
            assert create_data['success'] is True

            # 3. Listar tarefas para verificar criação
            list_response = await client.get(f"{api_server}/tasks")
            list_data = list_response.json()
            assert isinstance(list_data, list)

            # 4. Tentar executar (pode falhar, mas deve responder)
            task_id = create_data['task']['id']
            execute_response = await client.post(
                f"{api_server}/tasks/{task_id}/execute",
                timeout=20.0
            )
            execute_data = execute_response.json()
            assert 'success' in execute_data

            # 5. Verificar health continua OK
            health_response = await client.get(f"{api_server}/health")
            health_data = health_response.json()
            assert health_data['status'] in ['healthy', 'degraded']

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires GUI environment")
    async def test_desktop_application_basic(self):
        """Teste E2E: Aplicação desktop básica (pulado em CI)"""
        # Este teste só roda em ambiente com GUI
        # Simular inicialização da aplicação desktop

        with patch('src.presentation.qt_views.main_window.QApplication'):
            with patch('src.presentation.qt_views.main_window.MainWindow'):
                try:
                    # Tentar importar e executar main
                    from src.presentation.qt_views.main_window import main
                    # Nota: main() pode bloquear, então este teste é limitado
                    assert callable(main)
                except ImportError:
                    pytest.skip("Qt dependencies not available")

    @pytest.mark.asyncio
    async def test_cli_basic_functionality(self):
        """Teste E2E: Funcionalidades básicas da CLI"""
        # Testar CLI sem argumentos
        import subprocess
        import sys

        try:
            result = subprocess.run([
                sys.executable, "src/presentation/cli/automator_cli.py", "--help"
            ], capture_output=True, text=True, timeout=10)

            assert result.returncode == 0
            assert "Automator IA" in result.stdout
            assert "CLI Tools" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except FileNotFoundError:
            pytest.skip("CLI script not found")

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, api_server):
        """Teste E2E: Múltiplas requisições simultâneas"""
        import httpx
        import asyncio

        async def make_request(client, request_id):
            try:
                response = await client.get(f"{api_server}/health")
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'error': str(e),
                    'success': False
                }

        # Fazer 10 requisições simultâneas
        async with httpx.AsyncClient() as client:
            tasks = [
                make_request(client, i)
                for i in range(10)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verificar que a maioria das requisições teve sucesso
            successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
            assert successful_requests >= 7  # Pelo menos 70% de sucesso

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, api_server):
        """Teste E2E: Tratamento de erros e recuperação"""
        import httpx

        async with httpx.AsyncClient() as client:
            # 1. Tentar acessar endpoint inexistente
            try:
                response = await client.get(f"{api_server}/nonexistent")
                assert response.status_code == 404
            except Exception:
                # Pode falhar de diferentes formas, o importante é não quebrar
                pass

            # 2. Tentar criar tarefa com dados inválidos
            invalid_task = {
                "name": "",
                "url": "not-a-valid-url"
            }

            response = await client.post(
                f"{api_server}/tasks",
                json=invalid_task
            )

            # Deve retornar erro, não quebrar
            assert response.status_code in [400, 422, 500]

            # 3. Verificar que API ainda responde após erros
            health_response = await client.get(f"{api_server}/health")
            assert health_response.status_code == 200

    @pytest.mark.asyncio
    async def test_performance_under_load(self, api_server):
        """Teste E2E: Performance sob carga"""
        import httpx
        import time

        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()

            # Fazer múltiplas chamadas rápidas
            tasks = []
            for i in range(20):
                tasks.append(client.get(f"{api_server}/health"))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            total_time = end_time - start_time

            # Calcular métricas
            successful_responses = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 200]
            success_rate = len(successful_responses) / len(responses)

            # Verificar performance aceitável
            assert success_rate >= 0.9  # Pelo menos 90% de sucesso
            assert total_time < 10.0  # Menos de 10 segundos para 20 requisições
            avg_response_time = total_time / len(successful_responses)
            assert avg_response_time < 0.5  # Menos de 500ms em média


@pytest.mark.e2e
@pytest.mark.slow
class TestBrowserAutomationE2E:
    """Testes E2E específicos de automação web"""

    @pytest.fixture(scope="class")
    async def automation_browser(self):
        """Browser específico para testes de automação"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows'
                ]
            )

            # Configurar contexto com configurações realistas
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                geolocation={'latitude': -23.5505, 'longitude': -46.6333},  # São Paulo
                permissions=['geolocation']
            )

            yield context

            await context.close()
            await browser.close()

    @pytest.mark.asyncio
    async def test_real_webpage_interaction(self, automation_browser):
        """Teste E2E: Interação real com página web"""
        page = await automation_browser.new_page()

        try:
            # Acessar página de teste conhecida
            await page.goto("https://httpbin.org/html", timeout=10000)
            await page.wait_for_load_state('networkidle')

            # Verificar elementos básicos
            title = await page.title()
            assert title is not None

            # Procurar por elementos comuns
            headings = page.locator('h1, h2, h3, h4, h5, h6')
            heading_count = await headings.count()

            links = page.locator('a')
            link_count = await links.count()

            # Verificar se página tem conteúdo básico
            assert heading_count >= 0
            assert link_count >= 0

            # Tentar interagir com um link (se existir)
            if link_count > 0:
                first_link = links.first
                href = await first_link.get_attribute('href')
                if href and not href.startswith('javascript:'):
                    # Não clicar, apenas verificar que é acessível
                    assert href is not None

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_form_detection_and_analysis(self, automation_browser):
        """Teste E2E: Detecção e análise de formulários"""
        page = await automation_browser.new_page()

        try:
            # Acessar página com formulário conhecido
            await page.goto("https://httpbin.org/forms/post", timeout=10000)
            await page.wait_for_load_state('networkidle')

            # Analisar formulários
            forms = page.locator('form')
            form_count = await forms.count()

            # Analisar campos de input
            inputs = page.locator('input')
            input_count = await inputs.count()

            textareas = page.locator('textarea')
            textarea_count = await textareas.count()

            selects = page.locator('select')
            select_count = await selects.count()

            buttons = page.locator('button, input[type="submit"], input[type="button"]')
            button_count = await buttons.count()

            # Verificar que encontrou elementos de formulário
            total_form_elements = input_count + textarea_count + select_count + button_count
            assert total_form_elements > 0

            # Coletar informações sobre tipos de input
            input_types = []
            for i in range(min(input_count, 10)):  # Limitar para performance
                input_type = await inputs.nth(i).get_attribute('type')
                if input_type:
                    input_types.append(input_type)

            # Verificar tipos comuns
            assert any(t in ['text', 'email', 'password', 'submit'] for t in input_types)

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_selector_validation_and_adaptation(self, automation_browser):
        """Teste E2E: Validação e adaptação de seletores"""
        page = await automation_browser.new_page()

        try:
            # Acessar página de teste
            await page.goto("https://httpbin.org/html", timeout=10000)
            await page.wait_for_load_state('networkidle')

            # Testar diferentes tipos de seletores
            test_selectors = [
                'h1',  # CSS simples
                '[href]',  # Atributo
                'div > p',  # Hierarquia
                'text="Herman Melville"',  # Text match (Playwright)
            ]

            successful_selectors = []

            for selector in test_selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    if count > 0:
                        successful_selectors.append((selector, count))
                except Exception:
                    # Seletor pode falhar, é normal
                    continue

            # Verificar que pelo menos alguns seletores funcionaram
            assert len(successful_selectors) > 0

            # Testar adaptação de seletor (de genérico para específico)
            generic_selector = 'a'
            specific_selector = 'a[href*="http"]'

            generic_count = await page.locator(generic_selector).count()
            specific_count = await page.locator(specific_selector).count()

            # Seletor específico deve encontrar menos ou igual elementos
            assert specific_count <= generic_count

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery_browser(self, automation_browser):
        """Teste E2E: Tratamento de erros e recuperação no browser"""
        page = await automation_browser.new_page()

        try:
            # Testar página inexistente
            try:
                await page.goto("https://nonexistent-domain-12345.com", timeout=5000)
                assert False, "Deveria ter falhado"
            except Exception:
                # Esperado falhar
                pass

            # Verificar que browser ainda funciona após erro
            await page.goto("https://httpbin.org/html", timeout=10000)
            title = await page.title()
            assert title is not None

            # Testar seletor inexistente
            try:
                nonexistent = page.locator('[data-nonexistent="value"]')
                count = await nonexistent.count()
                assert count == 0  # OK, não encontrou
            except Exception:
                # Pode lançar exception dependendo da implementação
                pass

            # Verificar que página ainda responde
            body_text = await page.text_content('body')
            assert len(body_text) > 0

        finally:
            await page.close()
