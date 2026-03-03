#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DA LÓGICA DA GUI
"""

import os
import sys


def testar_logica_gui():
    print("TESTE DA LÓGICA DA GUI")
    print("=" * 50)

    # Simular exatamente o código da GUI
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)

    print(f"Arquivo atual: {__file__}")
    print(f"current_file: {current_file}")
    print(f"current_dir: {current_dir}")
    print(f"'src' in current_dir: {'src' in current_dir}")

    # Lógica da GUI
    if "src" in current_dir:
        # Estamos dentro de src/, voltar para a raiz do projeto
        project_root = current_dir
        print(f"project_root inicial: {project_root}")
        print(f"os.path.basename(project_root): {os.path.basename(project_root)}")

        while os.path.basename(project_root) != "src":
            project_root = os.path.dirname(project_root)
            print(f"project_root no loop: {project_root}")
            print(f"os.path.basename(project_root): {os.path.basename(project_root)}")

        project_root = os.path.dirname(project_root)
        print(f"project_root final (from src): {project_root}")
    else:
        # Estamos na raiz ou outro local, assumir raiz do projeto
        project_root = current_dir
        print(f"project_root (not from src): {project_root}")

    config_path = os.path.join(project_root, "config", "config.ini")
    print(f"config_path final: {config_path}")
    print(f"Arquivo existe: {os.path.exists(config_path)}")

    if os.path.exists(config_path):
        print("[OK] Caminho da configuração está correto!")
    else:
        print("[ERRO] Caminho da configuração está INCORRETO!")

    print("=" * 50)


if __name__ == "__main__":
    testar_logica_gui()
