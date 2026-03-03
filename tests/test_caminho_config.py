#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DO CAMINHO DA CONFIGURAÇÃO
"""

import os
import sys


def testar_caminho_config():
    print("TESTE DO CAMINHO DA CONFIGURAÇÃO")
    print("=" * 50)

    # Simular como a GUI calcula o caminho
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Diretório atual: {current_dir}")

    # Simular cálculo do caminho da config como na GUI
    if "src" in current_dir:
        # Se estamos em src/, voltar um nível
        project_root = os.path.dirname(current_dir)
    else:
        # Se estamos na raiz
        project_root = current_dir

    print(f"Raiz do projeto: {project_root}")

    config_path = os.path.join(project_root, "config", "config.ini")
    print(f"Caminho da config: {config_path}")

    # Verificar se o arquivo existe
    if os.path.exists(config_path):
        print("[OK] Arquivo config.ini encontrado!")
        print(f"Tamanho: {os.path.getsize(config_path)} bytes")

        # Tentar ler
        try:
            import configparser

            config = configparser.ConfigParser()
            config.read(config_path)
            print("[OK] Configuração lida com sucesso!")

            # Mostrar seções
            sections = config.sections()
            print(f"Seções encontradas: {sections}")

        except Exception as e:
            print(f"[ERRO] Falha ao ler configuração: {e}")

    else:
        print("[ERRO] Arquivo config.ini NÃO encontrado!")
        print("Verificando estrutura de pastas...")

        # Verificar estrutura
        config_dir = os.path.join(project_root, "config")
        if os.path.exists(config_dir):
            print(f"[OK] Pasta config existe: {config_dir}")
            files_in_config = os.listdir(config_dir)
            print(f"Arquivos em config/: {files_in_config}")
        else:
            print(f"[ERRO] Pasta config NÃO existe: {config_dir}")

    print("=" * 50)


if __name__ == "__main__":
    testar_caminho_config()
