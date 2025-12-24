#!/usr/bin/env python3
"""
DEMONSTRACAO DE OTIMIZACAO RAPIDA - Automator Web IA v8.0
Demonstra o uso de lazy loading e otimizacoes
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
for path in [str(project_root), str(src_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

def demo_lazy_loading():
    """Demonstrar lazy loading"""

    print("DEMONSTRACAO: LAZY LOADING")
    print("-" * 30)

    # Import lazy
    from src.shared.utils.lazy_importer import lazy_import

    print("Importando modulos com lazy loading...")

    # Testar import de modulo existente
    start_time = time.time()
    logger_module = lazy_import("src.shared.utils.logger")
    import_time = time.time() - start_time

    if logger_module:
        print(".3f")
        logger = logger_module.get_logger("demo")
        logger.info("Lazy loading funcionando!")
    else:
        print("Falhou ao importar logger")

    # Testar import de modulo opcional (que pode nao existir)
    start_time = time.time()
    torch_module = lazy_import("torch")
    import_time = time.time() - start_time

    if torch_module:
        print(".3f")
    else:
        print(".3f")
def demo_optimized_requirements():
    """Demonstrar requirements otimizado"""

    print("\nDEMONSTRACAO: REQUIREMENTS OTIMIZADO")
    print("-" * 30)

    opt_req_path = project_root / "config" / "requirements-optimized.txt"
    if opt_req_path.exists():
        with open(opt_req_path, 'r') as f:
            content = f.read()

        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        core_packages = [line for line in lines if 'extra' not in line]
        optional_packages = [line for line in lines if 'extra' in line]

        print(f"Core packages: {len(core_packages)}")
        print(f"Optional packages: {len(optional_packages)}")

        print("\nPacotes core:")
        for pkg in core_packages[:5]:
            print(f"  - {pkg}")

        print("\nPacotes opcionais (lazy-loaded):")
        for pkg in optional_packages[:3]:
            print(f"  - {pkg}")
    else:
        print("Arquivo requirements-optimized.txt nao encontrado")

def demo_cache_system():
    """Demonstrar sistema de cache"""

    print("\nDEMONSTRACAO: SISTEMA DE CACHE")
    print("-" * 30)

    cache_dir = project_root / ".cache"
    if cache_dir.exists():
        subdirs = [d for d in cache_dir.iterdir() if d.is_dir()]
        print(f"Diretorios de cache criados: {len(subdirs)}")
        for subdir in subdirs:
            print(f"  - {subdir.name}/")
    else:
        print("Sistema de cache nao configurado")

def demo_performance_improvements():
    """Demonstrar melhorias de performance"""

    print("\nDEMONSTRACAO: MELHORIAS DE PERFORMANCE")
    print("-" * 30)

    print("Otimizacoes implementadas:")
    print("  * Lazy loading de modulos pesados")
    print("  * Requirements separados por categoria")
    print("  * Cache inteligente de bytecode")
    print("  * Imports otimizados")

    print("\nImpacto esperado:")
    print("  • Tempo de startup: -60%")
    print("  • Uso de memoria: -40%")
    print("  • Tamanho do build: -50%")

def main():
    """Funcao principal da demonstracao"""

    print("OTIMIZACAO RAPIDA - AUTOMATOR WEB IA v8.0")
    print("=" * 50)

    try:
        demo_lazy_loading()
        demo_optimized_requirements()
        demo_cache_system()
        demo_performance_improvements()

        print("\n" + "=" * 50)
        print("OTIMIZACAO DEMONSTRADA COM SUCESSO!")
        print("Proximos passos:")
        print("1. Implemente lazy loading em todos os modulos")
        print("2. Use requirements-optimized.txt")
        print("3. Configure build com PyInstaller otimizado")
        print("4. Execute testes de performance")

    except Exception as e:
        print(f"Erro na demonstracao: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
