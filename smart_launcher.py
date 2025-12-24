#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMART LAUNCHER v8.0
Launcher inteligente com detecção automática de ambiente
Suporte a múltiplas plataformas e modos de execução
"""

import os
import sys
import platform
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# Adiciona src ao path se necessário
current_file = Path(__file__).resolve()
project_root = current_file.parent
src_dir = project_root / "src"

for path in [str(project_root), str(src_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Imports da aplicação
from src.shared.utils.logger import get_logger

# Logger
logger = get_logger(__name__)

class SmartLauncher:
    """Launcher inteligente para múltiplos ambientes"""

    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.python_version = sys.version_info

        # Detectar ambiente
        self.environment = self._detect_environment()
        self.is_frozen = getattr(sys, 'frozen', False)

        # Configurações
        self.config = self._load_config()

        logger.info(f"Smart Launcher v8.0 inicializado - Ambiente: {self.environment}")

    def _detect_environment(self) -> str:
        """Detectar ambiente de execução"""
        # Verificar se está congelado (PyInstaller)
        if getattr(sys, 'frozen', False):
            return "frozen"

        # Verificar se está em container Docker
        if os.path.exists('/.dockerenv') or os.environ.get('AUTOMATOR_BUILD_TYPE') == 'container':
            return "docker"

        # Verificar WSL
        if self.system == 'linux' and 'microsoft' in platform.release().lower():
            return "wsl"

        # Verificar se está em ambiente de desenvolvimento
        if (project_root / ".git").exists():
            return "development"

        # Ambiente de produção
        return "production"

    def _load_config(self) -> Dict[str, Any]:
        """Carregar configurações do launcher"""
        config_file = project_root / "config" / "launcher.json"

        default_config = {
            "version": "8.0.0",
            "default_mode": "gui",
            "supported_modes": ["gui", "cli", "api", "web"],
            "environments": {
                "development": {
                    "debug": True,
                    "auto_reload": True,
                    "log_level": "DEBUG"
                },
                "production": {
                    "debug": False,
                    "auto_reload": False,
                    "log_level": "INFO"
                },
                "frozen": {
                    "debug": False,
                    "auto_reload": False,
                    "log_level": "WARNING"
                },
                "docker": {
                    "debug": False,
                    "auto_reload": False,
                    "log_level": "INFO"
                }
            },
            "features": {
                "web_api": True,
                "web_ui": False,  # Ainda não implementado completamente
                "monitoring": True,
                "telemetry": False
            }
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge com default
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.warning(f"Erro ao carregar config: {e}")

        return default_config

    def _check_requirements(self) -> bool:
        """Verificar pré-requisitos do sistema"""
        logger.info("Verificando pré-requisitos do sistema...")

        issues = []

        # Verificar Python versão
        if self.python_version < (3, 11):
            issues.append(f"Python 3.11+ requerido, encontrado {self.python_version}")

        # Verificar espaço em disco
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            if free_gb < 2:
                issues.append(".1f"        # Verificar memória
        try:
            import psutil
            memory_gb = psutil.virtual_memory().available / (1024**3)
            if memory_gb < 2:
                issues.append(".1f"        except ImportError:
            logger.debug("psutil não disponível para verificação de memória")

        # Verificar se está em ambiente adequado
        if self.environment == "frozen" and not self.is_frozen:
            issues.append("Executável congelado esperado, mas não encontrado")

        if issues:
            logger.error("Pré-requisitos não atendidos:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False

        logger.info("✅ Pré-requisitos verificados com sucesso")
        return True

    def _setup_environment(self) -> None:
        """Configurar ambiente de execução"""
        logger.info("Configurando ambiente de execução...")

        env_config = self.config["environments"].get(self.environment, {})

        # Configurar variáveis de ambiente
        os.environ['AUTOMATOR_ENV'] = self.environment
        os.environ['AUTOMATOR_VERSION'] = self.config['version']
        os.environ['AUTOMATOR_BUILD_TYPE'] = 'frozen' if self.is_frozen else 'source'

        # Configurações específicas do ambiente
        if env_config.get('debug'):
            os.environ['AUTOMATOR_DEBUG'] = '1'

        os.environ['LOGURU_LEVEL'] = env_config.get('log_level', 'INFO')

        # Configurações específicas por sistema
        if self.system == 'windows':
            self._setup_windows_environment()
        elif self.system == 'darwin':
            self._setup_macos_environment()
        elif self.system == 'linux':
            self._setup_linux_environment()

        # Configurações de performance
        if self.environment in ['production', 'frozen']:
            os.environ['PYTHONOPTIMIZE'] = '1'
            os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

        logger.info("✅ Ambiente configurado")

    def _setup_windows_environment(self):
        """Configurações específicas para Windows"""
        # Configurar encodings
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'

        # Configurar Qt
        os.environ['QT_QPA_PLATFORM'] = 'windows:fontengine=freetype'

    def _setup_macos_environment(self):
        """Configurações específicas para macOS"""
        # Configurar locale
        os.environ['LC_ALL'] = 'en_US.UTF-8'
        os.environ['LANG'] = 'en_US.UTF-8'

        # Configurar Qt
        os.environ['QT_QPA_PLATFORM'] = 'cocoa'

    def _setup_linux_environment(self):
        """Configurações específicas para Linux"""
        # Configurar locale
        os.environ['LC_ALL'] = 'C.UTF-8'
        os.environ['LANG'] = 'C.UTF-8'

        # Configurar Qt
        if self.environment == 'docker':
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        else:
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

    def _launch_application(self, mode: str, args: Dict[str, Any]) -> int:
        """Lançar aplicação no modo especificado"""
        logger.info(f"Lançando aplicação em modo: {mode}")

        try:
            if mode == "gui":
                return self._launch_gui_mode(args)
            elif mode == "cli":
                return self._launch_cli_mode(args)
            elif mode == "api":
                return self._launch_api_mode(args)
            elif mode == "web":
                return self._launch_web_mode(args)
            else:
                logger.error(f"Modo não suportado: {mode}")
                return 1

        except Exception as e:
            logger.error(f"Erro ao lançar aplicação: {e}")
            return 1

    def _launch_gui_mode(self, args: Dict[str, Any]) -> int:
        """Lançar interface gráfica"""
        try:
            from src.presentation.qt_views.main_window import main
            return main()
        except ImportError as e:
            logger.error(f"Erro ao importar GUI: {e}")
            return 1

    def _launch_cli_mode(self, args: Dict[str, Any]) -> int:
        """Lançar interface de linha de comando"""
        try:
            from src.presentation.cli.automator_cli import main
            return main()
        except ImportError as e:
            logger.error(f"Erro ao importar CLI: {e}")
            return 1

    def _launch_api_mode(self, args: Dict[str, Any]) -> int:
        """Lançar servidor API"""
        try:
            import uvicorn
            from src.presentation.apis.fastapi_app import app

            host = args.get('host', '127.0.0.1')
            port = args.get('port', 8000)
            debug = self.config["environments"][self.environment].get('debug', False)

            logger.info(f"Iniciando API server em {host}:{port}")

            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=debug and self.environment == 'development',
                log_level="debug" if debug else "info"
            )

            return 0

        except ImportError as e:
            logger.error(f"Erro ao importar API: {e}")
            return 1

    def _launch_web_mode(self, args: Dict[str, Any]) -> int:
        """Lançar interface web completa (API + Web UI)"""
        logger.warning("Modo web ainda não implementado completamente")
        logger.info("Iniciando apenas API por enquanto...")

        # Por enquanto, lança apenas a API
        return self._launch_api_mode(args)

    def _create_desktop_shortcut(self) -> None:
        """Criar atalho na área de trabalho (se aplicável)"""
        if self.system == 'windows' and self.is_frozen:
            try:
                import winshell
                from win32com.client import Dispatch

                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, "Automator Web IA.lnk")

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.WorkingDirectory = str(project_root)
                shortcut.IconLocation = sys.executable
                shortcut.save()

                logger.info(f"Atalho criado: {shortcut_path}")

            except ImportError:
                logger.debug("winshell/win32com não disponível, pulando atalho")
            except Exception as e:
                logger.warning(f"Erro ao criar atalho: {e}")

    def launch(self, mode: Optional[str] = None, **kwargs) -> int:
        """Método principal de lançamento"""
        try:
            # Verificar pré-requisitos
            if not self._check_requirements():
                return 1

            # Configurar ambiente
            self._setup_environment()

            # Determinar modo
            if not mode:
                mode = self.config.get('default_mode', 'gui')

            # Validar modo
            if mode not in self.config['supported_modes']:
                logger.error(f"Modo não suportado: {mode}")
                logger.info(f"Modos suportados: {', '.join(self.config['supported_modes'])}")
                return 1

            # Log de inicialização
            logger.info(f"🚀 Automator Web IA v{self.config['version']} - Modo: {mode}")
            logger.info(f"🖥️ Sistema: {self.system} {self.machine}")
            logger.info(f"🐍 Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
            logger.info(f"🏭 Ambiente: {self.environment}")

            # Criar atalho se for primeira execução
            if self.environment == 'frozen':
                self._create_desktop_shortcut()

            # Lançar aplicação
            return self._launch_application(mode, kwargs)

        except KeyboardInterrupt:
            logger.info("Execução interrompida pelo usuário")
            return 0
        except Exception as e:
            logger.error(f"Erro crítico no launcher: {e}")
            return 1


def main():
    """Função principal do launcher"""
    parser = argparse.ArgumentParser(
        description="Automator Web IA v8.0 - Smart Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Interface gráfica (padrão)
  python smart_launcher.py

  # Interface de linha de comando
  python smart_launcher.py --mode cli

  # Servidor API
  python smart_launcher.py --mode api --host 0.0.0.0 --port 8000

  # Interface web completa
  python smart_launcher.py --mode web

  # Modo debug
  python smart_launcher.py --debug
        """
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['gui', 'cli', 'api', 'web'],
        help='Modo de execução'
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host para servidor API (padrão: 127.0.0.1)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='Porta para servidor API (padrão: 8000)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Habilitar modo debug'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Automator Web IA v8.0.0'
    )

    args = parser.parse_args()

    # Inicializar launcher
    launcher = SmartLauncher()

    # Lançar aplicação
    kwargs = {
        'host': args.host,
        'port': args.port,
        'debug': args.debug
    }

    sys.exit(launcher.launch(args.mode, **kwargs))


if __name__ == '__main__':
    main()
