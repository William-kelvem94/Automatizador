#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE COMPLETO DE CAMINHOS
"""

import sys
import os

def testar_caminhos():
    print("TESTE COMPLETO DE CAMINHOS")
    print("=" * 60)

    # Teste 1: Quando executado da raiz
    print("\n[TESTE 1] Executado da RAIZ do projeto")
    current_dir_raiz = "E:\\GitHub\\ABRIDOR DE SITE"  # Simular
    project_root_raiz = current_dir_raiz
    config_path_raiz = os.path.join(project_root_raiz, 'config', 'config.ini')
    print(f"current_dir: {current_dir_raiz}")
    print(f"project_root: {project_root_raiz}")
    print(f"config_path: {config_path_raiz}")
    print(f"Arquivo existe: {os.path.exists(config_path_raiz)}")

    # Teste 2: Quando executado de src/
    print("\n[TESTE 2] Executado de dentro de SRC/")
    current_dir_src = "E:\\GitHub\\ABRIDOR DE SITE\\src"
    project_root_src = os.path.dirname(current_dir_src)
    config_path_src = os.path.join(project_root_src, 'config', 'config.ini')
    print(f"current_dir: {current_dir_src}")
    print(f"project_root: {project_root_src}")
    print(f"config_path: {config_path_src}")
    print(f"Arquivo existe: {os.path.exists(config_path_src)}")

    # Teste 3: Lógica atual da GUI
    print("\n[TESTE 3] Lógica atual da GUI (de qualquer lugar)")
    current_dir_atual = os.path.dirname(os.path.abspath(__file__))
    print(f"os.path.dirname(os.path.abspath(__file__)): {current_dir_atual}")

    # A lógica atual: project_root = dirname(current_dir) se em src, senão current_dir
    basename_current = os.path.basename(current_dir_atual)
    if basename_current == 'src':
        project_root_atual = os.path.dirname(current_dir_atual)
        print("Detectado que estamos em 'src/' - usando dirname")
    else:
        project_root_atual = current_dir_atual
        print("Não estamos em 'src/' - usando current_dir")

    config_path_atual = os.path.join(project_root_atual, 'config', 'config.ini')
    print(f"project_root calculado: {project_root_atual}")
    print(f"config_path calculado: {config_path_atual}")
    print(f"Arquivo existe: {os.path.exists(config_path_atual)}")

    # Teste 4: Caminhos relativos problemáticos
    print("\n[TESTE 4] Caminhos relativos problemáticos")
    try:
        # Simular '../config/config.ini' de diferentes locais
        relative_from_raiz = os.path.abspath('../config/config.ini')
        print(f"De RAIZ '../config/config.ini' -> {relative_from_raiz}")
        print(f"Existe: {os.path.exists(relative_from_raiz)}")

        relative_from_src = os.path.abspath('E:\\GitHub\\ABRIDOR DE SITE\\src\\../config/config.ini')
        print(f"De SRC '../config/config.ini' -> {relative_from_src}")
        print(f"Existe: {os.path.exists(relative_from_src)}")

    except Exception as e:
        print(f"Erro nos caminhos relativos: {e}")

    # Teste 5: Verificar se há algum arquivo com "confug"
    print("\n[TESTE 5] Verificando possíveis erros de digitação")
    config_dir = "E:\\GitHub\\ABRIDOR DE SITE\\config"
    if os.path.exists(config_dir):
        files = os.listdir(config_dir)
        print(f"Arquivos em config/: {files}")

        for file in files:
            if 'conf' in file.lower():
                print(f"Arquivo suspeito encontrado: {file}")

    # Conclusão
    print("\n" + "=" * 60)
    print("ANÁLISE DOS CAMINHOS:")
    print("- Caminhos absolutos funcionam corretamente")
    print("- Caminhos relativos podem falhar dependendo do local de execução")
    print("- A lógica atual da GUI deve funcionar corretamente")
    if os.path.exists(config_path_atual):
        print("- Arquivo de configuração encontrado no caminho calculado")
    else:
        print("- PROBLEMA: Arquivo de configuração NÃO encontrado!")

    print("=" * 60)

if __name__ == '__main__':
    testar_caminhos()
