#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ponto de entrada principal do Automatizador IA
Sistema inteligente de automação de login com interface moderna
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    log_dir = root_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "automator.log"

    handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def main():
    """Função principal da aplicação"""
    setup_logging()
    logger = logging.getLogger("main")
    logger.info("Iniciando Automatizador IA v5.0")

    try:
        # Importações dinâmicas para melhor performance
        from .ui.main_window import main as ui_main

        # Executa interface principal
        ui_main()

    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        print(f"Erro de importação: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("pip install -r config/requirements.txt")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário.")
        print("\nAplicação interrompida pelo usuário.")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Erro crítico na aplicação: {e}", exc_info=True)
        print(f"Erro crítico na aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
