"""
Motor de Navegação Inteligente
Gerencia instâncias do navegador com configurações otimizadas
"""

import logging
import time
from typing import Any, Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BrowserEngine:
    """Motor inteligente para gerenciamento de navegadores"""

    def __init__(self, headless: bool = False, config: Optional[Dict[str, Any]] = None):
        self.headless = headless
        self.config = config or {}
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def create_driver(self) -> webdriver.Chrome:
        """Cria uma instância otimizada do Chrome WebDriver"""
        self.logger.info("Inicializando Chrome WebDriver...")

        options = self._configure_chrome_options()
        service = Service(ChromeDriverManager().install())

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self._optimize_driver()
            self.logger.info("Chrome WebDriver inicializado com sucesso")
            return self.driver
        except Exception as e:
            self.logger.error(f"Falha ao criar WebDriver: {e}")
            raise

    def _configure_chrome_options(self) -> Options:
        """Configura opções avançadas do Chrome"""
        options = Options()

        # Modo de execução
        if self.headless:
            options.add_argument("--headless=new")  # Novo modo headless
            self.logger.info("Executando em modo headless")
        else:
            # Configurações para máxima visibilidade
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            self.logger.info("Executando em modo visual com máxima visibilidade")

        # Configurações de performance e estabilidade
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Para velocidade
        options.add_argument(
            "--disable-javascript"
        )  # Desabilitado por padrão, habilitado quando necessário

        # User agent moderno
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        # Janela otimizada
        options.add_argument("--window-size=1366,768")

        # Perfis e privacidade
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Remover flag de automação
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def _optimize_driver(self):
        """Otimiza a instância do driver após criação"""
        if not self.driver:
            return

        try:
            # Remove webdriver property
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # Configura timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)

            # Maximiza se não headless
            if not self.headless:
                self.driver.maximize_window()

        except Exception as e:
            self.logger.warning(f"Erro na otimização do driver: {e}")

    def navigate_to(self, url: str, wait_for_load: bool = True) -> bool:
        """Navega para uma URL com verificações de segurança"""
        if not self.driver:
            raise RuntimeError("Driver não inicializado")

        try:
            self.logger.info(f"Navegando para: {url}")
            self.driver.get(url)

            if wait_for_load:
                self._wait_for_page_load()

            current_url = self.driver.current_url
            title = self.driver.title

            self.logger.info(f"Página carregada: {current_url}")
            self.logger.info(f"Título: {title}")

            return True

        except Exception as e:
            self.logger.error(f"Erro na navegação: {e}")
            return False

    def _wait_for_page_load(self, timeout: int = 30):
        """Aguarda carregamento completo da página"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Pausa adicional para carregamento dinâmico
        except Exception as e:
            self.logger.warning(f"Timeout no carregamento da página: {e}")

    def execute_script_safe(self, script: str, *args) -> Any:
        """Executa JavaScript de forma segura"""
        if not self.driver:
            raise RuntimeError("Driver não inicializado")

        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.warning(f"Erro ao executar script: {e}")
            return None

    def capture_screenshot(self, filename: str) -> bool:
        """Captura screenshot da página atual"""
        if not self.driver:
            return False

        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot salvo: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Erro no screenshot: {e}")
            return False

    def get_page_info(self) -> Dict[str, Any]:
        """Retorna informações detalhadas da página atual"""
        if not self.driver:
            return {}

        try:
            return {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "user_agent": self.execute_script_safe("return navigator.userAgent;"),
                "viewport": self.execute_script_safe(
                    "return {width: window.innerWidth, height: window.innerHeight};"
                ),
                "cookies": len(self.driver.get_cookies()),
                "forms": len(self.driver.find_elements("tag name", "form")),
                "links": len(self.driver.find_elements("tag name", "a")),
                "images": len(self.driver.find_elements("tag name", "img")),
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar informações da página: {e}")
            return {}

    def cleanup(self):
        """Limpa recursos do navegador"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Navegador fechado com sucesso")
            except Exception as e:
                self.logger.warning(f"Erro ao fechar navegador: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        """Context manager entry"""
        self.create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
