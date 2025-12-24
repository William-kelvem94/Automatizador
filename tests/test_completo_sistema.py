#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Teste Completo do Sistema Automatizador de Login
Testa todas as funcionalidades principais de forma automatizada
"""

import os
import sys
import time
import configparser
from datetime import datetime

# Adicionar o diretório atual ao path para importar módulos locais
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from login_automator import LoginAutomator

class SistemaTester:
    """Classe para testar todas as funcionalidades do sistema"""

    def __init__(self, config_file='config/config.ini'):
        self.config_file = config_file
        self.automator = None
        self.resultados = []

    def log(self, message, tipo="INFO"):
        """Log padronizado para testes"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{tipo}] {message}")
        self.resultados.append(f"[{tipo}] {message}")

    def testar_inicializacao(self):
        """Testa a inicialização do sistema"""
        self.log("=" * 70)
        self.log("TESTE 1: INICIALIZAÇÃO DO SISTEMA")
        self.log("=" * 70)

        try:
            self.log("Criando instancia do LoginAutomator...")
            self.automator = LoginAutomator(self.config_file)
            self.log("[OK] Sistema inicializado com sucesso", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha na inicializacao: {e}", "ERROR")
            return False

    def testar_configuracao(self):
        """Testa se a configuração foi carregada corretamente"""
        self.log("\n" + "=" * 70)
        self.log("TESTE 2: VALIDAÇÃO DA CONFIGURAÇÃO")
        self.log("=" * 70)

        if not self.automator:
            self.log("[EMOJI] Automator não inicializado", "ERROR")
            return False

        config = self.automator.config

        # Verificar seções obrigatórias
        secoes_obrigatorias = ['SITE', 'CREDENTIALS', 'SETTINGS']
        for secao in secoes_obrigatorias:
            if not config.has_section(secao):
                self.log(f"[EMOJI] Seção '{secao}' não encontrada na configuração", "ERROR")
                return False
            else:
                self.log(f"[EMOJI] Seção '{secao}' encontrada", "SUCCESS")

        # Verificar campos obrigatórios
        url = config.get('SITE', 'url', fallback='')
        email = config.get('CREDENTIALS', 'email', fallback='')
        password = config.get('CREDENTIALS', 'password', fallback='')

        checks = [
            ("URL do site", url, url.startswith(('http://', 'https://'))),
            ("E-mail", email, '@' in email and '.' in email),
            ("Senha", password, len(password) > 0)
        ]

        for campo, valor, valido in checks:
            if valido:
                self.log(f"[EMOJI] {campo}: OK ({valor[:50]}...)" if len(str(valor)) > 50 else f"[EMOJI] {campo}: OK ({valor})", "SUCCESS")
            else:
                self.log(f"[EMOJI] {campo}: Inválido ou vazio", "ERROR")
                return False

        self.log("[EMOJI] Configuração validada com sucesso", "SUCCESS")
        return True

    def testar_webdriver(self):
        """Testa a configuração do WebDriver"""
        self.log("\n" + "=" * 70)
        self.log("TESTE 3: CONFIGURAÇÃO DO WEBDRIVER")
        self.log("=" * 70)

        if not self.automator:
            self.log("[EMOJI] Automator não inicializado", "ERROR")
            return False

        try:
            self.log("Configurando WebDriver...")
            driver = self.automator.setup_driver()
            self.log("[EMOJI] WebDriver configurado com sucesso", "SUCCESS")

            # Testar navegação básica
            self.log("Testando navegação para google.com...")
            driver.get("https://www.google.com")
            title = driver.title
            if "Google" in title:
                self.log(f"[EMOJI] Navegação OK - Título: {title}", "SUCCESS")
            else:
                self.log(f"[EMOJI]️ Navegação OK mas título estranho: {title}", "WARNING")

            driver.quit()
            self.log("[EMOJI] WebDriver fechado corretamente", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"[EMOJI] Falha no WebDriver: {e}", "ERROR")
            return False

    def testar_acesso_pagina(self):
        """Testa o acesso à página de login configurada"""
        self.log("\n" + "=" * 70)
        self.log("TESTE 4: ACESSO À PÁGINA DE LOGIN")
        self.log("=" * 70)

        if not self.automator:
            self.log("[EMOJI] Automator não inicializado", "ERROR")
            return False

        try:
            self.log(f"Acessando página: {self.automator.site_url}")
            driver = self.automator.setup_driver()

            if self.automator._access_login_page(driver):
                current_url = driver.current_url
                title = driver.title
                self.log(f"[EMOJI] Página acessada: {current_url}", "SUCCESS")
                self.log(f"[EMOJI] Título da página: {title}", "INFO")

                # Testar validação da página
                if self.automator.validate_page(driver):
                    self.log("[EMOJI] Página validada para formulários de login", "SUCCESS")
                else:
                    self.log("[EMOJI]️ Página pode não ter formulários tradicionais", "WARNING")

                driver.quit()
                return True
            else:
                self.log("[EMOJI] Falha ao acessar página", "ERROR")
                driver.quit()
                return False

        except Exception as e:
            self.log(f"[EMOJI] Erro no acesso: {e}", "ERROR")
            return False

    def testar_mapeamento_campos(self):
        """Testa o mapeamento automático de campos"""
        self.log("\n" + "=" * 70)
        self.log("TESTE 5: MAPEAMENTO DE CAMPOS")
        self.log("=" * 70)

        if not self.automator:
            self.log("[EMOJI] Automator não inicializado", "ERROR")
            return False

        try:
            self.log("Executando mapeamento inteligente de campos...")
            driver = self.automator.setup_driver()
            self.automator._access_login_page(driver)

            # Testar detecção inteligente
            fields = self.automator.smart_field_detection(driver)
            if fields:
                self.log(f"[EMOJI] Campos detectados automaticamente: {list(fields.keys())}", "SUCCESS")
                for field_type, selector in fields.items():
                    self.log(f"   • {field_type.upper()}: {selector}", "INFO")
            else:
                self.log("[EMOJI]️ Detecção automática falhou, tentando fallback...", "WARNING")
                fields = self.automator.fallback_field_detection(driver)
                if fields:
                    self.log(f"[EMOJI] Campos detectados via fallback: {list(fields.keys())}", "SUCCESS")
                    for field_type, selector in fields.items():
                        self.log(f"   • {field_type.upper()}: {selector}", "INFO")
                else:
                    self.log("[EMOJI] Nenhum campo detectado", "ERROR")

            # Executar análise completa
            self.log("\n[EMOJI] EXECUTANDO ANÁLISE COMPLETA DA PÁGINA", "INFO")
            self.automator.analyze_page_elements(driver)

            driver.quit()
            return bool(fields)

        except Exception as e:
            self.log(f"[EMOJI] Erro no mapeamento: {e}", "ERROR")
            return False

    def testar_login_completo(self):
        """Testa o processo completo de login (sem realmente fazer login)"""
        self.log("\n" + "=" * 70)
        self.log("TESTE 6: SIMULAÇÃO DE LOGIN COMPLETO")
        self.log("=" * 70)

        if not self.automator:
            self.log("[EMOJI] Automator não inicializado", "ERROR")
            return False

        try:
            self.log("[EMOJI]️ ATENÇÃO: Este teste SIMULA o login sem enviá-lo realmente", "WARNING")
            self.log("Para segurança, apenas testaremos até o preenchimento dos campos")

            driver = self.automator.setup_driver()
            self.automator._access_login_page(driver)

            if not self.automator.validate_page(driver):
                self.log("[EMOJI] Página não validada", "ERROR")
                driver.quit()
                return False

            fields = self.automator.smart_field_detection(driver)
            if not fields:
                fields = self.automator.fallback_field_detection(driver)

            if not fields:
                self.log("[EMOJI] Nenhum campo detectado para teste", "ERROR")
                driver.quit()
                return False

            # Testar preenchimento (mas não enviar)
            if self.automator._fill_login_form(driver, fields):
                self.log("[EMOJI] Campos preenchidos com sucesso", "SUCCESS")
                self.log("[EMOJI]️ Login NÃO foi enviado (teste de segurança)", "WARNING")

                # Pequena pausa para visualização
                time.sleep(3)
                success = True
            else:
                self.log("[EMOJI] Falha no preenchimento dos campos", "ERROR")
                success = False

            driver.quit()
            return success

        except Exception as e:
            self.log(f"[EMOJI] Erro no teste de login: {e}", "ERROR")
            return False

    def executar_todos_testes(self):
        """Executa todos os testes em sequência"""
        self.log("[EMOJI] INICIANDO TESTES COMPLETOS DO SISTEMA")
        self.log("=" * 70)

        testes = [
            ("Inicialização", self.testar_inicializacao),
            ("Configuração", self.testar_configuracao),
            ("WebDriver", self.testar_webdriver),
            ("Acesso à Página", self.testar_acesso_pagina),
            ("Mapeamento de Campos", self.testar_mapeamento_campos),
            ("Login Simulado", self.testar_login_completo)
        ]

        resultados = []
        for nome_teste, funcao_teste in testes:
            try:
                self.log(f"\n[EMOJI] EXECUTANDO: {nome_teste}")
                resultado = funcao_teste()
                resultados.append((nome_teste, resultado))
            except Exception as e:
                self.log(f"[EMOJI] ERRO CRÍTICO no teste '{nome_teste}': {e}", "ERROR")
                resultados.append((nome_teste, False))

        # Resultado final
        self.log("\n" + "=" * 80)
        self.log("[EMOJI] RESULTADO FINAL DOS TESTES")
        self.log("=" * 80)

        testes_passaram = 0
        for nome_teste, resultado in resultados:
            status = "[EMOJI] PASSOU" if resultado else "[EMOJI] FALHOU"
            self.log(f"{nome_teste}: {status}")
            if resultado:
                testes_passaram += 1

        total_testes = len(resultados)
        percentual = (testes_passaram / total_testes) * 100

        self.log(f"\n[EMOJI] TOTAL: {testes_passaram}/{total_testes} testes passaram ({percentual:.1f}%)")

        if testes_passaram == total_testes:
            self.log("[EMOJI] SISTEMA TOTALMENTE FUNCIONAL!", "SUCCESS")
        elif testes_passaram >= total_testes * 0.8:
            self.log("[EMOJI] SISTEMA PRATICAMENTE FUNCIONAL", "SUCCESS")
        elif testes_passaram >= total_testes * 0.5:
            self.log("[EMOJI]️ SISTEMA PARCIALMENTE FUNCIONAL", "WARNING")
        else:
            self.log("[EMOJI] SISTEMA COM PROBLEMAS GRAVES", "ERROR")

        return testes_passaram == total_testes

def main():
    """Função principal"""
    print("[TEST] Sistema de Teste Automatizado - Automatizador de Login")
    print("=" * 60)

    # Verificar se estamos no diretório correto
    config_path = 'config/config.ini'
    if not os.path.exists(config_path):
        print(f"[EMOJI] Arquivo de configuração não encontrado: {config_path}")
        print("Execute este script a partir da raiz do projeto.")
        sys.exit(1)

    # Executar testes
    tester = SistemaTester(config_path)
    sucesso = tester.executar_todos_testes()

    # Salvar resultados em arquivo
    resultado_file = 'teste_resultado.txt'
    with open(resultado_file, 'w', encoding='utf-8') as f:
        f.write("RESULTADO DOS TESTES - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("=" * 80 + "\n")
        for linha in tester.resultados:
            f.write(linha + "\n")

    print(f"\n[EMOJI] Resultados salvos em: {resultado_file}")

    if sucesso:
        print("[EMOJI] Todos os testes passaram!")
        sys.exit(0)
    else:
        print("[EMOJI] Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == '__main__':
    main()
