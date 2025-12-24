#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simples para testar se o navegador aparece visivelmente
"""

import os
import sys
import time
from login_automator import LoginAutomator

def main():
    print("[TEST] TESTANDO VISIBILIDADE DO NAVEGADOR")
    print("=" * 50)

    config_path = 'config/config.ini'
    if not os.path.exists(config_path):
        print("[EMOJI] Arquivo de configuração não encontrado")
        return

    try:
        print("[EMOJI] Criando instância do automatizador...")
        automator = LoginAutomator(config_path)
        print(f"[EMOJI] Automatizador criado (headless: {automator.headless})")

        print("\n[EMOJI] Configurando WebDriver...")
        driver = automator.setup_driver()
        print("[EMOJI] WebDriver configurado")

        print("\n[EMOJI] Acessando Google (teste de visibilidade)...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"[EMOJI] Página carregada: {title}")

        print("\n⏳ Aguardando 10 segundos para verificar se a janela está visível...")
        print("[EMOJI] VERIFIQUE SE UMA JANELA DO CHROME APARECEU NA SUA TELA!")

        for i in range(10, 0, -1):
            print(f"⏳ {i} segundos restantes...")
            time.sleep(1)

        driver.quit()
        print("[EMOJI] Teste concluído")

    except Exception as e:
        print(f"[EMOJI] Erro: {e}")

if __name__ == '__main__':
    main()
