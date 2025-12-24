#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAUNCHER ENTERPRISE v9.0 - Automator Web IA
Launcher otimizado com lazy loading, cache inteligente e startup rápido
"""

import sys
import os
import time
import gc
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Configurações de performance antes de qualquer import
os.environ['PYTHONOPTIMIZE'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONPATH'] = str(Path(__file__).parent / "src")

# Lazy importer enterprise
from src.shared.utils.lazy_importer_enterprise import lazy_importer, lazy_import, preload_category

class EnterpriseLauncher:
    """
    Launcher Enterprise com otimizações avançadas

    Features:
    - Lazy loading inteligente
    - Preload assíncrono
    - Memory optimization
    - Error recovery avançado
    """

    def __init__(self):
        self.start_time = time.time()
        self._preload_thread: Optional[threading.Thread] = None

        # Configurar GC agressivo
        gc.set_threshold(700, 10, 10)
        gc.disable()  # Desabilitar durante startup

        # Configurações de ambiente
        self._configure_environment()

    def _configure_environment(self):
        """Configurar ambiente otimizado"""

        # Performance optimizations
        os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
        os.environ.setdefault('QTWEBENGINE_DISABLE_SANDBOX', '1')
        os.environ.setdefault('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', '1')

        # Memory optimizations
        os.environ.setdefault('OMP_NUM_THREADS', '1')
        os.environ.setdefault('MKL_NUM_THREADS', '1')
        os.environ.setdefault('NUMEXPR_NUM_THREADS', '1')

        # Automator specific
        os.environ.setdefault('AUTOMATOR_VERSION', '9.0.0')
        os.environ.setdefault('AUTOMATOR_ENV', 'production')

    def preload_core_async(self):
        """Pré-carregar componentes core de forma assíncrona"""

        def _preload():
            try:
                # Pequena pausa para permitir UI aparecer
                time.sleep(0.1)

                # Preload core modules
                core_loaded = preload_category('core')

                # Preload database se disponível
                try:
                    preload_category('database')
                except:
                    pass

                print(f"📦 Preloaded {len(core_loaded)} core modules")

            except Exception as e:
                print(f"Warning: Async preload failed: {e}")

        self._preload_thread = threading.Thread(target=_preload, daemon=True)
        self._preload_thread.start()

    def launch_gui(self) -> int:
        """Lançar interface gráfica otimizada"""
        try:
            print("Automator Web IA v9.0 - Enterprise Edition")
            print("Inicializando com otimizacoes avancadas...")

            # Start async preload
            self.preload_core_async()

            # Import e launch GUI (lazy)
            gui_module = lazy_import('src.presentation.qt_views.main_window')
            if not gui_module:
                print("❌ Falha ao carregar interface gráfica")
                return 1

            # Launch GUI
            startup_time = time.time() - self.start_time
            print(f"GUI inicializada em {startup_time:.2f}s")
            # Re-enable GC após startup
            gc.enable()

            # Launch application
            result = gui_module.main()

            # Cleanup
            self._cleanup()

            return result if isinstance(result, int) else 0

        except KeyboardInterrupt:
            print("\n👋 Aplicação interrompida pelo usuário")
            return 0
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def launch_cli(self, args) -> int:
        """Lançar interface CLI otimizada"""
        try:
            cli_module = lazy_import('src.presentation.cli.automator_cli')
            if not cli_module:
                print("❌ Falha ao carregar CLI")
                return 1

            return cli_module.main()

        except Exception as e:
            print(f"❌ Erro CLI: {e}")
            return 1

    def launch_api(self, host: str = '0.0.0.0', port: int = 8000) -> int:
        """Lançar servidor API otimizado"""
        try:
            # Import async modules
            uvicorn = lazy_import('uvicorn')
            if not uvicorn:
                print("❌ Uvicorn não disponível")
                return 1

            # Import app
            app_module = lazy_import('src.presentation.apis.fastapi_app')
            if not app_module:
                print("❌ Falha ao carregar API")
                return 1

            print(f"🌐 Iniciando API server em {host}:{port}")

            uvicorn.run(
                app_module.app,
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )

            return 0

        except Exception as e:
            print(f"❌ Erro API: {e}")
            return 1

    def _cleanup(self):
        """Limpeza otimizada"""
        try:
            # Force GC
            gc.collect()

            # Clear caches if needed
            if self._preload_thread and self._preload_thread.is_alive():
                self._preload_thread.join(timeout=1.0)

            # Log stats
            stats = lazy_importer.get_stats()
            print("📊 Stats finais:")
            print(f"  • Módulos carregados: {stats['loaded_modules']}")
            print(f"  Cache size: {stats['cache_size_mb']:.1f}MB")
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")


def main():
    """Função principal do launcher enterprise"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Automator Web IA v9.0 - Enterprise Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Interface gráfica (padrão)
  python launcher_enterprise.py

  # Interface CLI
  python launcher_enterprise.py --mode cli --help

  # Servidor API
  python launcher_enterprise.py --mode api --host 0.0.0.0 --port 8000

  # Stats do lazy importer
  python launcher_enterprise.py --stats
        """
    )

    parser.add_argument('--mode', '-m',
                       choices=['gui', 'cli', 'api'],
                       default='gui',
                       help='Modo de execução')

    parser.add_argument('--host',
                       default='127.0.0.1',
                       help='Host para API server')

    parser.add_argument('--port', '-p',
                       type=int,
                       default=8000,
                       help='Porta para API server')

    parser.add_argument('--stats',
                       action='store_true',
                       help='Mostrar estatísticas do lazy importer')

    parser.add_argument('--preload',
                       choices=lazy_importer._module_categories.keys(),
                       help='Pré-carregar categoria específica')

    args = parser.parse_args()

    # Initialize enterprise launcher
    launcher = EnterpriseLauncher()

    # Handle special commands
    if args.stats:
        stats = lazy_importer.get_stats()
        print("Lazy Importer Statistics:")
        print(f"  Loaded modules: {stats['loaded_modules']}")
        print(f"  Cache size: {stats['cache_size_mb']:.1f}MB")
        print(f"  Cache hit ratio: {stats['cache_hit_ratio']:.1%}")
        print(f"  Categories: {stats['categories']}")
        return 0

    if args.preload:
        print(f"Preloading category: {args.preload}")
        loaded = preload_category(args.preload)
        print(f"Loaded {len(loaded)} modules: {loaded}")
        return 0

    # Launch appropriate mode
    if args.mode == 'gui':
        return launcher.launch_gui()
    elif args.mode == 'cli':
        return launcher.launch_cli(args)
    elif args.mode == 'api':
        return launcher.launch_api(args.host, args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
