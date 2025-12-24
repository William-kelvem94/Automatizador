#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SETUP AUTOMATIZADOR IA v6.0 - Instalação Completa
Script de configuração automática do sistema
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header():
    """Imprime cabeçalho"""
    print("=" * 60)
    print("        AUTOMATIZADOR IA v6.0 - SETUP")
    print("=" * 60)
    print("Sistema de Automação Web Inteligente")
    print("Interface Moderna + Motor Robusto")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica versão do Python"""
    print("[CHECK] Verificando Python...")
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERRO] Python {version.major}.{version.minor} não suportado. Necessário Python 3.8+")
        return False

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def install_dependencies():
    """Instala dependências"""
    print("[INSTALL] Instalando dependências...")

    try:
        # Atualiza pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Instala dependências
        requirements_path = Path(__file__).parent.parent / "config" / "requirements.txt"
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[OK] Dependências instaladas com sucesso")
        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha na instalação: {e}")
        return False

def test_imports():
    """Testa imports críticos"""
    print("[TEST] Testando imports...")

    critical_modules = [
        'customtkinter',
        'selenium',
        'webdriver_manager',
        'requests'
    ]

    failed = []

    for module in critical_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[FAIL] {module}")
            failed.append(module)

    if failed:
        print(f"[ERRO] Módulos faltando: {', '.join(failed)}")
        return False

    print("[OK] Todos os módulos importados com sucesso")
    return True

def create_config():
    """Cria configuração inicial"""
    print("[CONFIG] Criando configuração inicial...")

    try:
        from src.core.config import ConfigManager

        config_manager = ConfigManager()
        config = config_manager.load_config()

        if config:
            print("[OK] Configuração carregada")
        else:
            print("[WARN] Usando configuração padrão")

        return True

    except Exception as e:
        print(f"[ERRO] Falha na configuração: {e}")
        return False

def test_system():
    """Testa sistema completo"""
    print("[TEST] Testando sistema...")

    try:
        from src.core.web_automator import WebAutomator
        from src.ui.app import WebAutomatorApp

        # Testa instância do automator
        automator = WebAutomator(headless=True)
        automator.cleanup()
        print("[OK] Motor de automação")

        # Testa interface (não abre janela)
        print("[OK] Interface carregada")

        return True

    except Exception as e:
        print(f"[ERRO] Falha no teste: {e}")
        return False

def main():
    """Função principal"""
    print_header()

    steps = [
        ("Verificação do Python", check_python_version),
        ("Instalação de dependências", install_dependencies),
        ("Teste de imports", test_imports),
        ("Criação de configuração", create_config),
        ("Teste do sistema", test_system)
    ]

    success_count = 0

    for step_name, step_func in steps:
        print(f"\n[STEP] {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"[FAIL] Falha em: {step_name}")
            break

    print("\n" + "=" * 60)

    if success_count == len(steps):
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Para executar o sistema:")
        print("  python launcher.py")
        print("  ou")
        print("  executar.bat")
        print()
        print("Funcionalidades disponíveis:")
        print("  • Interface moderna com CustomTkinter")
        print("  • Automação web robusta com Selenium")
        print("  • Sistema de configuração inteligente")
        print("  • Mapeamento automático de campos")
        print("  • Logs detalhados e tratamento de erros")
    else:
        print(f"❌ INSTALAÇÃO FALHADA ({success_count}/{len(steps)} passos)")
        print()
        print("Verifique os erros acima e tente novamente.")
        sys.exit(1)

    print("=" * 60)

if __name__ == "__main__":
    main()
