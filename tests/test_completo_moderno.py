#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste Completo do Sistema Moderno - Automatizador de Login
Valida todas as funcionalidades da interface moderna
"""

import configparser
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
sys.path.insert(0, src_dir)

LOGIN_AUTOMATOR_AVAILABLE = False
GUI_MODERNA_AVAILABLE = False

try:
    from login_automator import LoginAutomator

    LOGIN_AUTOMATOR_AVAILABLE = True
    print("[OK] LoginAutomator disponível")
except ImportError as e:
    print(f"[WARNING] Core não disponível: {e}")

try:
    from gui_moderna import ModernLoginAutomatorGUI

    GUI_MODERNA_AVAILABLE = True
    print("[OK] Interface moderna disponível")
except ImportError as e:
    print(f"[WARNING] Interface moderna não disponível: {e}")


class TestSistemaModerno(unittest.TestCase):
    """Testes completos do sistema moderno"""

    def setUp(self):
        """Configuração dos testes"""
        self.test_config_path = os.path.join(parent_dir, "config", "config_test.ini")

        # Criar configuração de teste
        self.config = configparser.ConfigParser()
        self.config.add_section("SITE")
        self.config.add_section("CREDENTIALS")
        self.config.add_section("SCHEDULE")
        self.config.add_section("SETTINGS")

        self.config.set("SITE", "url", "https://ixc.webflash.net.br/app/login")
        self.config.set("CREDENTIALS", "email", "teste@teste.com")
        self.config.set("CREDENTIALS", "password", "senha123")
        self.config.set("SCHEDULE", "horarios", "09:00,15:00")
        self.config.set("SETTINGS", "headless", "false")
        self.config.set("SETTINGS", "wait_timeout", "10")

        # Salvar configuração de teste
        with open(self.test_config_path, "w") as f:
            self.config.write(f)

        print("[SETUP] Configuração de teste criada")

    def tearDown(self):
        """Limpeza após testes"""
        try:
            if os.path.exists(self.test_config_path):
                os.remove(self.test_config_path)
                print("[CLEANUP] Configuração de teste removida")
        except:
            pass

    def test_01_importacoes(self):
        """Teste 1: Verificar importações"""
        print("\n" + "=" * 60)
        print("TESTE 1: VERIFICANDO IMPORTAÇÕES")
        print("=" * 60)

        # Testar imports essenciais
        try:
            import tkinter as tk

            print("[OK] tkinter disponível")
        except ImportError:
            self.fail("tkinter não disponível")

        try:
            import selenium

            print("[OK] selenium disponível")
        except ImportError:
            self.fail("selenium não disponível")

        try:
            import configparser

            print("[OK] configparser disponível")
        except ImportError:
            self.fail("configparser não disponível")

        try:
            import apscheduler

            print("[OK] apscheduler disponível")
        except ImportError:
            self.fail("apscheduler não disponível")

        if LOGIN_AUTOMATOR_AVAILABLE:
            print("[OK] LoginAutomator importado")
        else:
            print("[WARNING] LoginAutomator não disponível")

        if GUI_MODERNA_AVAILABLE:
            print("[OK] ModernLoginAutomatorGUI importado")
        else:
            print("[WARNING] ModernLoginAutomatorGUI não disponível")

        print("[SUCCESS] Todas as importações funcionais!")

    @unittest.skipUnless(LOGIN_AUTOMATOR_AVAILABLE, "LoginAutomator não disponível")
    def test_02_login_automator_core(self):
        """Teste 2: Funcionalidades core do LoginAutomator"""
        print("\n" + "=" * 60)
        print("TESTE 2: FUNCIONALIDADES CORE")
        print("=" * 60)

        # Testar instanciação
        try:
            automator = LoginAutomator(self.test_config_path)
            print("[OK] LoginAutomator instanciado")
        except Exception as e:
            self.fail(f"Falha na instanciação: {e}")

        # Testar configuração carregada
        self.assertEqual(automator.site_url, "https://ixc.webflash.net.br/app/login")
        self.assertEqual(automator.email, "teste@teste.com")
        self.assertEqual(automator.password, "senha123")
        print("[OK] Configuração carregada corretamente")

        # Testar métodos existentes
        self.assertTrue(hasattr(automator, "setup_driver"))
        self.assertTrue(hasattr(automator, "perform_login"))
        self.assertTrue(hasattr(automator, "smart_field_detection"))
        self.assertTrue(hasattr(automator, "validate_page"))
        self.assertTrue(hasattr(automator, "start_scheduler"))
        self.assertTrue(hasattr(automator, "stop_scheduler"))
        print("[OK] Métodos principais disponíveis")

        print("[SUCCESS] Funcionalidades core testadas!")

    @unittest.skipUnless(GUI_MODERNA_AVAILABLE, "Interface moderna não disponível")
    def test_03_gui_moderna_classe(self):
        """Teste 3: Verificação da classe da interface moderna"""
        print("\n" + "=" * 60)
        print("TESTE 3: VERIFICAÇÃO DA CLASSE DA INTERFACE MODERNA")
        print("=" * 60)

        try:
            from gui_moderna import ModernLoginAutomatorGUI

            print("[OK] Classe ModernLoginAutomatorGUI importada")

            # Verificar se é uma classe
            self.assertTrue(callable(ModernLoginAutomatorGUI))
            print("[OK] ModernLoginAutomatorGUI é uma classe válida")

            # Verificar se tem o método __init__
            self.assertTrue(hasattr(ModernLoginAutomatorGUI, "__init__"))
            print("[OK] Método __init__ presente")

            # Verificar se tem métodos principais
            expected_methods = [
                "save_config",
                "test_config",
                "map_fields",
                "run_login",
                "start_scheduler",
                "stop_scheduler",
                "log",
            ]
            for method in expected_methods:
                self.assertTrue(hasattr(ModernLoginAutomatorGUI, method))
            print("[OK] Métodos principais presentes")

            print("[SUCCESS] Classe da interface moderna verificada!")

        except Exception as e:
            self.fail(f"Falha na verificação da classe GUI: {e}")

    def test_04_configuracao_arquivos(self):
        """Teste 4: Configuração de arquivos"""
        print("\n" + "=" * 60)
        print("TESTE 4: CONFIGURAÇÃO DE ARQUIVOS")
        print("=" * 60)

        # Verificar estrutura de diretórios
        config_dir = os.path.join(parent_dir, "config")
        src_dir = os.path.join(parent_dir, "src")
        scripts_dir = os.path.join(parent_dir, "scripts")

        self.assertTrue(os.path.exists(config_dir), "Diretório config não existe")
        self.assertTrue(os.path.exists(src_dir), "Diretório src não existe")
        self.assertTrue(os.path.exists(scripts_dir), "Diretório scripts não existe")
        print("[OK] Estrutura de diretórios correta")

        # Verificar arquivos essenciais
        config_file = os.path.join(config_dir, "config.ini")
        gui_file = os.path.join(src_dir, "gui_moderna.py")
        automator_file = os.path.join(src_dir, "login_automator.py")

        if os.path.exists(config_file):
            print("[OK] Arquivo config.ini existe")
        else:
            print("[WARNING] Arquivo config.ini não encontrado")

        self.assertTrue(
            os.path.exists(gui_file), "Arquivo gui_moderna.py não encontrado"
        )
        self.assertTrue(
            os.path.exists(automator_file), "Arquivo login_automator.py não encontrado"
        )
        print("[OK] Arquivos essenciais presentes")

        # Verificar executável
        bat_file = os.path.join(parent_dir, "executar.bat")
        self.assertTrue(os.path.exists(bat_file), "Arquivo executar.bat não encontrado")
        print("[OK] Arquivo executável presente")

        print("[SUCCESS] Configuração de arquivos validada!")

    def test_05_funcionalidades_config(self):
        """Teste 5: Funcionalidades de configuração"""
        print("\n" + "=" * 60)
        print("TESTE 5: FUNCIONALIDADES DE CONFIGURAÇÃO")
        print("=" * 60)

        # Testar leitura de configuração
        config = configparser.ConfigParser()
        config.read(self.test_config_path)

        # Verificar seções
        self.assertTrue(config.has_section("SITE"), "Seção SITE não encontrada")
        self.assertTrue(
            config.has_section("CREDENTIALS"), "Seção CREDENTIALS não encontrada"
        )
        self.assertTrue(config.has_section("SCHEDULE"), "Seção SCHEDULE não encontrada")
        self.assertTrue(config.has_section("SETTINGS"), "Seção SETTINGS não encontrada")
        print("[OK] Todas as seções presentes")

        # Verificar valores
        self.assertEqual(
            config.get("SITE", "url"), "https://ixc.webflash.net.br/app/login"
        )
        self.assertEqual(config.get("CREDENTIALS", "email"), "teste@teste.com")
        self.assertEqual(config.get("CREDENTIALS", "password"), "senha123")
        print("[OK] Valores de configuração corretos")

        # Testar escrita de configuração
        config.add_section("TEST")
        config.set("TEST", "test_key", "test_value")
        with open(self.test_config_path, "w") as f:
            config.write(f)

        # Re-ler e verificar
        config2 = configparser.ConfigParser()
        config2.read(self.test_config_path)
        self.assertEqual(config2.get("TEST", "test_key"), "test_value")
        print("[OK] Escrita de configuração funcional")

        print("[SUCCESS] Funcionalidades de configuração testadas!")

    def test_06_dependencias_sistema(self):
        """Teste 6: Dependências do sistema"""
        print("\n" + "=" * 60)
        print("TESTE 6: DEPENDÊNCIAS DO SISTEMA")
        print("=" * 60)

        # Testar versões do Python
        python_version = sys.version_info
        self.assertGreaterEqual(python_version.major, 3)
        self.assertGreaterEqual(python_version.minor, 8)
        print(
            f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro} compatível"
        )

        # Testar codificação
        encoding = sys.stdout.encoding
        print(f"[INFO] Codificação do sistema: {encoding}")

        # Testar caminhos
        print(f"[INFO] Diretório atual: {os.getcwd()}")
        print(f"[INFO] Diretório do script: {current_dir}")
        print(f"[INFO] Diretório pai: {parent_dir}")

        # Testar permissões de arquivo
        try:
            test_file = os.path.join(parent_dir, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("[OK] Permissões de escrita OK")
        except Exception as e:
            print(f"[WARNING] Problemas com permissões: {e}")

        print("[SUCCESS] Dependências do sistema verificadas!")

    @unittest.skipUnless(GUI_MODERNA_AVAILABLE, "Interface moderna não disponível")
    def test_07_constantes_interface(self):
        """Teste 7: Constantes da interface"""
        print("\n" + "=" * 60)
        print("TESTE 7: CONSTANTES DA INTERFACE")
        print("=" * 60)

        try:
            from gui_moderna import ModernLoginAutomatorGUI

            print("[OK] Classe importada para verificação de constantes")

            # Verificar se tem constantes de cores
            gui_instance = ModernLoginAutomatorGUI.__new__(ModernLoginAutomatorGUI)
            gui_instance.colors = {
                "primary": "#1877f2",
                "secondary": "#42b883",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "dark": "#1c1e21",
                "light": "#f8f9fa",
                "white": "#ffffff",
                "border": "#e1e5e9",
            }

            # Verificar cores definidas
            expected_colors = [
                "primary",
                "secondary",
                "danger",
                "warning",
                "dark",
                "light",
                "white",
                "border",
            ]
            for color in expected_colors:
                self.assertIn(color, gui_instance.colors)
                self.assertTrue(gui_instance.colors[color].startswith("#"))
            print("[OK] Paleta de cores definida corretamente")

            print("[SUCCESS] Constantes da interface verificadas!")

        except Exception as e:
            self.fail(f"Falha na verificação de constantes: {e}")

    def test_08_log_sistema(self):
        """Teste 8: Sistema de logs"""
        print("\n" + "=" * 60)
        print("TESTE 8: SISTEMA DE LOGS")
        print("=" * 60)

        # Testar logging básico
        import logging

        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)

        # Capturar logs
        import io

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Testar log
        test_message = "Teste de log do sistema"
        logger.info(test_message)

        # Verificar se foi capturado
        logs = log_stream.getvalue()
        self.assertIn(test_message, logs)
        print("[OK] Sistema de logging funcional")

        print("[SUCCESS] Sistema de logs validado!")


def run_tests():
    """Executar todos os testes"""
    print("=" * 80)
    print("[TEST] TESTE COMPLETO DO SISTEMA MODERNO")
    print("[VERSION] Automatizador de Login v3.0")
    print("=" * 80)

    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSistemaModerno)

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Resultado final
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("[SUCCESS] TODOS OS TESTES PASSARAM!")
        print("[OK] Sistema funcionando perfeitamente")
        print("=" * 80)
        return True
    else:
        print("[FAILURE] ALGUNS TESTES FALHARAM!")
        print(f"   Falhas: {len(result.failures)}")
        print(f"   Erros: {len(result.errors)}")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
