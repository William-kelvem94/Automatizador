#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DE MAPEAMENTO - Simula a detecção de campos do site
"""

import sys
import os

def testar_mapeamento():
    """Testa a funcionalidade de mapeamento de campos"""
    print("TESTE DE MAPEAMENTO DE CAMPOS")
    print("=" * 50)

    # Configurar path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_dir)

    try:
        from login_automator import LoginAutomator
        print("[OK] Sistema de automacao carregado")

        # Carregar configuração
        config_path = os.path.join(current_dir, 'config', 'config.ini')
        automator = LoginAutomator(config_path)
        print("[OK] Automatizador inicializado")

        # Testar configuração do driver (sem executar)
        print("\n[TESTANDO] Configuracao do driver...")
        try:
            # Simular configuração sem abrir navegador
            options = automator._configure_chrome_options()
            print("[OK] Opcoes do Chrome configuradas")

            # Verificar se as estratégias existem
            strategies = [
                automator._try_chromedriver_manager,
                automator._try_system_chromedriver,
                automator._try_fallback_driver
            ]
            print(f"[OK] {len(strategies)} estrategias de driver disponiveis")

        except Exception as e:
            print(f"[ERRO] Configuracao do driver falhou: {e}")
            return False

        # Testar métodos de detecção
        print("\n[TESTANDO] Metodos de deteccao...")
        metodos_necessarios = [
            'validate_page',
            'smart_field_detection',
            'fallback_field_detection',
            'analyze_page_elements'
        ]

        for metodo in metodos_necessarios:
            if hasattr(automator, metodo):
                print(f"[OK] Metodo {metodo} disponivel")
            else:
                print(f"[ERRO] Metodo {metodo} faltando")
                return False

        # Verificar configuração dos seletores
        print("\n[VERIFICANDO] Seletores configurados...")
        if hasattr(automator, 'email_selector') and automator.email_selector:
            print(f"[OK] Seletor email: {automator.email_selector}")
        else:
            print("[INFO] Seletor email nao configurado (usara deteccao automatica)")

        if hasattr(automator, 'password_selector') and automator.password_selector:
            print(f"[OK] Seletor senha: {automator.password_selector}")
        else:
            print("[INFO] Seletor senha nao configurado (usara deteccao automatica)")

        if hasattr(automator, 'login_button_selector') and automator.login_button_selector:
            print(f"[OK] Seletor botao: {automator.login_button_selector}")
        else:
            print("[INFO] Seletor botao nao configurado (usara deteccao automatica)")

        print("\n" + "=" * 50)
        print("RESULTADO: MAPEAMENTO PRONTO!")
        print("[OK] Sistema de deteccao configurado")
        print("[OK] Metodos de fallback disponiveis")
        print("[OK] Estrategias multiplas implementadas")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"[ERRO] Falha no teste de mapeamento: {e}")
        return False

if __name__ == '__main__':
    testar_mapeamento()
