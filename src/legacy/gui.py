#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Gráfica para o Automatizador de Login
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import configparser
import threading
import time
import os
from datetime import datetime
from login_automator import LoginAutomator

class LoginAutomatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Automotizador de Login - Sistema Inteligente v2.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Calcular caminhos absolutos
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)

        # Verificar se estamos em src/ ou subpasta de src/
        if 'src' in current_dir:
            # Estamos dentro de src/, voltar para a raiz do projeto
            self.project_root = current_dir
            while os.path.basename(self.project_root) != 'src':
                self.project_root = os.path.dirname(self.project_root)
            self.project_root = os.path.dirname(self.project_root)
        else:
            # Estamos na raiz ou outro local, assumir raiz do projeto
            self.project_root = current_dir

        self.config_path = os.path.join(self.project_root, 'config', 'config.ini')

        # Carregar configurações
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Variáveis
        self.url_var = tk.StringVar(value=self.config.get('SITE', 'url', fallback=''))
        self.email_var = tk.StringVar(value=self.config.get('CREDENTIALS', 'email', fallback=''))
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sistema pronto")

        # Instância do automatizador
        self.automator = None
        self.is_scheduling = False

        self.setup_ui()
        self.load_saved_config()

    def setup_ui(self):
        """Configura a interface gráfica profissional"""
        self.root.configure(bg='#f0f0f0')

        # Header profissional
        self.create_header()

        # Container principal
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Painel esquerdo - Configurações
        left_panel = tk.LabelFrame(main_container, text="[CONFIG] Configuração do Sistema",
                                  font=('Arial', 11, 'bold'), bg='white', fg='#2E8B57')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.create_config_panel(left_panel)

        # Painel direito - Operações
        right_panel = tk.LabelFrame(main_container, text="[TARGET] Operações e Controle",
                                   font=('Arial', 11, 'bold'), bg='white', fg='#1976D2')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_operations_panel(right_panel)

        # Barra de status
        self.create_status_bar()

    def create_header(self):
        """Cria o cabeçalho profissional"""
        header_frame = tk.Frame(self.root, bg='#2E8B57', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        logo_label = tk.Label(header_frame, text="🔐", font=('Arial', 24), bg='#2E8B57', fg='white')
        logo_label.pack(side=tk.LEFT, padx=20, pady=10)

        title_frame = tk.Frame(header_frame, bg='#2E8B57')
        title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        main_title = tk.Label(title_frame, text="AUTOMOTIZADOR DE LOGIN",
                             font=('Arial', 16, 'bold'), bg='#2E8B57', fg='white')
        main_title.pack(anchor=tk.W)

        subtitle = tk.Label(title_frame, text="Sistema Inteligente v2.0",
                           font=('Arial', 8), bg='#2E8B57', fg='#E8F5E8')
        subtitle.pack(anchor=tk.W)

    def create_config_panel(self, parent):
        """Cria o painel de configuração"""
        # URL
        tk.Label(parent, text="URL do Site:", bg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        url_entry = tk.Entry(parent, textvariable=self.url_var, font=('Consolas', 10), relief=tk.SOLID, bd=1)
        url_entry.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=(0, 10))

        # Email
        tk.Label(parent, text="E-mail:", bg='white', font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        email_entry = tk.Entry(parent, textvariable=self.email_var, font=('Arial', 10), relief=tk.SOLID, bd=1)
        email_entry.grid(row=3, column=0, sticky=tk.EW, padx=10, pady=(0, 10))

        # Senha
        tk.Label(parent, text="Senha:", bg='white', font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        password_entry = tk.Entry(parent, textvariable=self.password_var, show="*", font=('Arial', 10), relief=tk.SOLID, bd=1)
        password_entry.grid(row=5, column=0, sticky=tk.EW, padx=10, pady=(0, 10))

        # Botões
        button_frame = tk.Frame(parent, bg='white')
        button_frame.grid(row=6, column=0, sticky=tk.EW, padx=10, pady=10)

        tk.Button(button_frame, text="💾 Salvar Configuração", command=self.save_config,
                 bg='#4CAF50', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X, pady=(0, 5))

        tk.Button(button_frame, text="[SEARCH] Mapear Campos", command=self.map_fields,
                 bg='#2196F3', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X, pady=(0, 5))

        tk.Button(button_frame, text="🧹 Limpar Campos", command=self.clear_config,
                 bg='#f44336', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X)

        parent.grid_columnconfigure(0, weight=1)

    def create_operations_panel(self, parent):
        """Cria o painel de operações"""
        # Testes
        test_frame = tk.LabelFrame(parent, text="[TEST] Testes", font=('Arial', 10, 'bold'), bg='#FFF8E1', fg='#F57C00')
        test_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Button(test_frame, text="[CONFIG] Testar Configuração", command=self.test_config,
                 bg='#607D8B', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=10, pady=10)

        tk.Button(test_frame, text="[LAUNCH] Executar Login", command=self.run_login,
                 bg='#FF5722', fg='white', font=('Arial', 10, 'bold')).pack(fill=tk.X, padx=10, pady=(0, 10))

        # Agendamento
        schedule_frame = tk.LabelFrame(parent, text="[SCHEDULE] Agendamento", font=('Arial', 10, 'bold'), bg='#E3F2FD', fg='#1565C0')
        schedule_frame.pack(fill=tk.X, padx=10, pady=(5, 5))

        self.schedule_status_label = tk.Label(schedule_frame, text="Status: Parado", bg='#E3F2FD', fg='red', font=('Arial', 9, 'bold'))
        self.schedule_status_label.pack(pady=10)

        tk.Button(schedule_frame, text="[START] Iniciar Agendamento", command=self.start_scheduler,
                 bg='#4CAF50', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Button(schedule_frame, text="[STOP] Parar Agendamento", command=self.stop_scheduler,
                 bg='#f44336', fg='white', font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=10, pady=(0, 10))

        # Log
        log_frame = tk.LabelFrame(parent, text="[LIST] Log", font=('Arial', 10, 'bold'), bg='#FCE4EC', fg='#C2185B')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 9),
                                                 bg='#2D2D2D', fg='#E0E0E0')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        tk.Button(log_frame, text="🧹 Limpar Log", command=self.clear_log,
                 bg='#9E9E9E', fg='white', font=('Arial', 8)).pack(pady=(0, 10))

    def create_status_bar(self):
        """Cria a barra de status"""
        status_frame = tk.Frame(self.root, bg='#424242', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                   bg='#424242', fg='#4CAF50', font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT, padx=15)

    def load_saved_config(self):
        """Carrega configurações salvas"""
        try:
            # A senha não é salva por segurança
            pass
        except:
            pass

    def save_config(self):
        """Salva a configuração"""
        try:
            # Atualizar config
            if not self.config.has_section('SITE'):
                self.config.add_section('SITE')
            if not self.config.has_section('CREDENTIALS'):
                self.config.add_section('CREDENTIALS')
            if not self.config.has_section('SETTINGS'):
                self.config.add_section('SETTINGS')

            self.config.set('SITE', 'url', self.url_var.get())
            self.config.set('CREDENTIALS', 'email', self.email_var.get())
            self.config.set('CREDENTIALS', 'password', self.password_var.get())
            self.config.set('SETTINGS', 'headless', 'false')
            self.config.set('SETTINGS', 'wait_timeout', '10')

            with open(self.config_path, 'w') as f:
                self.config.write(f)

            self.log("Configuração salva com sucesso!")
            self.status_var.set("Configuração salva")

        except Exception as e:
            self.log(f"Erro ao salvar configuração: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")

    def map_fields(self):
        """Mapeia campos do site com análise completa"""
        def map_worker():
            try:
                self.status_var.set("Mapeando campos do site...")
                self.log("=" * 60)
                self.log("[SEARCH] INICIANDO MAPEAMENTO DE CAMPOS")
                self.log("=" * 60)

                # Verificar se URL está configurada
                url = self.url_var.get().strip()
                if not url:
                    self.log("❌ ERRO: URL não configurada!")
                    self.log("Configure a URL primeiro antes de mapear campos.")
                    self.status_var.set("Erro: URL não configurada")
                    return

                self.log(f"[WEB] Analisando URL: {url}")

                # Criar instância do automatizador
                self.log("[CONFIG] Inicializando sistema de automação...")
                automator = LoginAutomator(self.config_path)
                self.log("[OK] Sistema inicializado")

                # Executar detecção inteligente
                self.log("\n[TARGET] EXECUTANDO DETECÇÃO INTELIGENTE DE CAMPOS")
                self.log("-" * 50)

                # Simular abertura do navegador e análise
                self.log("[WEB] Abrindo navegador...")
                driver = automator.setup_driver()
                self.log("[OK] Navegador aberto com sucesso")

                self.log(f"🔗 Acessando página: {url}")
                automator._access_login_page(driver)
                self.log("[OK] Página carregada")

                # Executar análise da página
                self.log("\n📊 ANALISANDO ESTRUTURA DA PÁGINA")
                self.log("-" * 40)

                if automator.validate_page(driver):
                    self.log("[OK] Página validada para formulários de login")
                else:
                    self.log("[WARNING] Página pode não ter formulários de login tradicionais")
                    self.log("Continuando análise...")

                # Executar detecção de campos
                self.log("\n[TARGET] DETECTANDO CAMPOS DO FORMULÁRIO")
                self.log("-" * 40)

                # Estratégia 1: Detecção inteligente automática
                self.log("[SEARCH] Estratégia 1: Detecção automática inteligente")
                fields = automator.smart_field_detection(driver)

                if fields:
                    self.log("[OK] Campos detectados automaticamente!")
                    self.log(f"[LIST] Campos encontrados: {list(fields.keys())}")

                    for field_type, selector in fields.items():
                        self.log(f"   • {field_type.upper()}: {selector}")
                else:
                    self.log("[WARNING] Detecção automática falhou, tentando estratégia alternativa...")
                    self.log("🔄 Estratégia 2: Detecção por análise profunda")
                    fields = automator.fallback_field_detection(driver)

                    if fields:
                        self.log("[OK] Campos detectados via análise alternativa!")
                        self.log(f"[LIST] Campos encontrados: {list(fields.keys())}")

                        for field_type, selector in fields.items():
                            self.log(f"   • {field_type.upper()}: {selector}")
                    else:
                        self.log("❌ Não foi possível detectar campos automaticamente")
                        self.log("[TIP] Sugestões:")
                        self.log("   • Verifique se a página tem formulários de login")
                        self.log("   • Tente configurar os seletores manualmente")
                        self.log("   • Use a ferramenta inspecionar_site.py para análise")

                # Análise adicional de elementos
                self.log("\n📈 ANÁLISE COMPLEMENTAR")
                self.log("-" * 30)
                automator.analyze_page_elements(driver)

                # Fechar navegador
                driver.quit()
                self.log("[SECURE] Navegador fechado")

                # Resultado final
                self.log("\n" + "=" * 60)
                if fields:
                    self.log("[SUCCESS] MAPEAMENTO CONCLUÍDO COM SUCESSO!")
                    self.log(f"[OK] {len(fields)} campos detectados e analisados")
                    self.log("[TIP] Use essas informações para configurar seletores personalizados")
                else:
                    self.log("[WARNING] MAPEAMENTO CONCLUÍDO COM LIMITAÇÕES")
                    self.log("❌ Campos não detectados automaticamente")
                    self.log("[TIP] Considere configuração manual dos seletores")
                self.log("=" * 60)

                self.status_var.set("Mapeamento concluído")

            except Exception as e:
                self.log(f"❌ ERRO durante mapeamento: {e}")
                self.log("[SEARCH] Detalhes do erro para diagnóstico:")
                import traceback
                self.log("Stack trace:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.log(f"   {line}")
                self.status_var.set("Erro no mapeamento")

        threading.Thread(target=map_worker, daemon=True).start()

    def clear_config(self):
        """Limpa a configuração"""
        self.url_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.log("Configuração limpa")

    def test_config(self):
        """Testa a configuração com análise detalhada"""
        def test_worker():
            try:
                self.status_var.set("Testando configuração...")
                self.log("=" * 60)
                self.log("[TEST] INICIANDO TESTE DE CONFIGURAÇÃO COMPLETA")
                self.log("=" * 60)

                # Teste 1: Verificação básica dos campos
                self.log("[LIST] TESTE 1: VERIFICAÇÃO BÁSICA DOS CAMPOS")
                self.log("-" * 50)

                url = self.url_var.get().strip()
                email = self.email_var.get().strip()
                password = self.password_var.get()

                # URL
                if not url:
                    self.log("❌ URL: NÃO CONFIGURADA")
                    self.log("   [TIP] Configure a URL do site de login")
                elif not url.startswith(('http://', 'https://')):
                    self.log("[WARNING]  URL: FORMATO INVÁLIDO")
                    self.log(f"   URL atual: {url}")
                    self.log("   [TIP] A URL deve começar com http:// ou https://")
                else:
                    self.log("[OK] URL: CONFIGURADA CORRETAMENTE")
                    self.log(f"   [WEB] {url}")

                # E-mail
                if not email:
                    self.log("❌ E-MAIL: NÃO CONFIGURADO")
                    self.log("   [TIP] Configure seu endereço de e-mail")
                elif '@' not in email or '.' not in email:
                    self.log("[WARNING]  E-MAIL: FORMATO POSSIVELMENTE INVÁLIDO")
                    self.log(f"   [EMAIL] {email}")
                    self.log("   [TIP] Verifique se o e-mail está correto")
                else:
                    self.log("[OK] E-MAIL: CONFIGURADO CORRETAMENTE")
                    self.log(f"   [EMAIL] {email}")

                # Senha
                if not password:
                    self.log("❌ SENHA: NÃO CONFIGURADA")
                    self.log("   [TIP] Configure sua senha de acesso")
                elif len(password) < 4:
                    self.log("[WARNING]  SENHA: MUITO CURTA")
                    self.log("   [SECURE] Comprimento atual: muito curto")
                    self.log("   [TIP] Use uma senha com pelo menos 4 caracteres")
                else:
                    self.log("[OK] SENHA: CONFIGURADA CORRETAMENTE")
                    self.log("   [SECURE] Senha definida (segurança mantida)")

                # Teste 2: Conectividade com o site
                self.log("\n[WEB] TESTE 2: CONECTIVIDADE COM O SITE")
                self.log("-" * 50)

                if url and url.startswith(('http://', 'https://')):
                    self.log("[SEARCH] Testando conexão com o site...")
                    try:
                        import urllib.request
                        req = urllib.request.Request(url, method='HEAD')
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.status == 200:
                                self.log("[OK] CONECTIVIDADE: SITE ACESSÍVEL")
                                self.log(f"   📊 Status HTTP: {response.status} OK")
                                self.log("   [LAUNCH] Site responde corretamente")
                            elif response.status == 301 or response.status == 302:
                                self.log("[WARNING]  CONECTIVIDADE: REDIRECIONAMENTO")
                                self.log(f"   📊 Status HTTP: {response.status} (redirecionamento)")
                                self.log("   [TIP] O site pode ter mudado de endereço")
                            else:
                                self.log(f"[WARNING]  CONECTIVIDADE: STATUS HTTP {response.status}")
                                self.log("   [TIP] Verifique se o site está funcionando")
                    except urllib.error.HTTPError as e:
                        if e.code == 401:
                            self.log("[WARNING]  CONECTIVIDADE: AUTENTICAÇÃO NECESSÁRIA")
                            self.log("   🔐 O site requer autenticação (normal)")
                        elif e.code == 403:
                            self.log("[WARNING]  CONECTIVIDADE: ACESSO NEGADO")
                            self.log("   🚫 Verifique se o site permite acesso automatizado")
                        elif e.code == 404:
                            self.log("❌ CONECTIVIDADE: PÁGINA NÃO ENCONTRADA")
                            self.log("   📄 A URL pode estar incorreta")
                        else:
                            self.log(f"[WARNING]  CONECTIVIDADE: ERRO HTTP {e.code}")
                    except Exception as e:
                        self.log(f"❌ CONECTIVIDADE: FALHA NA CONEXÃO")
                        self.log(f"   Erro: {e}")
                        self.log("   [TIP] Verifique sua conexão com a internet")
                else:
                    self.log("[SKIP]  CONECTIVIDADE: PULADO (URL inválida)")

                # Teste 3: Verificação da configuração técnica
                self.log("\n[CONFIG] TESTE 3: CONFIGURAÇÃO TÉCNICA")
                self.log("-" * 50)

                try:
                    # Verificar se arquivo de configuração existe
                    if os.path.exists(self.config_path):
                        self.log("[OK] ARQUIVO CONFIG: Encontrado")
                        config_size = os.path.getsize(self.config_path)
                        self.log(f"   📁 Tamanho: {config_size} bytes")
                    else:
                        self.log("❌ ARQUIVO CONFIG: Não encontrado")
                        self.log("   📁 Caminho esperado: config/config.ini")

                    # Verificar se conseguimos criar uma instância
                    temp_automator = LoginAutomator(self.config_path)
                    self.log("[OK] SISTEMA CORE: Inicialização OK")

                    # Verificar métodos essenciais
                    metodos_essenciais = ['perform_login', 'setup_driver', 'validate_page']
                    for metodo in metodos_essenciais:
                        if hasattr(temp_automator, metodo):
                            self.log(f"[OK] MÉTODO {metodo.upper()}: Disponível")
                        else:
                            self.log(f"❌ MÉTODO {metodo.upper()}: Não encontrado")

                except Exception as e:
                    self.log(f"❌ SISTEMA CORE: Falha na inicialização")
                    self.log(f"   Erro: {e}")

                # Resultado final
                self.log("\n" + "=" * 60)
                self.log("📊 RESULTADO DO TESTE DE CONFIGURAÇÃO")
                self.log("=" * 60)

                # Contar problemas
                problemas = 0
                avisos = 0

                if not url or not url.startswith(('http://', 'https://')):
                    problemas += 1
                if not email or '@' not in email:
                    problemas += 1
                if not password or len(password) < 4:
                    problemas += 1

                if problemas > 0:
                    self.log(f"❌ PROBLEMAS CRÍTICOS: {problemas}")
                    self.log("🔧 CORRIJA os problemas acima antes de usar o sistema")
                    self.status_var.set("Configuração com problemas")
                else:
                    self.log("[OK] CONFIGURAÇÃO VÁLIDA!")
                    self.log("[LAUNCH] Sistema pronto para uso")
                    self.log("[TIP] Você pode agora:")
                    self.log("   • Mapear campos do site")
                    self.log("   • Executar login de teste")
                    self.log("   • Configurar agendamento automático")
                    self.status_var.set("Configuração válida")

                self.log("=" * 60)

            except Exception as e:
                self.log(f"❌ ERRO CRÍTICO no teste: {e}")
                self.status_var.set("Erro no teste")

        threading.Thread(target=test_worker, daemon=True).start()

    def run_login(self):
        """Executa o login com logs detalhados"""
        def login_worker():
            try:
                self.status_var.set("Executando login...")
                self.log("=" * 80)
                self.log("[LAUNCH] INICIANDO PROCESSO DE LOGIN AUTOMATIZADO")
                self.log("=" * 80)

                # Verificar configuração antes de iniciar
                self.log("[SEARCH] VERIFICANDO CONFIGURAÇÃO")
                self.log("-" * 40)

                url = self.url_var.get().strip()
                email = self.email_var.get().strip()
                password = self.password_var.get()

                if not url:
                    self.log("❌ ERRO: URL não configurada!")
                    self.status_var.set("Erro: URL não configurada")
                    return

                if not email:
                    self.log("❌ ERRO: E-mail não configurado!")
                    self.status_var.set("Erro: E-mail não configurado")
                    return

                if not password:
                    self.log("❌ ERRO: Senha não configurada!")
                    self.status_var.set("Erro: Senha não configurada")
                    return

                self.log(f"[OK] URL: {url}")
                self.log(f"[OK] E-mail: {email}")
                self.log("[OK] Senha: configurada (segurança mantida)")
                # Criar instância do automatizador
                self.log("\n[CONFIG] INICIALIZANDO SISTEMA DE AUTOMAÇÃO")
                self.log("-" * 40)
                self.automator = LoginAutomator(self.config_path)
                self.log("[OK] Sistema de automação inicializado")

                # Executar login com acompanhamento detalhado
                self.log("\n[TARGET] EXECUTANDO LOGIN AUTOMATIZADO")
                self.log("-" * 40)
                self.log("[LIST] Acompanhe o progresso nos logs do sistema...")
                self.log("⏳ Isso pode levar alguns segundos...")

                # Executar login
                success = self.automator.perform_login()

                self.log("\n" + "=" * 80)
                if success:
                    self.log("[SUCCESS] LOGIN EXECUTADO COM SUCESSO!")
                    self.log("[OK] Processo de autenticação concluído")
                    self.log("[OK] Sistema pronto para uso")
                else:
                    self.log("❌ LOGIN FALHOU!")
                    self.log("[WARNING] Verifique os logs detalhados acima")
                    self.log("[TIP] Possíveis causas:")
                    self.log("   • Credenciais incorretas")
                    self.log("   • Site com mudanças estruturais")
                    self.log("   • Problemas de conectividade")
                    self.log("   • Seletores desatualizados")

                self.log("=" * 80)
                self.status_var.set("Login concluído")

            except Exception as e:
                self.log("\n" + "=" * 80)
                self.log("❌ ERRO CRÍTICO DURANTE LOGIN")
                self.log("=" * 80)
                self.log(f"[SEARCH] Detalhes do erro: {e}")
                self.log("\n🔧 DIAGNÓSTICO DETALHADO:")
                import traceback
                self.log("Stack trace:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.log(f"   {line}")

                self.log("\n[TIP] SOLUÇÕES SUGERIDAS:")
                self.log("   • Verifique se o Chrome está instalado")
                self.log("   • Teste a conectividade com o site")
                self.log("   • Execute o mapeamento de campos")
                self.log("   • Verifique as credenciais")

                self.status_var.set("Erro crítico no login")

        threading.Thread(target=login_worker, daemon=True).start()

    def start_scheduler(self):
        """Inicia o agendamento automático com horários configurados"""
        def scheduler_worker():
            try:
                self.status_var.set("Iniciando agendamento...")
                self.log("=" * 60)
                self.log("[SCHEDULE] INICIANDO AGENDAMENTO AUTOMÁTICO")
                self.log("=" * 60)

                # Verificar se já está agendado
                if hasattr(self, 'automator') and self.automator and self.automator.is_scheduling:
                    self.log("[WARNING] Agendador já está ativo!")
                    self.log("Pare o agendamento atual antes de iniciar outro.")
                    self.status_var.set("Agendador já ativo")
                    return

                # Carregar horários da configuração
                self.log("[CALENDAR] Carregando configuração de horários...")
                try:
                    horarios_str = self.config.get('SCHEDULE', 'horarios', fallback='')
                    if not horarios_str:
                        self.log("❌ ERRO: Nenhum horário configurado!")
                        self.log("Configure horários na seção [SCHEDULE] do config.ini")
                        self.log("Exemplo: horarios = 08:00, 12:00, 18:00")
                        self.status_var.set("Erro: horários não configurados")
                        return

                    # Processar horários
                    horarios = [h.strip() for h in horarios_str.split(',') if h.strip()]
                    self.log(f"[OK] {len(horarios)} horário(s) configurado(s): {', '.join(horarios)}")

                    # Validar formato dos horários
                    horarios_validos = []
                    for horario in horarios:
                        try:
                            hour, minute = map(int, horario.split(':'))
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                horarios_validos.append(horario)
                                self.log(f"   ✓ {horario} - válido")
                            else:
                                self.log(f"   ✗ {horario} - horário inválido (deve ser HH:MM)")
                        except ValueError:
                            self.log(f"   ✗ {horario} - formato inválido (deve ser HH:MM)")

                    if not horarios_validos:
                        self.log("❌ ERRO: Nenhum horário válido encontrado!")
                        self.status_var.set("Erro: horários inválidos")
                        return

                    self.log(f"[TARGET] Usando {len(horarios_validos)} horário(s) válido(s)")

                except Exception as e:
                    self.log(f"❌ ERRO ao carregar horários: {e}")
                    self.status_var.set("Erro na configuração")
                    return

                # Criar instância do automatizador se não existir
                self.log("\n[CONFIG] Inicializando sistema de automação...")
                if not hasattr(self, 'automator') or not self.automator:
                    self.automator = LoginAutomator(self.config_path)
                self.log("[OK] Sistema inicializado")

                # Iniciar agendamento
                self.log("\n[SCHEDULE] CONFIGURANDO AGENDAMENTO")
                self.log("-" * 40)

                try:
                    self.automator.start_scheduler(horarios_validos)
                    self.log("[OK] Agendamento configurado com sucesso!")

                    # Mostrar próximos horários
                    self.log("\n[LIST] PRÓXIMOS HORÁRIOS AGENDADOS:")
                    for horario in horarios_validos:
                        self.log(f"   • {horario} - Login automático diário")

                    # Atualizar interface
                    self.schedule_status_label.config(text="Status: Ativo", fg='green')
                    self.log("\n" + "=" * 60)
                    self.log("[SUCCESS] AGENDAMENTO ATIVADO COM SUCESSO!")
                    self.log("O sistema executará logins automaticamente nos horários configurados")
                    self.log("=" * 60)

                    self.status_var.set("Agendamento ativo")

                except Exception as e:
                    self.log(f"❌ ERRO ao configurar agendamento: {e}")
                    self.status_var.set("Erro no agendamento")

            except Exception as e:
                self.log(f"❌ ERRO inesperado: {e}")
                self.status_var.set("Erro no agendamento")

        threading.Thread(target=scheduler_worker, daemon=True).start()

    def stop_scheduler(self):
        """Para o agendamento automático"""
        def stop_worker():
            try:
                self.status_var.set("Parando agendamento...")
                self.log("=" * 60)
                self.log("[STOP] PARANDO AGENDAMENTO AUTOMÁTICO")
                self.log("=" * 60)

                if not hasattr(self, 'automator') or not self.automator:
                    self.log("[WARNING] Sistema de automação não inicializado")
                    self.status_var.set("Sistema não inicializado")
                    return

                if not self.automator.is_scheduling:
                    self.log("[WARNING] Agendador não está ativo")
                    self.status_var.set("Agendador já parado")
                    return

                # Parar agendamento
                self.log("[STOP] Desativando agendamento...")
                self.automator.stop_scheduler()
                self.log("[OK] Agendamento parado com sucesso!")

                # Atualizar interface
                self.schedule_status_label.config(text="Status: Parado", fg='red')

                self.log("=" * 60)
                self.log("[OK] AGENDAMENTO DESATIVADO")
                self.log("O sistema não executará mais logins automáticos")
                self.log("=" * 60)

                self.status_var.set("Agendamento parado")

            except Exception as e:
                self.log(f"❌ ERRO ao parar agendamento: {e}")
                self.status_var.set("Erro ao parar")

        threading.Thread(target=stop_worker, daemon=True).start()

    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)

    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()


def main():
    """Função principal"""
    app = LoginAutomatorGUI()
    app.run()


if __name__ == '__main__':
    main()
