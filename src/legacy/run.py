#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicialização simplificado para o Automatizador de Login
"""

import sys
import os

def main():
    """Função principal de inicialização"""
    print("============================================")
    print("        AUTOMATIZADOR DE LOGIN")
    print("============================================")
    print()

    # Verificar se estamos no diretório correto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[INFO] Diretorio atual: {current_dir}")

    # Importar e executar a interface gráfica
    try:
        print("[INFO] Carregando interface grafica...")
        from gui import main as gui_program
        print("[OK] Interface grafica carregada com sucesso!")
        print("[INFO] Abrindo interface...")
        print()

        # Executar a interface gráfica
        gui_program()

    except ImportError as e:
        print(f"[ERRO] Erro ao importar modulos: {e}")
        print("[INFO] Verifique se todas as dependencias estao instaladas.")
        print("[INFO] Execute: install.bat")
        input("Pressione Enter para continuar...")

    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        input("Pressione Enter para continuar...")

if __name__ == '__main__':
    main()
