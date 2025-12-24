#!/usr/bin/env python3
from login_automator import LoginAutomator

print("Testando LoginAutomator...")

try:
    automator = LoginAutomator('config.ini')
    print("LoginAutomator criado com sucesso")

    print("Testando perform_login...")
    result = automator.run_once()
    print(f"Resultado: {result}")

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
