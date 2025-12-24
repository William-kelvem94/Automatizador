"""
Detector Inteligente de Campos
Sistema avançado para detecção automática de formulários de login
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FieldDetector:
    """Detector inteligente de campos de formulário"""

    def __init__(self, driver, config: Optional[Dict[str, Any]] = None):
        self.driver = driver
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Padrões de detecção
        self.patterns = {
            'email': [
                r'email', r'e-mail', r'mail', r'usuario', r'user', r'login',
                r'correo', r'account', r'identifiant'
            ],
            'password': [
                r'password', r'senha', r'pass', r'pwd', r'clave', r'motdepasse',
                r'contraseña', r'пароль'
            ],
            'submit': [
                r'submit', r'login', r'entrar', r'acessar', r'conectar',
                r'sign.?in', r'log.?in', r'connect', r'auth'
            ]
        }

    def detect_fields(self) -> Dict[str, str]:
        """
        Detecta campos de formulário usando múltiplas estratégias
        Retorna dicionário com seletores encontrados
        """
        self.logger.info("Iniciando detecção inteligente de campos...")

        strategies = [
            self._strategy_css_selectors,
            self._strategy_attribute_analysis,
            self._strategy_text_analysis,
            self._strategy_fallback_detection
        ]

        for strategy in strategies:
            try:
                self.logger.debug(f"Tentando estratégia: {strategy.__name__}")
                fields = strategy()
                if fields and self._validate_fields(fields):
                    self.logger.info(f"Campos detectados com sucesso: {list(fields.keys())}")
                    return fields
            except Exception as e:
                self.logger.debug(f"Estratégia {strategy.__name__} falhou: {e}")

        self.logger.warning("Nenhum campo detectado automaticamente")
        return {}

    def _strategy_css_selectors(self) -> Dict[str, str]:
        """Estratégia 1: Seletores CSS comuns"""
        fields = {}

        # Mapeamento de seletores por tipo
        selectors_map = {
            'email': [
                'input[type="email"]',
                'input[name*="email"]',
                'input[name*="mail"]',
                'input[name*="usuario"]',
                'input[name*="user"]',
                'input[name*="login"]',
                'input[id*="email"]',
                'input[id*="mail"]',
                'input[id*="usuario"]',
                'input[id*="user"]',
                'input[id*="login"]',
                '#email', '#mail', '#usuario', '#user', '#login'
            ],
            'password': [
                'input[type="password"]',
                'input[name*="password"]',
                'input[name*="senha"]',
                'input[name*="pass"]',
                'input[name*="pwd"]',
                'input[id*="password"]',
                'input[id*="senha"]',
                'input[id*="pass"]',
                'input[id*="pwd"]',
                '#password', '#senha', '#pass', '#pwd'
            ],
            'submit': [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[name*="login"]',
                'button[name*="entrar"]',
                'button[name*="submit"]',
                'button[id*="login"]',
                'button[id*="entrar"]',
                'button[id*="submit"]',
                '.btn-login', '.btn-entrar', '.btn-submit'
            ]
        }

        for field_type, selectors in selectors_map.items():
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        fields[field_type] = selector
                        self.logger.debug(f"Campo {field_type} encontrado: {selector}")
                        break
                except Exception:
                    continue

        return fields

    def _strategy_attribute_analysis(self) -> Dict[str, str]:
        """Estratégia 2: Análise de atributos"""
        fields = {}

        # Analisa todos os inputs visíveis
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        buttons = self.driver.find_elements(By.TAG_NAME, "button")

        # Categoriza inputs
        candidates = {'email': [], 'password': [], 'submit': []}

        for inp in inputs:
            if not inp.is_displayed():
                continue

            input_type = inp.get_attribute('type') or ''
            name = inp.get_attribute('name') or ''
            id_attr = inp.get_attribute('id') or ''
            placeholder = inp.get_attribute('placeholder') or ''
            class_attr = inp.get_attribute('class') or ''

            # Analisa atributos para classificação
            attrs_text = f"{input_type} {name} {id_attr} {placeholder} {class_attr}".lower()

            if input_type == 'email' or self._matches_patterns(attrs_text, self.patterns['email']):
                candidates['email'].append(inp)
            elif input_type == 'password' or self._matches_patterns(attrs_text, self.patterns['password']):
                candidates['password'].append(inp)
            elif input_type == 'submit':
                candidates['submit'].append(inp)

        # Analisa botões
        for btn in buttons:
            if not btn.is_displayed():
                continue

            btn_text = btn.text.lower()
            name = btn.get_attribute('name') or ''
            id_attr = btn.get_attribute('id') or ''
            class_attr = btn.get_attribute('class') or ''

            attrs_text = f"{btn_text} {name} {id_attr} {class_attr}"
            if self._matches_patterns(attrs_text, self.patterns['submit']):
                candidates['submit'].append(btn)

        # Seleciona melhores candidatos
        for field_type, elements in candidates.items():
            if elements:
                best_element = self._select_best_candidate(elements, field_type)
                if best_element:
                    selector = self._get_css_selector(best_element)
                    fields[field_type] = selector
                    self.logger.debug(f"Campo {field_type} selecionado via análise: {selector}")

        return fields

    def _strategy_text_analysis(self) -> Dict[str, str]:
        """Estratégia 3: Análise de texto próximo aos campos"""
        fields = {}
        # Implementação simplificada - pode ser expandida
        return fields

    def _strategy_fallback_detection(self) -> Dict[str, str]:
        """Estratégia 4: Detecção fallback"""
        fields = {}

        # Busca por qualquer input visível
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        visible_inputs = [inp for inp in inputs if inp.is_displayed()]

        if len(visible_inputs) >= 2:
            # Assume que o primeiro é email e o segundo senha
            fields['email'] = self._get_css_selector(visible_inputs[0])
            fields['password'] = self._get_css_selector(visible_inputs[1])
            self.logger.info("Campos detectados via fallback (assunção)")

        # Busca por botão de submit
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        submit_buttons = [btn for btn in buttons if btn.is_displayed()]

        if submit_buttons:
            fields['submit'] = self._get_css_selector(submit_buttons[0])
            self.logger.info("Botão submit detectado via fallback")

        return fields

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Verifica se o texto corresponde a algum padrão"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in patterns)

    def _select_best_candidate(self, elements: List, field_type: str) -> Optional[Any]:
        """Seleciona o melhor candidato entre elementos similares"""
        if not elements:
            return None

        # Critérios de prioridade
        priority_attrs = {
            'email': ['type', 'name', 'id', 'placeholder'],
            'password': ['type', 'name', 'id', 'placeholder'],
            'submit': ['type', 'name', 'id', 'text']
        }

        best_score = -1
        best_element = None

        for element in elements:
            score = 0

            for attr in priority_attrs.get(field_type, []):
                try:
                    value = element.get_attribute(attr) or ''
                    if self._matches_patterns(value, self.patterns[field_type]):
                        score += 1
                except:
                    continue

            if score > best_score:
                best_score = score
                best_element = element

        return best_element or elements[0]

    def _get_css_selector(self, element) -> str:
        """Gera um seletor CSS único para o elemento"""
        try:
            # Tenta ID primeiro
            element_id = element.get_attribute('id')
            if element_id:
                return f"#{element_id}"

            # Tenta name
            element_name = element.get_attribute('name')
            if element_name:
                return f"[name='{element_name}']"

            # Tenta classe
            element_class = element.get_attribute('class')
            if element_class:
                # Usa primeira classe
                first_class = element_class.split()[0]
                return f".{first_class}"

            # Fallback para tag
            return element.tag_name

        except Exception:
            return element.tag_name

    def _validate_fields(self, fields: Dict[str, str]) -> bool:
        """Valida se os campos detectados são consistentes"""
        required_fields = ['email', 'password']
        found_required = [field for field in required_fields if field in fields]

        # Pelo menos email deve estar presente
        return 'email' in fields

    def analyze_page_structure(self) -> Dict[str, Any]:
        """Analisa a estrutura completa da página"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            links = self.driver.find_elements(By.TAG_NAME, "a")

            return {
                'forms_count': len(forms),
                'inputs_count': len(inputs),
                'buttons_count': len(buttons),
                'links_count': len(links),
                'forms': [
                    {
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method'),
                        'inputs': len(form.find_elements(By.TAG_NAME, "input"))
                    } for form in forms[:3]  # Máximo 3 forms
                ],
                'page_title': self.driver.title,
                'page_url': self.driver.current_url
            }
        except Exception as e:
            self.logger.error(f"Erro na análise da estrutura: {e}")
            return {}
