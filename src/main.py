#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import getpass
from login_automator import LoginAutomator

def configure_login(automator, config_file):
    """Configura as informações de login interativamente"""
    print("\n" + "="*50)
    print("        [CONFIG] CONFIGURACAO DE LOGIN")
    print("="*50)

    config = automator.config

    # Configurar URL
    print("\n[URL] PASSO 1: URL do Site de Login")
    current_url = config.get('SITE', 'url', fallback='')
    if current_url:
        print(f"URL atual: {current_url}")
        change = input("Deseja alterar? (s/n): ").strip().lower()
        if change == 'n':
            url = current_url
        else:
            url = input("Nova URL: ").strip()
    else:
        url = input("Digite a URL do site de login: ").strip()

    if url:
        config.set('SITE', 'url', url)
    else:
        print("[ERRO] URL e obrigatoria!")
        return

    # Configurar email
    print("\n[EMAIL] PASSO 2: E-mail de Login")
    current_email = config.get('CREDENTIALS', 'email', fallback='')
    if current_email:
        print(f"E-mail atual: {current_email}")
        change = input("Deseja alterar? (s/n): ").strip().lower()
        if change == 'n':
            email = current_email
        else:
            email = input("Novo e-mail: ").strip()
    else:
        email = input("Digite seu e-mail: ").strip()

    if email:
        config.set('CREDENTIALS', 'email', email)
    else:
        print("[ERRO] E-mail e obrigatorio!")
        return

    # Configurar senha
    print("\n[SENHA] PASSO 3: Senha de Login")
    print("[INFO] A senha sera oculta durante a digitacao")
    current_password = config.get('CREDENTIALS', 'password', fallback='')
    if current_password:
        change = input("Deseja alterar a senha? (s/n): ").strip().lower()
        if change == 'n':
            password = current_password
        else:
            password = getpass.getpass("Nova senha: ")
    else:
        password = getpass.getpass("Digite sua senha: ")

    if password:
        config.set('CREDENTIALS', 'password', password)
    else:
        print("[ERRO] Senha e obrigatoria!")
        return

    # Configurar horários
    print("\n[HORARIO] PASSO 4: Horarios de Login")
    print("[INFO] Digite os horarios no formato HH:MM (24h)")
    print("[INFO] Separe multiplos horarios com virgula")
    print("[INFO] Exemplo: 08:00, 12:00, 18:00, 22:00")

    current_horarios = config.get('SCHEDULE', 'horarios', fallback='')
    if current_horarios:
        print(f"Horários atuais: {current_horarios}")
        change = input("Deseja alterar? (s/n): ").strip().lower()
        if change == 'n':
            horarios = current_horarios
        else:
            horarios = input("Novos horários: ").strip()
    else:
        horarios = input("Digite os horários desejados: ").strip()

    if horarios:
        # Validar formato dos horários
        horario_list = [h.strip() for h in horarios.split(',')]
        horarios_validos = []

        for horario in horario_list:
            try:
                hora, minuto = horario.split(':')
                hora = int(hora)
                minuto = int(minuto)
                if 0 <= hora <= 23 and 0 <= minuto <= 59:
                    horarios_validos.append(horario)
                else:
                    print(f"[ERRO] Horario invalido: {horario}")
            except:
                print(f"[ERRO] Formato invalido: {horario} (use HH:MM)")

        if horarios_validos:
            config.set('SCHEDULE', 'horarios', ', '.join(horarios_validos))
        else:
            print("[ERRO] Nenhum horario valido informado!")
            return
    else:
        print("[ERRO] Pelo menos um horario e obrigatorio!")
        return

    # Salvar configuração
    try:
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        print("\n[OK] Configuracao salva com sucesso!")
        print("[INFO] Agora voce pode testar o login ou iniciar o agendador.")
    except Exception as e:
        print(f"[ERRO] Erro ao salvar configuracao: {e}")

def show_current_config(automator):
    """Mostra as configurações atuais"""
    print("\n" + "="*50)
    print("        [CONFIG] CONFIGURACOES ATUAIS")
    print("="*50)

    config = automator.config

    print("\n[SITE] SITE:")
    url = config.get('SITE', 'url', fallback='Nao configurado')
    print(f"   URL: {url}")

    email_selector = config.get('SITE', 'email_field_selector', fallback='Nao configurado')
    print(f"   Campo e-mail: {email_selector}")

    password_selector = config.get('SITE', 'password_field_selector', fallback='Nao configurado')
    print(f"   Campo senha: {password_selector}")

    button_selector = config.get('SITE', 'login_button_selector', fallback='Nao configurado')
    print(f"   Botao login: {button_selector}")

    print("\n[CREDENCIAIS] CREDENCIAIS:")
    email = config.get('CREDENTIALS', 'email', fallback='Nao configurado')
    if email != 'Nao configurado':
        print(f"   E-mail: {email}")
    else:
        print("   E-mail: Nao configurado")

    password = config.get('CREDENTIALS', 'password', fallback='')
    if password:
        print("   Senha: ********")
    else:
        print("   Senha: Nao configurada")

    print("\n[HORARIOS] HORARIOS:")
    horarios = config.get('SCHEDULE', 'horarios', fallback='Nao configurado')
    print(f"   Horarios programados: {horarios}")

    print("\n[SETTINGS] CONFIGURACOES:")
    headless = config.getboolean('SETTINGS', 'headless', fallback=False)
    print(f"   Modo headless: {'Sim' if headless else 'Nao'}")

    timeout = config.getint('SETTINGS', 'wait_timeout', fallback=10)
    print(f"   Tempo de espera: {timeout}s")

