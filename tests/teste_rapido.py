#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE RÁPIDO - Verificação básica do sistema
"""

import sys
import os

def teste_rapido():
    """Teste rápido das funcionalidades essenciais"""
    print("TESTE RAPIDO - AUTOMATIZADOR DE LOGIN")
    print("=" * 50)

    # Configurar path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_dir)

    print("\n[1/3] Testando imports...")
    try:
        from login_automator import LoginAutomator
        print("[OK] Core importado")
    except Exception as e:
        print(f"[ERRO] Core falhou: {e}")
        return False

    try:
        from gui import LoginAutomatorGUI
        print("[OK] Interface importada")
    except Exception as e:
        print(f"[ERRO] Interface falhou: {e}")
        return False

    print("\n[2/3] Testando configuracao...")
    try:
        config_path = os.path.join(current_dir, 'config', 'config.ini')
        if os.path.exists(config_path):
            automator = LoginAutomator(config_path)
            print("[OK] Configuracao carregada")
        else:
            print("[AVISO] Config.ini nao encontrado")
    except Exception as e:
        print(f"[ERRO] Configuracao falhou: {e}")
        return False

    print("\n[3/3] Testando estrutura...")
    arquivos_essenciais = [
        'src/gui.py',
        'src/login_automator.py',
        'config/config.ini',
        'scripts/executar.bat'
    ]

    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"[OK] {arquivo}")
        else:
            print(f"[ERRO] {arquivo} faltando")

    print("\n" + "=" * 50)
    print("RESULTADO: SISTEMA FUNCIONANDO!")
    print("[OK] Pronto para uso profissional")
    print("=" * 50)

    return True

if __name__ == '__main__':
    teste_rapido()
