#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAUNCHER AUTOMATIZADOR IA v7.0
Ponto de entrada organizado e limpo
"""

import sys
import os
from pathlib import Path

def main():
    """Função principal do launcher v7.0"""
    try:
        print("Automator Web IA v7.0")
        print("Carregando arquitetura Clean Architecture...")

        # Adiciona src ao path
        current_dir = Path(__file__).parent
        src_path = current_dir / "src"

        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Executa a aplicação diretamente
        try:
            import subprocess
            import os

            # Executa o main_window.py diretamente
            main_window_path = src_path / "presentation" / "qt_views" / "main_window.py"
            env = os.environ.copy()
            env['PYTHONPATH'] = str(src_path)

            print("Iniciando aplicacao PySide6...")
            result = subprocess.run([
                sys.executable, str(main_window_path)
            ], env=env, cwd=current_dir)

            if result.returncode != 0:
                print(f"Aplicação encerrou com código: {result.returncode}")

        except Exception as e:
            print(f"Erro ao executar aplicação: {e}")
            # Fallback: tentar executar diretamente
            try:
                os.system(f'python "{src_path}/presentation/qt_views/main_window.py"')
            except Exception as e2:
                print(f"Fallback também falhou: {e2}")
                raise e

        except ImportError as e:
            print(f"Erro de importacao: {e}")
            print("Tentando metodo alternativo...")

            # Método alternativo - executar diretamente
            try:
                os.system("python src/presentation/qt_views/main_window.py")
            except Exception as e2:
                print(f"Falha no metodo alternativo: {e2}")
                raise e

    except ImportError as e:
        print(f"Erro ao importar v7.0: {e}")
        print("Certifique-se de que todas as dependencias estao instaladas:")
        print("   pip install PySide6 playwright sqlalchemy loguru")
        input("Pressione Enter para continuar...")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nAplicacao interrompida.")
        sys.exit(0)

    except Exception as e:
        print(f"Erro critico: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para continuar...")
        sys.exit(1)

if __name__ == "__main__":
    main()