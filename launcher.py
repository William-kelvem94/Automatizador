#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher principal para o Automatizador IA
Resolve problemas de imports relativos quando executado diretamente
"""

import sys
import os
from pathlib import Path

def main():
    """Função principal do launcher"""
    try:
        # Tentar importar diretamente (para executável empacotado)
        try:
            from main import main as app_main
        except ImportError:
            # Método alternativo para desenvolvimento
            src_path = Path(__file__).parent / "src"
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            from src.main import main as app_main

        app_main()

    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("pip install -r config/requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Erro crítico na aplicação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
