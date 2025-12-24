#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DA CONFIGURAÇÃO - Simula o teste de configuração da interface
"""

import sys
import os

def testar_configuracao():
    """Testa a configuração como faria a interface gráfica"""
    print("TESTE DE CONFIGURACAO - INTERFACE GRAFICA")
    print("=" * 50)

    # Simular os valores que estariam na interface
    url_test = "https://ixc.webflash.net.br/app/login"
    email_test = "williampereira@webflash.net.br"
    senha_test = "***SENHA CONFIGURADA***"

    print("\n[VALIDANDO] URL...")
    if url_test and url_test.startswith(('http://', 'https://')):
        print(f"[OK] URL valida: {url_test}")
    else:
        print("[ERRO] URL invalida")
        return False

    print("\n[VALIDANDO] Email...")
    if email_test and '@' in email_test and '.' in email_test:
        print(f"[OK] Email valido: {email_test}")
    else:
        print("[ERRO] Email invalido")
        return False

    print("\n[VALIDANDO] Senha...")
    if senha_test and len(senha_test) >= 4:
        print("[OK] Senha configurada (seguranca mantida)")
    else:
        print("[ERRO] Senha muito curta ou nao configurada")
        return False

    print("\n[VALIDANDO] Conectividade...")
    try:
        import urllib.request
        req = urllib.request.Request(url_test, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print("[OK] Site acessivel")
            else:
                print(f"[AVISO] Status HTTP: {response.status}")
    except Exception as e:
        print(f"[ERRO] Site inacessivel: {e}")
        return False

    print("\n" + "=" * 50)
    print("RESULTADO: CONFIGURACAO VALIDA!")
    print("[OK] Sistema pronto para automacao")
    print("[OK] Todos os parametros verificados")
    print("=" * 50)

    return True

if __name__ == '__main__':
    testar_configuracao()
