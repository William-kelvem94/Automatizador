#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ferramenta para inspecionar elementos do site de login
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def inspecionar_site(url):
    """Abre o site e mostra informações sobre os campos de formulário"""

    print(f"Inspecionando: {url}")
    print("=" * 60)

    # Configurar driver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    try:
        # Primeiro tentar com ChromeDriverManager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
    except Exception as e:
        print(f"Erro com ChromeDriverManager: {e}")
        print("Tentando método alternativo...")
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e2:
            print(f"Erro geral: {e2}")
            return

    try:
        driver.get(url)
        time.sleep(5)  # Esperar página carregar

        print("[INFO] Procurando campos de formulario...")
        print()

        # Procurar inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Encontrados {len(inputs)} campos input:")

        for i, inp in enumerate(inputs):
            input_type = inp.get_attribute("type") or "text"
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            class_attr = inp.get_attribute("class") or ""

            print(f"  [{i+1}] Tipo: {input_type}")
            if name:
                print(f"      Name: {name}")
            if id_attr:
                print(f"      ID: {id_attr}")
            if placeholder:
                print(f"      Placeholder: {placeholder}")
            if class_attr:
                print(f"      Class: {class_attr}")
            print(
                f"      Seletor: input[type='{input_type}']"
                + (f"[name='{name}']" if name else "")
            )
            print()

        # Procurar todos os inputs (incluindo hidden)
        all_inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
        print(f"Encontrados {len(all_inputs)} campos de formulario totais:")

        for i, inp in enumerate(all_inputs):
            tag_name = inp.tag_name
            input_type = inp.get_attribute("type") or "text"
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            class_attr = inp.get_attribute("class") or ""

            print(f"  [{i+1}] {tag_name.upper()}[type='{input_type}']")
            if name:
                print(f"      Name: {name}")
            if id_attr:
                print(f"      ID: {id_attr}")
            if placeholder:
                print(f"      Placeholder: {placeholder}")
            if class_attr:
                print(f"      Class: {class_attr}")

            # Sugestão de seletor
            selector = (
                f"{tag_name}[name='{name}']"
                if name
                else f"{tag_name}[type='{input_type}']"
            )
            print(f"      Seletor sugerido: {selector}")
            print()

        # Procurar botões e links clicáveis
        buttons = driver.find_elements(
            By.CSS_SELECTOR, "button, input[type='submit'], a"
        )
        print(f"Encontrados {len(buttons)} elementos clicaveis:")

        for i, btn in enumerate(buttons):
            tag_name = btn.tag_name
            if tag_name == "a":
                href = btn.get_attribute("href") or ""
                text = btn.text.strip() or "[link]"
            else:
                href = ""
                text = btn.get_attribute("value") or btn.text.strip()

            name = btn.get_attribute("name") or ""
            id_attr = btn.get_attribute("id") or ""
            class_attr = btn.get_attribute("class") or ""

            print(f"  [{i+1}] {tag_name.upper()}: '{text}'")
            if name:
                print(f"      Name: {name}")
            if id_attr:
                print(f"      ID: {id_attr}")
            if class_attr:
                print(f"      Class: {class_attr}")
            if href:
                print(f"      Link: {href}")

            # Sugestão de seletor
            if name:
                selector = f"{tag_name}[name='{name}']"
            elif id_attr:
                selector = f"#{id_attr}"
            else:
                selector = tag_name
            print(f"      Seletor sugerido: {selector}")
            print()

        print("=" * 60)
        print("[DICA] DICAS:")
        print("• Copie os seletores que correspondem aos campos")
        print("• Para email: geralmente input[type='email']")
        print("• Para senha: geralmente input[type='password']")
        print("• Para botao: geralmente button[type='submit']")
        print("• Atualize o config.ini com os seletores corretos")
        print("• Use a interface grafica para mapeamento automatico")

    except Exception as e:
        print(f"Erro ao inspecionar: {e}")

    finally:
        print("\n[INFO] Fechando navegador em 3 segundos...")
        time.sleep(3)
        driver.quit()
        print("[OK] Analise concluida!")


def main():
    """Função principal"""
    print("[INSPECTOR] INSPECIONADOR DE CAMPOS DE LOGIN")
    print("=" * 50)

    # Ler URL do config
    import configparser

    config = configparser.ConfigParser()
    config.read("config.ini")

    url = config.get("SITE", "url", fallback="")
    if not url:
        print("[ERRO] URL nao configurada no config.ini")
        print("[INFO] Configure a URL na secao [SITE] do arquivo config.ini")
        return

    print(f"[INFO] Analisando URL: {url}")
    inspecionar_site(url)


if __name__ == "__main__":
    main()
