#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DA GUI - Caminho da Configuração
"""

import sys
import os

def testar_gui_config():
    print("TESTE DA GUI - CAMINHO DA CONFIGURAÇÃO")
    print("=" * 50)

    # Simular exatamente o que a GUI faz
    print("Simulando inicialização da GUI...")

    # Calcular caminhos absolutos (como na GUI)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"current_dir (de dentro de gui.py): {current_dir}")

    # Se estamos em src/, o current_dir será src
    # Então project_root deve ser o diretório pai
    if os.path.basename(current_dir) == 'src':
        project_root = os.path.dirname(current_dir)
        print("[INFO] Estamos em src/, project_root = dirname(current_dir)")
    else:
        project_root = current_dir
        print("[INFO] Não estamos em src/, project_root = current_dir")

    print(f"project_root calculado: {project_root}")
    config_path = os.path.join(project_root, 'config', 'config.ini')
    print(f"config_path calculado: {config_path}")

    # Verificar se existe
    if os.path.exists(config_path):
        print("[OK] Arquivo config.ini encontrado no caminho calculado!")

        # Tentar ler como a GUI faz
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)

            print("[OK] Configuração lida com sucesso!")
            print(f"Seções: {config.sections()}")

            # Testar escrita (como no save_config)
            print("\nTestando escrita...")
            with open(config_path, 'w') as f:
                config.write(f)
            print("[OK] Escrita realizada com sucesso!")

        except Exception as e:
            print(f"[ERRO] Falha na leitura/escrita: {e}")

    else:
        print("[ERRO] Arquivo config.ini NÃO encontrado!")
        print(f"Caminho tentado: {config_path}")

        # Verificar estrutura
        print("Verificando estrutura de pastas...")
        print(f"current_dir existe: {os.path.exists(current_dir)}")
        print(f"project_root existe: {os.path.exists(project_root)}")

        config_dir = os.path.join(project_root, 'config')
        print(f"config_dir: {config_dir}")
        print(f"config_dir existe: {os.path.exists(config_dir)}")

        if os.path.exists(config_dir):
            files = os.listdir(config_dir)
            print(f"Arquivos em config/: {files}")

    print("=" * 50)

if __name__ == '__main__':
    testar_gui_config()
