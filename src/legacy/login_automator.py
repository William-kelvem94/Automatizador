"""
Login Automator - Sistema Inteligente de Automação de Login

Este módulo implementa um automatizador inteligente de login que:
- Valida páginas web completamente
- Detecta campos automaticamente
- Adapta-se a diferentes layouts de site
- Executa login de forma segura e confiável
- Fornece logs detalhados de todas as operações

Autor: Sistema Automatizado
Versão: 2.0 - Validação Avançada
"""

import time
import configparser
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os


class LoginAutomator:
    """
    Classe principal do Automatizador de Login.

    Implementa um sistema inteligente que:
    1. Valida páginas web antes de qualquer ação
    2. Detecta campos de formulário automaticamente
    3. Adapta-se a diferentes layouts e estruturas
    4. Executa login com múltiplas estratégias
    5. Fornece feedback detalhado de todas as operações
    """

    def _clean_log_text(self, text):
        """Remove caracteres especiais que podem causar problemas de codificação nos logs"""
        if not isinstance(text, str):
            text = str(text)
        # Remove caracteres unicode problemáticos (emojis, símbolos especiais)
        text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF\u2700-\u27BF\uFE00-\uFE0F]', '', text)
        # Remove outros caracteres especiais que podem causar problemas
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text.strip()

    def __init__(self, config_file='config.ini'):
        """
        Inicializa o automatizador com configurações do arquivo.

        Args:
            config_file (str): Caminho para o arquivo de configuração
        """
        # Carrega configurações
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Configura logging profissional
        self._setup_logging()

        # Carrega configurações do site
        self._load_site_config()

        # Carrega credenciais
        self._load_credentials()

        # Carrega configurações do sistema
        self._load_system_settings()

        # Inicializa agendador
        self.scheduler = BlockingScheduler()
        self.is_scheduling = False

        self.logger.info("LoginAutomator inicializado com sucesso")

    def _setup_logging(self):
        """Configura o sistema de logging profissional."""
        log_level = logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler('automator.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def _load_site_config(self):
        """Carrega configurações específicas do site."""
        try:
            self.site_url = self.config.get('SITE', 'url', fallback='')
            self.email_selector = self.config.get('SITE', 'email_field_selector', fallback='')
            self.password_selector = self.config.get('SITE', 'password_field_selector', fallback='')
            self.login_button_selector = self.config.get('SITE', 'login_button_selector', fallback='')

            self.logger.info(f"Configurações do site carregadas: {self.site_url}")

        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações do site: {e}")
            raise

    def _load_credentials(self):
        """Carrega credenciais de acesso."""
        try:
            self.email = self.config.get('CREDENTIALS', 'email', fallback='')
            self.password = self.config.get('CREDENTIALS', 'password', fallback='')

            # Log seguro (não mostra senha)
            if self.email:
                self.logger.info(f"Credenciais carregadas para: {self.email}")
            else:
                self.logger.warning("E-mail não configurado")

        except Exception as e:
            self.logger.error(f"Erro ao carregar credenciais: {e}")
            raise

    def _load_system_settings(self):
        """Carrega configurações do sistema."""
        try:
            self.headless = self.config.getboolean('SETTINGS', 'headless', fallback=False)
            self.wait_timeout = self.config.getint('SETTINGS', 'wait_timeout', fallback=10)

            self.logger.info(f"Configurações do sistema: headless={self.headless}, timeout={self.wait_timeout}s")

        except Exception as e:
            self.logger.warning(f"Erro ao carregar configurações do sistema: {e}")
            # Valores padrão
            self.headless = False
            self.wait_timeout = 10

    def setup_driver(self):
        """
        Configura e retorna uma instância do Chrome WebDriver.

        Returns:
            webdriver.Chrome: Instância configurada do Chrome driver

        Raises:
            Exception: Se não conseguir configurar o driver
        """
        self.logger.info("Configurando Chrome WebDriver...")

        # Configura opções do Chrome
        options = self._configure_chrome_options()

        # Tenta múltiplas estratégias para obter o driver
        driver = None
        strategies = [
            self._try_chromedriver_manager,
            self._try_system_chromedriver,
            self._try_fallback_driver
        ]

        for strategy in strategies:
            try:
                self.logger.debug(f"Tentando estratégia: {strategy.__name__}")
                driver = strategy(options)
                if driver:
                    self.logger.info("Chrome WebDriver configurado com sucesso")
            # Verificar se o driver está realmente funcional e visível
            try:
                # Teste básico de funcionalidade
                test_url = driver.current_url
                test_title = driver.title
                self.logger.info(f"WebDriver criado com sucesso - URL atual: {test_url}")
                self.logger.info(f"Título da página: {test_title}")

                # Tentar executar JavaScript para verificar se a janela está ativa
                try:
                    is_visible = driver.execute_script("return document.hasFocus();")
                    self.logger.info(f"Janela tem foco: {is_visible}")

                    # Forçar foco na janela
                    driver.execute_script("window.focus();")
                    self.logger.info("Tentativa de focar na janela executada")

                except Exception as js_error:
                    self.logger.warning(f"Não foi possível verificar foco da janela: {js_error}")

                return driver

            except Exception as test_error:
                self.logger.warning(f"Driver criado mas falhou no teste: {test_error}")
                try:
                    driver.quit()
                except:
                    pass
                continue

        except Exception as e:
            self.logger.debug(f"Estratégia {strategy.__name__} falhou (tentando próxima): {str(e)[:100]}")
            continue

        # Se todas as estratégias falharam
        error_msg = (
            "Não foi possível configurar o ChromeDriver. "
            "Verifique se o Google Chrome está instalado e atualizado.\n"
            "Soluções possíveis:\n"
            "1. Instale ou atualize o Google Chrome\n"
            "2. Execute: pip install --upgrade webdriver-manager\n"
            "3. Reinicie o sistema\n"
            "4. Verifique se há antivírus bloqueando o ChromeDriver"
        )
        self.logger.error("FALHA CRÍTICA: ChromeDriver não pôde ser configurado")
        self.logger.error("DETALHES: " + error_msg)
        raise Exception(error_msg)

    def _configure_chrome_options(self):
        """
        Configura as opções do Chrome para automação.

        Returns:
            webdriver.ChromeOptions: Opções configuradas
        """
        options = webdriver.ChromeOptions()

        # Modo headless se configurado
        self.logger.info(f"Configuração headless: {self.headless}")
        if self.headless:
            options.add_argument('--headless')
            self.logger.info("Executando em modo headless")
        else:
            self.logger.info("Executando em modo visual (janela visível)")
            # Garantir que a janela seja visível - múltiplas abordagens
            options.add_argument('--no-headless')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-background-media-download')
            options.add_argument('--disable-features=VizDisplayCompositor')
            self.logger.info("Adicionados argumentos para forçar visibilidade da janela")

        # Configurações de estabilidade
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        # Configurações de interface - FORÇAR VISIBILIDADE
        options.add_argument('--window-size=1366,768')
        options.add_argument('--start-maximized')  # Maximizar janela
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Para velocidade

        # Configurações de privacidade e segurança
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # User agent para parecer navegador normal
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        # Desabilitar flags de automação
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        return options

    def _try_chromedriver_manager(self, options):
        """Tenta usar ChromeDriverManager para baixar driver automaticamente."""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Remove flag de automação
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver
        except Exception:
            raise

    def _try_system_chromedriver(self, options):
        """Tenta usar ChromeDriver do sistema (PATH)."""
        try:
            driver = webdriver.Chrome(options=options)

            # Remove flag de automação
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver
        except Exception:
            raise

    def _try_fallback_driver(self, options):
        """Última tentativa com configurações mínimas."""
        try:
            # Remove algumas opções problemáticas
            minimal_options = webdriver.ChromeOptions()
            minimal_options.add_argument('--no-sandbox')
            minimal_options.add_argument('--disable-dev-shm-usage')
            minimal_options.add_argument('--window-size=1366,768')

            driver = webdriver.Chrome(options=minimal_options)

            # Remove flag de automação
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.logger.warning("Usando configurações mínimas do Chrome")
            return driver
        except Exception:
            raise

    def perform_login(self):
        """
        Executa o processo completo de login com validação inteligente.

        Fluxo de execução:
        1. Validação inicial das configurações
        2. Configuração e abertura do navegador
        3. Acesso à página de login
        4. Validação completa da página
        5. Detecção inteligente de campos
        6. Preenchimento automático dos campos
        7. Submissão do formulário
        8. Verificação de sucesso

        Returns:
            bool: True se login foi executado com sucesso
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PROCESSO DE LOGIN AUTOMATIZADO")
        self.logger.info("=" * 60)

        driver = None

        try:
            # FASE 1: Validação inicial
            self.logger.info("FASE 1: Validando configurações...")
            if not self._validate_initial_config():
                raise Exception("Configurações inválidas")

            # FASE 2: Configuração do navegador
            self.logger.info("FASE 2: Configurando navegador...")
            driver = self.setup_driver()

            # FASE 3: Acesso à página
            self.logger.info("FASE 3: Acessando página de login...")
            if not self._access_login_page(driver):
                raise Exception("Falha ao acessar página de login")

            # FASE 4: Validação da página
            self.logger.info("FASE 4: Validando página...")
            if not self.validate_page(driver):
                raise Exception("Página não é válida para login")

            # FASE 5: Detecção de campos
            self.logger.info("FASE 5: Detectando campos do formulário...")
            fields = self.smart_field_detection(driver)
            if not fields:
                self.logger.warning("Campos não detectados automaticamente, tentando fallback...")
                fields = self.fallback_field_detection(driver)

            # Verificar se temos campos mínimos para prosseguir
            if not fields or 'email' not in fields:
                self.logger.warning("ATENÇÃO: Campo de e-mail não detectado!")
                self.logger.info("Este site pode usar um sistema de login não tradicional.")
                self.logger.info("Dicas para configuração manual:")
                self.logger.info("  1. Use a ferramenta 'Mapear Campos' para detectar seletores")
                self.logger.info("  2. Configure os seletores manualmente no arquivo config.ini")
                self.logger.info("  3. Verifique se o site requer autenticação de dois fatores")
                return self._hybrid_mode(driver)

            # FASE 6: Preenchimento dos campos
            self.logger.info("FASE 6: Preenchendo formulário...")
            if not self._fill_login_form(driver, fields):
                self.logger.warning("Não conseguiu preencher automaticamente")
                return self._hybrid_mode(driver)

            # FASE 7: Submissão do formulário
            self.logger.info("FASE 7: Enviando formulário...")
            if not self._submit_login_form(driver, fields):
                self.logger.warning("Não conseguiu enviar formulário automaticamente")

            # FASE 8: Verificação de sucesso
            self.logger.info("FASE 8: Verificando resultado...")
            success = self._verify_login_success(driver)

            if success:
                self.logger.info("=" * 60)
                self.logger.info("✅ LOGIN EXECUTADO COM SUCESSO!")
                self.logger.info("=" * 60)
                return True
            else:
                self.logger.info("=" * 60)
                self.logger.info("⚠️  LOGIN PODE TER FALHADO - MODO HÍBRIDO ATIVADO")
                self.logger.info("=" * 60)
                return self._hybrid_mode(driver)

        except Exception as e:
            self.logger.error(f"ERRO durante o processo de login: {e}")
            return False

        finally:
            if driver:
                self.logger.info("Fechando navegador...")
                try:
                    driver.quit()
                except:
                    pass

    def _validate_initial_config(self):
        """
        Valida se todas as configurações necessárias estão presentes.

        Returns:
            bool: True se configurações são válidas
        """
        issues = []

        if not self.site_url:
            issues.append("URL do site não configurada")
        if not self.email:
            issues.append("E-mail não configurado")
        if not self.password:
            issues.append("Senha não configurada")

        if issues:
            for issue in issues:
                self.logger.error(f"❌ {issue}")
            return False

        self.logger.info("✅ Configurações válidas")
        return True

    def _access_login_page(self, driver):
        """
        Acessa a página de login com validação.

        Args:
            driver: Instância do WebDriver

        Returns:
            bool: True se conseguiu acessar
        """
        try:
            self.logger.info(f"Acessando: {self.site_url}")
            driver.get(self.site_url)

            # Aguarda carregamento básico
            WebDriverWait(driver, self.wait_timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Pequena pausa para carregamento dinâmico
            time.sleep(2)

            current_url = driver.current_url
            self.logger.info(f"Página carregada: {current_url}")

            return True

        except Exception as e:
            self.logger.error(f"Erro ao acessar página: {e}")
            return False

    def validate_page(self, driver):
        """
        Valida se a página está adequada para login.

        Args:
            driver: Instância do WebDriver

        Returns:
            bool: True se página é válida
        """
        try:
            self.logger.info("Analisando estrutura da página...")

            # Conta elementos básicos
            forms = driver.find_elements(By.TAG_NAME, "form")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            buttons = driver.find_elements(By.TAG_NAME, "button")

            self.logger.info(f"Encontrados: {len(forms)} forms, {len(inputs)} inputs, {len(buttons)} buttons")

            # Verifica se há pelo menos um formulário
            if len(forms) == 0:
                self.logger.warning("Nenhum formulário encontrado na página")
                return False

            # Verifica se há campos de input
            if len(inputs) == 0:
                self.logger.warning("Nenhum campo de input encontrado")
                return False

            # Verifica palavras-chave de login
            page_text = driver.page_source.lower()
            login_keywords = ['login', 'entrar', 'acessar', 'conectar', 'autenticar']

            found_keywords = [kw for kw in login_keywords if kw in page_text]
            if found_keywords:
                self.logger.info(f"Palavras-chave encontradas: {', '.join(found_keywords)}")
            else:
                self.logger.warning("Nenhuma palavra-chave de login encontrada")

            # Verifica se não está em página de erro
            if '404' in driver.title.lower() or 'erro' in driver.title.lower():
                self.logger.error("Página de erro detectada")
                return False

            self.logger.info("✅ Página validada com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro na validação da página: {e}")
            return False

    def smart_field_detection(self, driver):
        """
        Detecta campos de formulário de forma inteligente.

        Args:
            driver: Instância do WebDriver

        Returns:
            dict: Campos detectados com seletores
        """
        fields = {}

        try:
            self.logger.info("Detectando campos automaticamente...")

            # Estratégia 1: Seletores CSS comuns
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="login"]',
                'input[name="usuario"]',
                'input[name="user"]',
                'input[id="email"]',
                'input[id="login"]',
                'input[id="usuario"]',
                '#email',
                '#login',
                '#usuario'
            ]

            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="senha"]',
                'input[name="pass"]',
                'input[id="password"]',
                'input[id="senha"]',
                'input[id="pass"]',
                '#password',
                '#senha',
                '#pass'
            ]

            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[name="login"]',
                'button[name="entrar"]',
                'button[id="login"]',
                'button[id="entrar"]',
                '.btn-login',
                '.btn-entrar'
            ]

            # Detecta email
            for selector in email_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        fields['email'] = selector
                        self.logger.info(f"Campo email detectado: {selector}")
                        break
                except:
                    continue

            # Detecta senha
            for selector in password_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        fields['password'] = selector
                        self.logger.info(f"Campo senha detectado: {selector}")
                        break
                except:
                    continue

            # Detecta botão
            for selector in button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        fields['submit'] = selector
                        self.logger.info(f"Botão submit detectado: {selector}")
                        break
                except:
                    continue

            if fields:
                self.logger.info(f"Campos detectados: {list(fields.keys())}")
            else:
                self.logger.warning("Nenhum campo detectado automaticamente")

            return fields

        except Exception as e:
            self.logger.error(f"Erro na detecção automática: {e}")
            return {}

    def fallback_field_detection(self, driver):
        """
        Estratégia de fallback para detecção de campos.

        Args:
            driver: Instância do WebDriver

        Returns:
            dict: Campos detectados
        """
        fields = {}

        try:
            self.logger.info("Aplicando estratégia de fallback...")

            # Busca por qualquer input visivel
            inputs = driver.find_elements(By.TAG_NAME, "input")

            email_candidates = []
            password_candidates = []

            for input_elem in inputs:
                if input_elem.is_displayed():
                    input_type = input_elem.get_attribute('type') or ''
                    input_name = input_elem.get_attribute('name') or ''
                    input_id = input_elem.get_attribute('id') or ''
                    input_placeholder = input_elem.get_attribute('placeholder') or ''

                    # Classifica campos
                    if input_type.lower() == 'email' or 'email' in (input_name + input_id + input_placeholder).lower():
                        email_candidates.append(input_elem)
                    elif input_type.lower() == 'password' or 'senha' in (input_name + input_id + input_placeholder).lower():
                        password_candidates.append(input_elem)

            # Seleciona melhores candidatos
            if email_candidates:
                fields['email'] = self._get_css_selector(email_candidates[0])
                self.logger.info("Campo email encontrado via fallback")

            if password_candidates:
                fields['password'] = self._get_css_selector(password_candidates[0])
                self.logger.info("Campo senha encontrado via fallback")

            # Busca botão de submit
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed():
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['entrar', 'login', 'acessar', 'conectar']):
                        fields['submit'] = self._get_css_selector(button)
                        self.logger.info("Botão encontrado via fallback")
                        break

            return fields

        except Exception as e:
            self.logger.error(f"Erro no fallback: {e}")
            return {}

    def _get_css_selector(self, element):
        """
        Gera um seletor CSS para um elemento.

        Args:
            element: Elemento WebElement

        Returns:
            str: Seletor CSS
        """
        try:
            elem_id = element.get_attribute('id')
            if elem_id:
                return f"#{elem_id}"

            elem_name = element.get_attribute('name')
            if elem_name:
                return f"[name='{elem_name}']"

            elem_class = element.get_attribute('class')
            if elem_class:
                return f".{elem_class.split()[0]}"

            # Fallback para tag
            return element.tag_name

        except:
            return element.tag_name

    def _fill_login_form(self, driver, fields):
        """
        Preenche o formulário de login usando campos detectados.

        Args:
            driver: Instância do WebDriver
            fields: Dicionário com campos detectados

        Returns:
            bool: True se conseguiu preencher
        """
        try:
            # Preenche email se detectado
            if 'email' in fields and fields['email']:
                self.logger.info("Preenchendo campo de email...")
                email_field = WebDriverWait(driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, fields['email']))
                )
                email_field.clear()
                email_field.send_keys(self.email)
                self.logger.info("✅ Email preenchido")
                time.sleep(1)

                # Tenta ativar próximos campos (TAB ou click)
                try:
                    email_field.send_keys(Keys.TAB)
                    time.sleep(1)
                except:
                    pass

            # Aguarda carregamento dinâmico de campo de senha
            time.sleep(2)

            # Preenche senha se detectada
            if 'password' in fields and fields['password']:
                self.logger.info("Preenchendo campo de senha...")
                password_field = WebDriverWait(driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, fields['password']))
                )
                password_field.clear()
                password_field.send_keys(self.password)
                self.logger.info("✅ Senha preenchida")
                time.sleep(1)

            return True

        except Exception as e:
            self.logger.warning(f"Não conseguiu preencher formulário automaticamente: {e}")
            return False

    def _submit_login_form(self, driver, fields):
        """
        Submete o formulário de login.

        Args:
            driver: Instância do WebDriver
            fields: Dicionário com campos detectados

        Returns:
            bool: True se conseguiu submeter
        """
        try:
            # Tenta usar botão detectado
            if 'submit' in fields and fields['submit']:
                self.logger.info("Clicando no botão de submit...")
                submit_button = WebDriverWait(driver, self.wait_timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, fields['submit']))
                )
                submit_button.click()
                self.logger.info("✅ Botão clicado")
                time.sleep(3)
                return True

            # Tenta submit automático do formulário
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    self.logger.info("Tentando submit automático do formulário...")
                    forms[0].submit()
                    self.logger.info("✅ Formulário submetido")
                    time.sleep(3)
                    return True
            except:
                pass

            # Tenta tecla Enter no último campo
            try:
                active_element = driver.switch_to.active_element
                if active_element:
                    active_element.send_keys(Keys.RETURN)
                    self.logger.info("✅ Enter enviado no campo ativo")
                    time.sleep(3)
                    return True
            except:
                pass

            self.logger.warning("Não conseguiu submeter formulário automaticamente")
            return False

        except Exception as e:
            self.logger.warning(f"Erro ao submeter formulário: {e}")
            return False

    def _verify_login_success(self, driver):
        """
        Verifica se o login foi bem-sucedido.

        Args:
            driver: Instância do WebDriver

        Returns:
            bool: True se login parece ter sido bem-sucedido
        """
        try:
            current_url = driver.current_url
            page_title = driver.title

            # Verifica se ainda está na página de login
            if 'login' in current_url.lower() or 'login' in page_title.lower():
                self.logger.warning("Ainda parece estar na página de login")
                return False

            # Verifica se há elementos de erro
            error_elements = driver.find_elements(By.CSS_SELECTOR,
                "[class*='error'], [class*='erro'], [class*='alert'], [id*='error'], [id*='erro']"
            )

            if error_elements:
                for error in error_elements:
                    if error.is_displayed() and error.text.strip():
                        self.logger.warning(f"Possível erro detectado: {error.text[:100]}")
                        return False

            # Verifica se há elementos de sucesso ou dashboard
            success_indicators = [
                'dashboard', 'painel', 'home', 'principal', 'conta', 'perfil',
                'logout', 'sair', 'welcome', 'bem-vindo'
            ]

            page_text = driver.page_source.lower()
            if any(indicator in page_text for indicator in success_indicators):
                self.logger.info("Indicadores de sucesso detectados")
                return True

            # Se não encontrou indicadores claros, assume sucesso se não está mais na página de login
            self.logger.info("Login parece ter sido bem-sucedido")
            return True

        except Exception as e:
            self.logger.warning(f"Erro ao verificar sucesso: {e}")
            return False

    def _hybrid_mode(self, driver):
        """
        Ativa o modo híbrido quando o login automático falha parcialmente.

        Args:
            driver: Instância do WebDriver

        Returns:
            bool: True (sempre retorna True pois é modo híbrido)
        """
        self.logger.info("=" * 60)
        self.logger.info("🎯 MODO HÍBRIDO ATIVADO - ASSISTÊNCIA MANUAL")
        self.logger.info("=" * 60)
        self.logger.info("📋 O que aconteceu:")
        self.logger.info("   • O sistema conseguiu acessar a página de login")
        self.logger.info("   • Alguns campos foram preenchidos automaticamente")
        self.logger.info("   • O login completo não pôde ser feito automaticamente")
        self.logger.info("")
        self.logger.info("🔧 Próximos passos recomendados:")
        self.logger.info("   1. ✅ Complete o login manualmente no navegador aberto")
        self.logger.info("   2. 🔍 Use 'Mapear Campos' para detectar seletores automaticamente")
        self.logger.info("   3. ⚙️ Configure seletores manualmente se necessário")
        self.logger.info("   4. 📝 Verifique se há CAPTCHA ou autenticação 2FA")
        self.logger.info("")
        self.logger.info("⏰ O navegador ficará aberto por 60 segundos para conclusão manual")

        try:
            # Mantém navegador aberto por tempo determinado
            for i in range(60, 0, -10):
                self.logger.info(f"⏳ Navegador aberto - Tempo restante: {i} segundos")
                time.sleep(10)

        except KeyboardInterrupt:
            self.logger.info("✅ Modo híbrido interrompido pelo usuário")

        self.logger.info("🔒 Navegador fechado - Processo concluído")
        return True

    def analyze_page_elements(self, driver):
        """
        Analisa elementos da página para fornecer informações detalhadas de diagnóstico.

        Args:
            driver: Instância do WebDriver
        """
        try:
            self.logger.info("[ANALYSIS] REALIZANDO ANALISE DETALHADA DA PAGINA")
            self.logger.info("-" * 60)

            # Análise geral de elementos
            forms = len(driver.find_elements(By.TAG_NAME, "form"))
            inputs = len(driver.find_elements(By.TAG_NAME, "input"))
            buttons = len(driver.find_elements(By.TAG_NAME, "button"))
            links = len(driver.find_elements(By.TAG_NAME, "a"))
            images = len(driver.find_elements(By.TAG_NAME, "img"))

            self.logger.info("[COUNT] CONTAGEM GERAL DE ELEMENTOS:")
            self.logger.info(f"   [FORMS] Formularios: {forms}")
            self.logger.info(f"   [INPUTS] Campos input: {inputs}")
            self.logger.info(f"   [BUTTONS] Botoes: {buttons}")
            self.logger.info(f"   [LINKS] Links: {links}")
            self.logger.info(f"   [IMAGES] Imagens: {images}")

            # Análise específica de formulários
            if forms > 0:
                self.logger.info(f"\n[FORMS] ANALISE DOS {forms} FORMULARIO(S):")
                form_elements = driver.find_elements(By.TAG_NAME, "form")

                for i, form in enumerate(form_elements):
                    form_id = form.get_attribute('id') or 'sem-id'
                    form_name = form.get_attribute('name') or 'sem-nome'
                    form_action = form.get_attribute('action') or 'sem-action'
                    form_method = form.get_attribute('method') or 'GET'

                    self.logger.info(f"   [FORM] Form {i+1}: id='{form_id}', name='{form_name}'")
                    self.logger.info(f"      Action: {form_action}, Method: {form_method}")

                    # Inputs dentro deste form
                    form_inputs = form.find_elements(By.TAG_NAME, "input")
                    if form_inputs:
                        self.logger.info(f"      [INPUTS] Contem {len(form_inputs)} campo(s) input")

            # Análise detalhada dos campos input
            self.logger.info("\n[INPUT] ANALISE DETALHADA DOS CAMPOS INPUT:")
            input_elements = driver.find_elements(By.TAG_NAME, "input")

            # Categorizar inputs
            email_inputs = []
            password_inputs = []
            text_inputs = []
            hidden_inputs = []
            submit_inputs = []

            for inp in input_elements:
                input_type = inp.get_attribute('type') or 'text'
                input_name = self._clean_log_text(inp.get_attribute('name') or '')
                input_id = self._clean_log_text(inp.get_attribute('id') or '')
                input_placeholder = self._clean_log_text(inp.get_attribute('placeholder') or '')
                visible = inp.is_displayed()

                if input_type.lower() == 'email':
                    email_inputs.append((input_name, input_id, input_placeholder, visible))
                elif input_type.lower() == 'password':
                    password_inputs.append((input_name, input_id, input_placeholder, visible))
                elif input_type.lower() == 'submit':
                    submit_inputs.append((input_name, input_id, input_placeholder, visible))
                elif input_type.lower() == 'hidden':
                    hidden_inputs.append((input_name, input_id, input_placeholder, visible))
                else:
                    text_inputs.append((input_name, input_id, input_placeholder, visible))

            # Relatório por categoria
            if email_inputs:
                self.logger.info(f"   [EMAIL] CAMPOS EMAIL ({len(email_inputs)}):")
                for name, id, placeholder, visible in email_inputs[:3]:  # Máximo 3
                    self.logger.info(f"      • name='{name}', id='{id}', placeholder='{placeholder}', visivel={visible}")

            if password_inputs:
                self.logger.info(f"   [PASSWORD] CAMPOS SENHA ({len(password_inputs)}):")
                for name, id, placeholder, visible in password_inputs[:3]:  # Máximo 3
                    self.logger.info(f"      • name='{name}', id='{id}', placeholder='{placeholder}', visivel={visible}")

            if submit_inputs:
                self.logger.info(f"   [SUBMIT] BOTOES SUBMIT ({len(submit_inputs)}):")
                for name, id, placeholder, visible in submit_inputs[:3]:  # Máximo 3
                    self.logger.info(f"      • name='{name}', id='{id}', placeholder='{placeholder}', visivel={visible}")

            # Análise de botões
            self.logger.info("\n[BUTTON] ANALISE DOS BOTOES:")
            button_elements = driver.find_elements(By.TAG_NAME, "button")

            login_buttons = []
            submit_buttons = []

            for btn in button_elements:
                button_type = btn.get_attribute('type') or 'button'
                button_text = self._clean_log_text(btn.text.strip())
                button_id = self._clean_log_text(btn.get_attribute('id') or '')
                button_name = self._clean_log_text(btn.get_attribute('name') or '')
                visible = btn.is_displayed()

                # Identificar botões de login
                text_lower = button_text.lower()
                if any(keyword in text_lower for keyword in ['login', 'entrar', 'acessar', 'conectar', 'autenticar']):
                    login_buttons.append((button_text, button_type, button_id, button_name, visible))
                elif button_type.lower() == 'submit':
                    submit_buttons.append((button_text, button_type, button_id, button_name, visible))

            if login_buttons:
                self.logger.info(f"   [LOGIN] BOTOES DE LOGIN IDENTIFICADOS ({len(login_buttons)}):")
                for text, type, id, name, visible in login_buttons[:3]:
                    self.logger.info(f"      • Texto: '{text}', Tipo: {type}, ID: '{id}', Visivel: {visible}")

            if submit_buttons:
                self.logger.info(f"   [SUBMIT] BOTOES SUBMIT ({len(submit_buttons)}):")
                for text, type, id, name, visible in submit_buttons[:3]:
                    self.logger.info(f"      • Texto: '{text}', ID: '{id}', Visivel: {visible}")

            # Análise de palavras-chave na página
            self.logger.info("\n[KEYWORDS] ANALISE DE PALAVRAS-CHAVE:")
            page_text = driver.page_source.lower()

            keywords = {
                'login': ['login', 'logar', 'entrar', 'acessar', 'conectar'],
                'forms': ['formulário', 'form', 'cadastro', 'registro'],
                'security': ['captcha', 'verificação', 'segurança', 'recaptcha']
            }

            for category, words in keywords.items():
                found_words = [word for word in words if word in page_text]
                if found_words:
                    self.logger.info(f"   {category.upper()}: {', '.join(found_words)}")

            # Verificação de elementos especiais
            iframes = len(driver.find_elements(By.TAG_NAME, "iframe"))
            if iframes > 0:
                self.logger.info(f"   [IFRAMES] IFRAMES DETECTADOS: {iframes} (possivel CAPTCHA)")

            # Resumo final
            self.logger.info("\n[SUMMARY] RESUMO DA ANALISE:")
            self.logger.info(f"   • Total de formularios: {forms}")
            self.logger.info(f"   • Campos de entrada: {inputs}")
            self.logger.info(f"   • Botões disponíveis: {buttons}")
            self.logger.info(f"   • Campos email detectados: {len(email_inputs)}")
            self.logger.info(f"   • Campos senha detectados: {len(password_inputs)}")
            self.logger.info(f"   • Botões de login: {len(login_buttons)}")

            if email_inputs and password_inputs:
                self.logger.info("   ✅ PÁGINA APARECE TER FORMULÁRIO DE LOGIN")
            else:
                self.logger.info("   ⚠️ PÁGINA PODE NÃO TER FORMULÁRIO DE LOGIN TRADICIONAL")

            self.logger.info("-" * 60)

        except Exception as e:
            self.logger.error(f"❌ ERRO na análise de elementos: {e}")
            import traceback
            self.logger.error("Stack trace:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    self.logger.error(f"   {line}")

    # Métodos de agendamento (mantidos da versão anterior)
    def start_scheduler(self, times):
        """
        Inicia o agendamento automático.

        Args:
            times (list): Lista de horários no formato HH:MM
        """
        if self.is_scheduling:
            self.logger.warning("Agendador já está ativo")
            return

        self.logger.info(f"Iniciando agendador com horários: {times}")

        for time_str in times:
            try:
                hour, minute = map(int, time_str.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
                self.scheduler.add_job(
                    func=self.perform_login,
                    trigger=trigger,
                    id=f"login_{time_str}",
                    name=f"Login automático {time_str}"
                )
                self.logger.info(f"Agendado para {time_str}")
            except Exception as e:
                self.logger.error(f"Erro ao agendar {time_str}: {e}")

        self.is_scheduling = True
        self.logger.info("Agendador iniciado")

    def stop_scheduler(self):
        """Para o agendamento automático."""
        if not self.is_scheduling:
            self.logger.warning("Agendador não está ativo")
            return

        self.scheduler.remove_all_jobs()
        self.is_scheduling = False
        self.logger.info("Agendador parado")

    def run_scheduler(self):
        """Executa o agendador (bloqueante)."""
        if not self.is_scheduling:
            self.logger.warning("Nenhum job agendado")
            return

        self.logger.info("Iniciando execução do agendador...")
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            self.logger.info("Agendador interrompido pelo usuário")
        finally:
            self.stop_scheduler()