def main():
    parser = argparse.ArgumentParser(
        description='Automatizador de Login - Executa login automático em horários específicos'
    )

    parser.add_argument(
        '--config',
        default='config.ini',
        help='Arquivo de configuração (padrão: config.ini)'
    )

    parser.add_argument(
        '--map',
        action='store_true',
        help='Mapeia os campos de login da página e atualiza config'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Executa um teste de login único'
    )

    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Inicia o agendador para executar logins nos horários configurados'
    )

    args = parser.parse_args()

    # Cria instância do automatizador
    try:
        automator = LoginAutomator(args.config)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        sys.exit(1)

    if args.map:
        # Mapeia os campos de login
        print("Mapeando campos de login...")
        mapped_fields = automator.map_login_fields()

        if mapped_fields:
            print("Campos encontrados:")
            for field_type, selector in mapped_fields.items():
                print(f"  {field_type}: {selector}")

            # Atualiza a configuração
            config = automator.config
            if 'email' in mapped_fields:
                config.set('SITE', 'email_field_selector', mapped_fields['email'])
            if 'password' in mapped_fields:
                config.set('SITE', 'password_field_selector', mapped_fields['password'])
            if 'login_button' in mapped_fields:
                config.set('SITE', 'login_button_selector', mapped_fields['login_button'])

            # Salva a configuração
            with open(args.config, 'w') as configfile:
                config.write(configfile)

            print("Configuração atualizada com sucesso!")
        else:
            print("Não foi possível mapear os campos automaticamente.")
            print("Configure manualmente os seletores no arquivo config.ini")

    elif args.test:
        # Executa teste único
        print("Executando teste de login...")
        success = automator.run_once()
        if success:
            print("✓ Login realizado com sucesso!")
        else:
            print("✗ Falha no login. Verifique as configurações e logs.")

    elif args.schedule:
        # Inicia o agendador
        print("Iniciando agendador de logins...")
        print("O programa ficará executando em segundo plano.")
        print("Pressione Ctrl+C para interromper.")
        automator.start_scheduler()

    else:
        # Menu interativo
        while True:
            print("\n" + "="*50)
            print("        AUTOMATIZADOR DE LOGIN")
            print("="*50)
            print("1. [CONFIG] Configurar login (URL, email, senha, horarios)")
            print("2. [MAPEAR] Mapear campos de login automaticamente")
            print("3. [TESTAR] Testar login unico")
            print("4. [AGENDAR] Iniciar agendador automatico")
            print("5. [VER] Ver configuracoes atuais")
            print("6. [SAIR] Sair")

            try:
                choice = input("\nEscolha uma opção (1-6): ").strip()

                if choice == '1':
                    configure_login(automator, args.config)

                elif choice == '2':
                    print("\n[MAPEAR] Mapeando campos de login...")
                    mapped_fields = automator.map_login_fields()

                    if mapped_fields:
                        print("[OK] Campos encontrados:")
                        for field_type, selector in mapped_fields.items():
                            print(f"   {field_type}: {selector}")

                        # Atualiza configuração
                        config = automator.config
                        if 'email' in mapped_fields:
                            config.set('SITE', 'email_field_selector', mapped_fields['email'])
                        if 'password' in mapped_fields:
                            config.set('SITE', 'password_field_selector', mapped_fields['password'])
                        if 'login_button' in mapped_fields:
                            config.set('SITE', 'login_button_selector', mapped_fields['login_button'])

                        with open(args.config, 'w') as configfile:
                            config.write(configfile)

                        print("[OK] Configuracao atualizada!")
                    else:
                        print("[ERRO] Campos nao encontrados automaticamente.")
                        print("   Configure manualmente os seletores no arquivo config.ini")

                elif choice == '3':
                    print("\n[TESTAR] Testando login...")
                    success = automator.run_once()
                    if success:
                        print("[OK] Login realizado com sucesso!")
                    else:
                        print("[ERRO] Falha no login. Verifique as configuracoes e logs.")

                elif choice == '4':
                    print("\n[AGENDAR] Iniciando agendador automatico...")
                    print("[INFO] O programa ficara executando em segundo plano.")
                    print("[INFO] Pressione Ctrl+C para interromper.")
                    automator.start_scheduler()
                    break

                elif choice == '5':
                    show_current_config(automator)

                elif choice == '6':
                    print("\n[Ate logo!")
                    break

                else:
                    print("[ERRO] Opcao invalida! Escolha entre 1-6.")

            except KeyboardInterrupt:
                print("\n\n[Interrompido pelo usuario.")
                break
            except Exception as e:
                print(f"[ERRO] Erro: {e}")

if __name__ == '__main__':
    main()
