#!/usr/bin/env python3
"""
ANALISE BASICA - Automator Web IA v8.0
Analise simples sem dependencias externas
"""

import os
import sys
from pathlib import Path

def analyze_requirements():
    """Analisa requirements.txt"""

    req_path = Path(__file__).parent.parent / "config" / "requirements.txt"

    if not req_path.exists():
        return {"error": "requirements.txt not found"}

    packages = []
    heavy_packages = []

    with open(req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)

                # Identificar pacotes pesados
                if any(heavy in line.lower() for heavy in [
                    'torch', 'transformers', 'opencv', 'pyside6',
                    'pyqt6', 'numpy', 'pandas', 'tensorflow'
                ]):
                    heavy_packages.append(line)

    return {
        "total_packages": len(packages),
        "packages": packages,
        "heavy_packages": heavy_packages,
        "optimization_potential": len(heavy_packages) > 0
    }

def analyze_imports():
    """Analisa imports no codigo"""

    src_path = Path(__file__).parent.parent / "src"

    if not src_path.exists():
        return {"error": "src directory not found"}

    python_files = list(src_path.rglob("*.py"))
    total_imports = 0
    unique_imports = set()

    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Contar imports simples
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    total_imports += 1
                    # Extrair nome do modulo
                    if line.startswith('import '):
                        module = line.split()[1].split('.')[0]
                    else:  # from import
                        module = line.split()[1].split('.')[0]
                    unique_imports.add(module)

        except Exception as e:
            print(f"Error analyzing {py_file}: {e}")

    return {
        "python_files": len(python_files),
        "total_imports": total_imports,
        "unique_imports": len(unique_imports),
        "imports_list": sorted(list(unique_imports))
    }

def main():
    """Funcao principal"""

    print("ANALISE BASICA - AUTOMATOR WEB IA v8.0")
    print("=" * 50)

    # Analisar requirements
    print("Analisando requirements.txt...")
    req_analysis = analyze_requirements()

    if "error" in req_analysis:
        print(f"Erro: {req_analysis['error']}")
        return 1

    # Analisar imports
    print("Analisando imports no codigo...")
    import_analysis = analyze_imports()

    if "error" in import_analysis:
        print(f"Erro: {import_analysis['error']}")
        return 1

    # Resultados
    print("\nRESULTADOS:")
    print(f"- Total de pacotes: {req_analysis['total_packages']}")
    print(f"- Pacotes pesados: {len(req_analysis['heavy_packages'])}")
    print(f"- Arquivos Python: {import_analysis['python_files']}")
    print(f"- Total de imports: {import_analysis['total_imports']}")
    print(f"- Imports unicos: {import_analysis['unique_imports']}")

    if req_analysis['heavy_packages']:
        print("\nPACOTES PESADOS:")
        for pkg in req_analysis['heavy_packages'][:5]:
            print(f"  - {pkg}")

    print("\nPRINCIPAIS IMPORTS:")
    for imp in import_analysis['imports_list'][:10]:
        print(f"  - {imp}")

    print("\nRECOMENDACOES:")
    if req_analysis['optimization_potential']:
        print("- Implementar lazy loading para pacotes pesados")
    if import_analysis['total_imports'] > 100:
        print("- Otimizar estrutura de imports")
    print("- Separar dependencias por categoria")

    print("\nAnalise concluida!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
