#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LOGGER COMPARTILHADO - LOGURU
Sistema de logging moderno para toda a aplicação
"""

from loguru import logger
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str) -> logger:
    """Retorna logger configurado para o módulo"""
    return logger.bind(module=name)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Configura sistema de logging"""

    # Remove handlers padrão
    logger.remove()

    # Níveis de log
    level_map = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL"
    }

    log_level = level_map.get(log_level.upper(), "INFO")

    # Formato do log
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[module]: <15}</cyan> | <level>{message}</level>"

    # Handler para console
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True,
        enqueue=True  # Thread-safe
    )

    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)

        logger.add(
            log_path,
            format=log_format,
            level=log_level,
            rotation="10 MB",  # Rotaciona arquivo a cada 10MB
            retention="1 week",  # Mantém logs por 1 semana
            encoding="utf-8",
            enqueue=True
        )
        print(f"Logs sendo salvos em: {log_path}")

    # Log inicial
    logger.bind(module="system").info("Sistema de logging inicializado")


def get_default_log_file() -> str:
    """Retorna caminho padrão para arquivo de log"""
    log_dir = Path.home() / ".automator_ia_v7" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / "automator.log")
