"""
Motor de Automação Principal
Coordena todas as operações de automação de login
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.core.browser_engine import BrowserEngine
from src.core.field_detector import FieldDetector


class AutomationEngine:
    """Motor principal de automação de login"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser = None
        self.logger = logging.getLogger(__name__)

        # Estado da automação
        self.is_running = False
        self.current_operation = None
        self.last_result = None

        # Estatísticas
        self.stats = {
            "operations_total": 0,
            "operations_success": 0,
            "operations_failed": 0,
            "last_execution": None,
            "average_duration": 0,
        }

    def initialize(self) -> bool:
        """Inicializa o motor de automação"""
        try:
            self.logger.info("Inicializando motor de automação...")

            # Cria instância do navegador
            headless = self.config.get("headless", False)
            self.browser = BrowserEngine(headless=headless, config=self.config)

            # Cria driver
            self.browser.create_driver()

            self.logger.info("Motor de automação inicializado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Falha na inicialização: {e}")
            return False

    def execute_login_sequence(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Executa sequência completa de login
        Retorna resultado detalhado da operação
        """
        start_time = time.time()
        result = {
            "success": False,
            "stage": "initialization",
            "duration": 0,
            "error": None,
            "details": {},
            "screenshots": [],
        }

        try:
            self.is_running = True
            self.current_operation = "login_sequence"
            self.logger.info("Iniciando sequência de login automatizado")

            # Fase 1: Acesso à página
            result["stage"] = "navigation"
            url = self.config.get("site_url", "")
            if not self.browser.navigate_to(url):
                raise Exception("Falha ao acessar página de login")

            result["details"]["navigation"] = {
                "url": url,
                "title": self.browser.driver.title,
                "success": True,
            }

            # Captura screenshot inicial
            screenshot_path = f"screenshot_{int(time.time())}_initial.png"
            if self.browser.capture_screenshot(screenshot_path):
                result["screenshots"].append(screenshot_path)

            # Fase 2: Detecção de campos
            result["stage"] = "field_detection"
            self.logger.info("Detectando campos do formulário...")

            detector = FieldDetector(self.browser.driver, self.config)
            fields = detector.detect_fields()

            if not fields:
                raise Exception("Nenhum campo de formulário detectado")

            result["details"]["field_detection"] = {
                "fields_found": list(fields.keys()),
                "selectors": fields,
                "page_analysis": detector.analyze_page_structure(),
            }

            # Fase 3: Preenchimento do formulário
            result["stage"] = "form_filling"
            self.logger.info("Preenchendo formulário de login...")

            fill_result = self._fill_login_form(fields, credentials)
            result["details"]["form_filling"] = fill_result

            if not fill_result["success"]:
                raise Exception(f"Falha no preenchimento: {fill_result['error']}")

            # Captura screenshot após preenchimento
            screenshot_path = f"screenshot_{int(time.time())}_filled.png"
            if self.browser.capture_screenshot(screenshot_path):
                result["screenshots"].append(screenshot_path)

            # Fase 4: Submissão e verificação
            result["stage"] = "submission"
            self.logger.info("Enviando formulário...")

            submit_result = self._submit_and_verify(fields)
            result["details"]["submission"] = submit_result

            # Determina sucesso final
            result["success"] = submit_result["login_success"]
            result["stage"] = "completed"

            # Captura screenshot final
            screenshot_path = f"screenshot_{int(time.time())}_final.png"
            if self.browser.capture_screenshot(screenshot_path):
                result["screenshots"].append(screenshot_path)

            # Estatísticas
            duration = time.time() - start_time
            result["duration"] = duration
            self._update_statistics(result["success"], duration)

            if result["success"]:
                self.logger.info("Sequência de login concluída com SUCESSO")
            else:
                self.logger.warning(
                    "Sequência de login concluída com AVISO (modo híbrido)"
                )

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["duration"] = time.time() - start_time
            self.logger.error(f"Erro na sequência de login: {e}")

            # Captura screenshot de erro
            screenshot_path = f"screenshot_{int(time.time())}_error.png"
            if self.browser and self.browser.capture_screenshot(screenshot_path):
                result["screenshots"].append(screenshot_path)

        finally:
            self.is_running = False
            self.current_operation = None
            self.last_result = result

        return result

    def _fill_login_form(
        self, fields: Dict[str, str], credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """Preenche o formulário de login"""
        result = {"success": False, "error": None, "fields_filled": []}

        try:
            # Preenche email
            if "email" in fields and "email" in credentials:
                if self._fill_field(fields["email"], credentials["email"]):
                    result["fields_filled"].append("email")
                    self.logger.info("Campo email preenchido")
                else:
                    raise Exception("Falha ao preencher campo email")

            # Pequena pausa
            time.sleep(1)

            # Preenche senha
            if "password" in fields and "password" in credentials:
                if self._fill_field(fields["password"], credentials["password"]):
                    result["fields_filled"].append("password")
                    self.logger.info("Campo senha preenchido")
                else:
                    raise Exception("Falha ao preencher campo senha")

            # Aguarda carregamento dinâmico
            time.sleep(2)

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Erro no preenchimento do formulário: {e}")

        return result

    def _fill_field(self, selector: str, value: str) -> bool:
        """Preenche um campo específico"""
        try:
            # Aguarda elemento estar disponível
            element = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )

            # Limpa e preenche
            element.clear()
            element.send_keys(value)

            # Verifica se foi preenchido
            current_value = element.get_attribute("value")
            if current_value and len(current_value) > 0:
                return True
            else:
                self.logger.warning(
                    f"Campo não foi preenchido corretamente: {selector}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Erro ao preencher campo {selector}: {e}")
            return False

    def _submit_and_verify(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Submete formulário e verifica resultado"""
        result = {
            "submit_success": False,
            "login_success": False,
            "current_url": None,
            "page_title": None,
            "error_indicators": [],
            "success_indicators": [],
        }

        try:
            initial_url = self.browser.driver.current_url

            # Tenta submissão
            if "submit" in fields:
                # Usa botão específico
                submit_success = self._click_submit_button(fields["submit"])
            else:
                # Tenta submit automático
                submit_success = self._try_auto_submit()

            result["submit_success"] = submit_success

            if submit_success:
                # Aguarda mudança
                time.sleep(3)

                # Verifica resultado
                result["current_url"] = self.browser.driver.current_url
                result["page_title"] = self.browser.driver.title

                # Verifica indicadores de erro
                error_indicators = self._check_error_indicators()
                result["error_indicators"] = error_indicators

                # Verifica indicadores de sucesso
                success_indicators = self._check_success_indicators()
                result["success_indicators"] = success_indicators

                # Determina se login foi bem-sucedido
                result["login_success"] = self._determine_login_success(
                    initial_url,
                    result["current_url"],
                    error_indicators,
                    success_indicators,
                )

            else:
                self.logger.warning("Falha na submissão do formulário")

        except Exception as e:
            self.logger.error(f"Erro na submissão e verificação: {e}")

        return result

    def _click_submit_button(self, selector: str) -> bool:
        """Clica no botão de submit"""
        try:
            button = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            button.click()
            self.logger.info(f"Botão submit clicado: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao clicar botão submit {selector}: {e}")
            return False

    def _try_auto_submit(self) -> bool:
        """Tenta submissão automática do formulário"""
        try:
            # Tenta encontrar e submeter formulário
            forms = self.browser.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                forms[0].submit()
                self.logger.info("Formulário submetido automaticamente")
                return True

            # Tenta tecla Enter no campo ativo
            active_element = self.browser.driver.switch_to.active_element
            if active_element:
                active_element.send_keys("\n")
                self.logger.info("Enter enviado no campo ativo")
                return True

        except Exception as e:
            self.logger.error(f"Erro na submissão automática: {e}")

        return False

    def _check_error_indicators(self) -> List[str]:
        """Verifica indicadores de erro na página"""
        error_indicators = []

        try:
            # Busca por elementos de erro comuns
            error_selectors = [
                "[class*='error']",
                "[class*='erro']",
                "[class*='alert']",
                "[id*='error']",
                "[id*='erro']",
                "[class*='invalid']",
                "[class*='danger']",
                "[class*='warning']",
            ]

            for selector in error_selectors:
                try:
                    elements = self.browser.driver.find_elements(
                        By.CSS_SELECTOR, selector
                    )
                    for element in elements:
                        if element.is_displayed() and element.text.strip():
                            error_indicators.append(element.text.strip()[:100])
                except:
                    continue

            # Verifica se ainda está na página de login
            current_url = self.browser.driver.current_url.lower()
            page_title = self.browser.driver.title.lower()

            if "login" in current_url or "login" in page_title:
                error_indicators.append("Ainda na página de login")

        except Exception as e:
            self.logger.error(f"Erro ao verificar indicadores de erro: {e}")

        return error_indicators

    def _check_success_indicators(self) -> List[str]:
        """Verifica indicadores de sucesso na página"""
        success_indicators = []

        try:
            success_keywords = [
                "dashboard",
                "painel",
                "home",
                "principal",
                "conta",
                "perfil",
                "logout",
                "sair",
                "welcome",
                "bem-vindo",
                "success",
                "sucesso",
                "logado",
                "authenticated",
                "signed in",
            ]

            page_text = self.browser.driver.page_source.lower()
            page_title = self.browser.driver.title.lower()

            for keyword in success_keywords:
                if keyword in page_text or keyword in page_title:
                    success_indicators.append(keyword)

        except Exception as e:
            self.logger.error(f"Erro ao verificar indicadores de sucesso: {e}")

        return success_indicators

    def _determine_login_success(
        self,
        initial_url: str,
        current_url: str,
        error_indicators: List[str],
        success_indicators: List[str],
    ) -> bool:
        """Determina se o login foi bem-sucedido baseado em múltiplos fatores"""

        # Se há indicadores de erro claros, falhou
        if error_indicators:
            return False

        # Se há indicadores de sucesso claros, sucesso
        if success_indicators:
            return True

        # Verifica se a URL mudou (saiu da página de login)
        if current_url != initial_url and "login" not in current_url.lower():
            return True

        # Por padrão, assume sucesso se não há erros claros
        return True

    def _update_statistics(self, success: bool, duration: float):
        """Atualiza estatísticas da automação"""
        self.stats["operations_total"] += 1
        self.stats["last_execution"] = datetime.now()

        if success:
            self.stats["operations_success"] += 1
        else:
            self.stats["operations_failed"] += 1

        # Atualiza duração média
        total_ops = self.stats["operations_total"]
        current_avg = self.stats["average_duration"]
        self.stats["average_duration"] = (
            current_avg * (total_ops - 1) + duration
        ) / total_ops

    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do motor"""
        return {
            "is_running": self.is_running,
            "current_operation": self.current_operation,
            "last_result": self.last_result,
            "stats": self.stats.copy(),
            "browser_info": (
                self.browser.get_page_info()
                if self.browser and self.browser.driver
                else {}
            ),
        }

    def cleanup(self):
        """Limpa recursos"""
        if self.browser:
            self.browser.cleanup()
        self.is_running = False
        self.current_operation = None
