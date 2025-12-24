#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ponto de entrada principal do Automatizador IA
Sistema inteligente de automação de login com interface moderna
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def main():
    """Função principal da aplicação"""
    try:
        # Importações dinâmicas para melhor performance
        from .ui.modern_interface import main as ui_main

        # Executa interface principal
        ui_main()

    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("pip install -r config/requirements.txt")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário.")
        sys.exit(0)

    except Exception as e:
        print(f"Erro crítico na aplicação: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()