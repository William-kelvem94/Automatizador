#!/usr/bin/env python3
"""
VERIFICACAO RAPIDA - Automator Web IA v8.0
"""

import os
from pathlib import Path

def main():
    print("VERIFICACAO RAPIDA - AUTOMATOR WEB IA v8.0")
    print("=" * 50)

    project_root = Path(__file__).parent.parent

    # Verificar requirements.txt
    req_path = project_root / "config" / "requirements.txt"
    if req_path.exists():
        try:
            with open(req_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            packages = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            print(f"Requirements.txt: {len(packages)} pacotes encontrados")
        except Exception as e:
            print(f"Erro no requirements.txt: {e}")
    else:
        print("requirements.txt nao encontrado")

    # Verificar arquivos Python
    src_path = project_root / "src"
    if src_path.exists():
        py_files = list(src_path.rglob("*.py"))
        print(f"Arquivos Python: {len(py_files)}")

        # Contar linhas de codigo aproximadas
        total_lines = 0
        for py_file in py_files[:10]:  # Apenas primeiros 10 para velocidade
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        print(f"Linhas de codigo (amostra): {total_lines}")
    else:
        print("Diretorio src nao encontrado")

    # Verificar estrutura de diretorios
    dirs_to_check = ["k8s", "tests", "build", "scripts"]
    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"{dir_name}/: OK ({len(list(dir_path.rglob('*')))} arquivos)")
        else:
            print(f"{dir_name}/: AUSENTE")

    print("\nPROJETO PRONTO PARA OTIMIZACAO!")
    print("- Implemente lazy loading")
    print("- Configure build otimizado")
    print("- Aplique otimizacoes de performance")

if __name__ == "__main__":
    main()
