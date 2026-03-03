import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    print("[INFO] Verificando dependências...")
    req_file = Path("config/requirements.txt")
    if not req_file.exists():
        print("[ERRO] Arquivo config/requirements.txt não encontrado!")
        return False
    
    try:
        # Tenta instalar as dependências silenciosamente
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.STDOUT)
        print("[OK] Dependências instaladas/atualizadas.")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao instalar dependências: {e}")
        return False

def run_app():
    print("[INFO] Iniciando Automatizador IA v5.0...")
    main_py = Path("src/main.py")
    if not main_py.exists():
        print("[ERRO] src/main.py não encontrado!")
        return
    
    # Executa o projeto
    try:
        subprocess.run([sys.executable, str(main_py)])
    except KeyboardInterrupt:
        print("\n[INFO] Aplicação encerrada pelo usuário.")
    except Exception as e:
        print(f"[ERRO] Erro ao executar a aplicação: {e}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*50)
    print("      🚀 AUTOMATIZADOR IA v5.0 - AUTO-LOADER")
    print("="*50)
    
    if check_dependencies():
        run_app()
    else:
        print("[ALERTA] Tentando iniciar mesmo assim...")
        run_app()
    
    print("\nProcesso finalizado.")
    input("Pressione Enter para sair...")
