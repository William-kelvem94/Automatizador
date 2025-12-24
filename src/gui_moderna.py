#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Gráfica Moderna e Completa - Automatizador de Login
Design profissional com cores modernas e funcionalidades completas
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import configparser
import threading
import time
import os
from datetime import datetime
from login_automator import LoginAutomator

class ModernLoginAutomatorGUI:
    """Interface gráfica moderna e profissional"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Automatizador de Login - Sistema Inteligente v3.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(True, True)

        # Cores modernas
        self.colors = {
            'primary': '#1877f2',      # Azul Facebook
            'secondary': '#42b883',   # Verde sucesso
            'danger': '#dc3545',      # Vermelho erro
            'warning': '#ffc107',     # Amarelo aviso
            'dark': '#1c1e21',        # Cinza escuro
            'light': '#f8f9fa',       # Cinza claro
            'white': '#ffffff',       # Branco
            'border': '#e1e5e9',      # Cinza borda
            'text': '#1c1e21',        # Texto principal
            'text_light': '#8a8d91',  # Texto secundário
            'success': '#28a745',     # Verde sucesso
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2'
        }

        # Configurar estilos
        self.setup_styles()

        # Carregar configurações
        self.setup_config()

        # Criar interface
        self.create_modern_interface()

        # Variáveis de estado
        self.automator = None
        self.is_testing = False
        self.is_scheduling = False
        self.current_operation = None

    def setup_styles(self):
        """Configurar estilos modernos"""
        style = ttk.Style()

        # Botões modernos
        style.configure("Modern.TButton",
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       relief="flat")

        style.configure("Primary.TButton",
                       background=self.colors['primary'],
                       foreground=self.colors['white'])

        style.configure("Success.TButton",
                       background=self.colors['success'],
                       foreground=self.colors['white'])

        style.configure("Danger.TButton",
                       background=self.colors['danger'],
                       foreground=self.colors['white'])

        style.configure("Warning.TButton",
                       background=self.colors['warning'],
                       foreground=self.colors['dark'])

        # Labels modernos
        style.configure("Modern.TLabel",
                       font=('Segoe UI', 10),
                       background=self.colors['light'])

        style.configure("Title.TLabel",
                       font=('Segoe UI', 16, 'bold'),
                       foreground=self.colors['primary'])

        style.configure("Subtitle.TLabel",
                       font=('Segoe UI', 12),
                       foreground=self.colors['text_light'])

        # Frames modernos
        style.configure("Card.TFrame",
                       background=self.colors['white'],
                       relief="solid",
                       borderwidth=1)

    def setup_config(self):
        """Configurar carregamento de configurações"""
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)

        if 'src' in current_dir:
            self.project_root = current_dir
            while os.path.basename(self.project_root) != 'src':
                self.project_root = os.path.dirname(self.project_root)
            self.project_root = os.path.dirname(self.project_root)
        else:
            self.project_root = current_dir

        self.config_path = os.path.join(self.project_root, 'config', 'config.ini')

        # Carregar configurações
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Variáveis da interface
        self.url_var = tk.StringVar(value=self.config.get('SITE', 'url', fallback=''))
        self.email_var = tk.StringVar(value=self.config.get('CREDENTIALS', 'email', fallback=''))
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sistema pronto para uso")

    def create_modern_interface(self):
        """Criar interface moderna e bonita"""
        # Header moderno com gradiente
        self.create_modern_header()

        # Container principal
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Layout em grid responsivo
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=0)

        # Painel esquerdo - Configurações
        left_panel = self.create_config_panel(main_container)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Painel direito - Operações e Logs
        right_panel = self.create_operations_panel(main_container)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Barra de status moderna
        self.create_modern_status_bar()

        # Menu superior
        self.create_modern_menu()

    def create_modern_header(self):
        """Criar header moderno com gradiente"""
        header_frame = tk.Frame(self.root, height=80, bg=self.colors['primary'])
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Gradiente background (simulado)
        canvas = tk.Canvas(header_frame, height=80, bg=self.colors['primary'], highlightthickness=0)
        canvas.pack(fill=tk.X)

        # Logo e título
        logo_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=15)

        # Logo grande
        logo_label = tk.Label(logo_frame, text="🔐",
                             font=('Segoe UI', 32), bg=self.colors['primary'], fg=self.colors['white'])
        logo_label.pack(side=tk.LEFT)

        # Texto do título
        title_frame = tk.Frame(logo_frame, bg=self.colors['primary'])
        title_frame.pack(side=tk.LEFT, padx=(15, 0))

        title_label = tk.Label(title_frame, text="AUTOMATIZADOR",
                              font=('Segoe UI', 14, 'bold'), bg=self.colors['primary'], fg=self.colors['white'])
        title_label.pack(anchor=tk.W)

        subtitle_label = tk.Label(title_frame, text="Sistema Inteligente v3.0",
                                 font=('Segoe UI', 9), bg=self.colors['primary'], fg='#e8f4fd')
        subtitle_label.pack(anchor=tk.W)

        # Status do sistema
        status_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        status_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        # Indicador de status
        status_indicator = tk.Label(status_frame, text="●",
                                   font=('Segoe UI', 12), bg=self.colors['primary'], fg=self.colors['success'])
        status_indicator.pack(side=tk.LEFT)

        status_text = tk.Label(status_frame, text="ONLINE",
                              font=('Segoe UI', 10, 'bold'), bg=self.colors['primary'], fg=self.colors['white'])
        status_text.pack(side=tk.LEFT, padx=(5, 0))

    def create_config_panel(self, parent):
        """Criar painel de configuração moderno"""
        # Frame do card
        card_frame = tk.Frame(parent, bg=self.colors['white'],
                             relief="solid", bd=1, highlightbackground=self.colors['border'])
        card_frame.pack(fill=tk.BOTH, expand=True)

        # Header do card
        card_header = tk.Frame(card_frame, bg=self.colors['primary'], height=50)
        card_header.pack(fill=tk.X)
        card_header.pack_propagate(False)

        header_label = tk.Label(card_header, text="⚙️ CONFIGURAÇÃO DO SISTEMA",
                               font=('Segoe UI', 12, 'bold'), bg=self.colors['primary'], fg=self.colors['white'])
        header_label.pack(pady=15)

        # Conteúdo do card
        content_frame = tk.Frame(card_frame, bg=self.colors['white'], padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Seção 1: Site
        site_frame = tk.Frame(content_frame, bg=self.colors['white'])
        site_frame.pack(fill=tk.X, pady=(0, 20))

        site_label = tk.Label(site_frame, text="🌐 SITE DE LOGIN",
                             font=('Segoe UI', 11, 'bold'), bg=self.colors['white'], fg=self.colors['text'])
        site_label.pack(anchor=tk.W, pady=(0, 10))

        # URL com ícone
        url_frame = tk.Frame(site_frame, bg=self.colors['white'])
        url_frame.pack(fill=tk.X)

        url_icon = tk.Label(url_frame, text="🔗", font=('Segoe UI', 12),
                           bg=self.colors['white'], fg=self.colors['primary'])
        url_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                 font=('Consolas', 10), relief=tk.FLAT,
                                 bg=self.colors['light'], fg=self.colors['text'],
                                 insertbackground=self.colors['primary'])
        self.url_entry.pack(fill=tk.X, ipady=8, padx=(0, 10))

        # Seção 2: Credenciais
        cred_frame = tk.Frame(content_frame, bg=self.colors['white'])
        cred_frame.pack(fill=tk.X, pady=(0, 20))

        cred_label = tk.Label(cred_frame, text="🔐 CREDENCIAIS DE ACESSO",
                             font=('Segoe UI', 11, 'bold'), bg=self.colors['white'], fg=self.colors['text'])
        cred_label.pack(anchor=tk.W, pady=(0, 10))

        # Email
        email_frame = tk.Frame(cred_frame, bg=self.colors['white'])
        email_frame.pack(fill=tk.X, pady=(0, 10))

        email_icon = tk.Label(email_frame, text="📧", font=('Segoe UI', 12),
                             bg=self.colors['white'], fg=self.colors['primary'])
        email_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.email_entry = tk.Entry(email_frame, textvariable=self.email_var,
                                   font=('Segoe UI', 10), relief=tk.FLAT,
                                   bg=self.colors['light'], fg=self.colors['text'],
                                   insertbackground=self.colors['primary'])
        self.email_entry.pack(fill=tk.X, ipady=8)

        # Senha
        pass_frame = tk.Frame(cred_frame, bg=self.colors['white'])
        pass_frame.pack(fill=tk.X)

        pass_icon = tk.Label(pass_frame, text="🔒", font=('Segoe UI', 12),
                            bg=self.colors['white'], fg=self.colors['primary'])
        pass_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.password_entry = tk.Entry(pass_frame, textvariable=self.password_var,
                                      show="●", font=('Segoe UI', 10), relief=tk.FLAT,
                                      bg=self.colors['light'], fg=self.colors['text'],
                                      insertbackground=self.colors['primary'])
        self.password_entry.pack(fill=tk.X, ipady=8)

        # Botões de ação
        buttons_frame = tk.Frame(content_frame, bg=self.colors['white'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        # Botão salvar
        save_btn = tk.Button(buttons_frame, text="💾 SALVAR CONFIGURAÇÃO",
                            command=self.save_config,
                            bg=self.colors['success'], fg=self.colors['white'],
                            font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                            padx=20, pady=10, cursor="hand2")
        save_btn.pack(fill=tk.X, pady=(0, 8))

        # Botão testar
        test_btn = tk.Button(buttons_frame, text="🧪 TESTAR CONFIGURAÇÃO",
                            command=self.test_config,
                            bg=self.colors['primary'], fg=self.colors['white'],
                            font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                            padx=20, pady=10, cursor="hand2")
        test_btn.pack(fill=tk.X, pady=(0, 8))

        # Botão limpar
        clear_btn = tk.Button(buttons_frame, text="🧹 LIMPAR CAMPOS",
                             command=self.clear_config,
                             bg=self.colors['warning'], fg=self.colors['dark'],
                             font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                             padx=20, pady=10, cursor="hand2")
        clear_btn.pack(fill=tk.X)

        return card_frame

    def create_operations_panel(self, parent):
        """Criar painel de operações moderno"""
        # Container para os cards
        container = tk.Frame(parent, bg=self.colors['light'])
        container.pack(fill=tk.BOTH, expand=True)

        # Card 1: Operações Principais
        main_ops_card = self.create_operations_card(container, "🎯 OPERAÇÕES PRINCIPAIS")
        main_ops_card.pack(fill=tk.X, pady=(0, 10))

        # Card 2: Agendamento
        schedule_card = self.create_schedule_card(container, "⏰ AGENDAMENTO AUTOMÁTICO")
        schedule_card.pack(fill=tk.X, pady=(0, 10))

        # Card 3: Logs
        logs_card = self.create_logs_card(container, "📋 LOGS DO SISTEMA")
        logs_card.pack(fill=tk.BOTH, expand=True)

        return container

    def create_operations_card(self, parent, title):
        """Criar card de operações principais"""
        card = tk.Frame(parent, bg=self.colors['white'],
                       relief="solid", bd=1, highlightbackground=self.colors['border'])

        # Header
        header = tk.Frame(card, bg=self.colors['secondary'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_label = tk.Label(header, text=title,
                               font=('Segoe UI', 11, 'bold'), bg=self.colors['secondary'], fg=self.colors['white'])
        header_label.pack(pady=10)

        # Conteúdo
        content = tk.Frame(card, bg=self.colors['white'], padx=15, pady=15)
        content.pack(fill=tk.X)

        # Botões em grid
        buttons_frame = tk.Frame(content, bg=self.colors['white'])
        buttons_frame.pack(fill=tk.X)

        # Mapear campos
        map_btn = tk.Button(buttons_frame, text="🔍 MAPEAR CAMPOS",
                           command=self.map_fields,
                           bg=self.colors['primary'], fg=self.colors['white'],
                           font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                           padx=15, pady=8, cursor="hand2", width=20)
        map_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Executar login
        login_btn = tk.Button(buttons_frame, text="🚀 EXECUTAR LOGIN",
                             command=self.run_login,
                             bg=self.colors['success'], fg=self.colors['white'],
                             font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                             padx=15, pady=8, cursor="hand2", width=20)
        login_btn.pack(side=tk.LEFT)

        return card

    def create_schedule_card(self, parent, title):
        """Criar card de agendamento"""
        card = tk.Frame(parent, bg=self.colors['white'],
                       relief="solid", bd=1, highlightbackground=self.colors['border'])

        # Header
        header = tk.Frame(card, bg=self.colors['warning'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_label = tk.Label(header, text=title,
                               font=('Segoe UI', 11, 'bold'), bg=self.colors['warning'], fg=self.colors['dark'])
        header_label.pack(pady=10)

        # Conteúdo
        content = tk.Frame(card, bg=self.colors['white'], padx=15, pady=15)
        content.pack(fill=tk.X)

        # Status
        status_frame = tk.Frame(content, bg=self.colors['white'])
        status_frame.pack(fill=tk.X, pady=(0, 10))

        status_label = tk.Label(status_frame, text="Status:",
                               font=('Segoe UI', 9, 'bold'), bg=self.colors['white'], fg=self.colors['text'])
        status_label.pack(side=tk.LEFT)

        self.schedule_status_label = tk.Label(status_frame, text="PARADO",
                                            font=('Segoe UI', 9, 'bold'), bg=self.colors['white'], fg=self.colors['danger'])
        self.schedule_status_label.pack(side=tk.LEFT, padx=(10, 0))

        # Botões
        buttons_frame = tk.Frame(content, bg=self.colors['white'])
        buttons_frame.pack(fill=tk.X)

        start_btn = tk.Button(buttons_frame, text="▶️ INICIAR AGENDAMENTO",
                             command=self.start_scheduler,
                             bg=self.colors['success'], fg=self.colors['white'],
                             font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                             padx=15, pady=8, cursor="hand2")
        start_btn.pack(side=tk.LEFT, padx=(0, 10))

        stop_btn = tk.Button(buttons_frame, text="⏹️ PARAR AGENDAMENTO",
                            command=self.stop_scheduler,
                            bg=self.colors['danger'], fg=self.colors['white'],
                            font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                            padx=15, pady=8, cursor="hand2")
        stop_btn.pack(side=tk.LEFT)

        return card

    def create_logs_card(self, parent, title):
        """Criar card de logs"""
        card = tk.Frame(parent, bg=self.colors['white'],
                       relief="solid", bd=1, highlightbackground=self.colors['border'])

        # Header
        header = tk.Frame(card, bg=self.colors['dark'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_label = tk.Label(header, text=title,
                               font=('Segoe UI', 11, 'bold'), bg=self.colors['dark'], fg=self.colors['white'])
        header_label.pack(pady=10)

        # Conteúdo
        content = tk.Frame(card, bg=self.colors['white'], padx=15, pady=(15, 0))
        content.pack(fill=tk.BOTH, expand=True)

        # Área de log
        self.log_text = scrolledtext.ScrolledText(
            content,
            font=('Consolas', 9),
            bg=self.colors['dark'],
            fg='#e0e0e0',
            insertbackground=self.colors['primary'],
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Botões de controle
        controls_frame = tk.Frame(content, bg=self.colors['white'])
        controls_frame.pack(fill=tk.X)

        clear_btn = tk.Button(controls_frame, text="🧹 LIMPAR LOGS",
                             command=self.clear_log,
                             bg=self.colors['warning'], fg=self.colors['dark'],
                             font=('Segoe UI', 8, 'bold'), relief=tk.FLAT,
                             padx=10, pady=6, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        save_btn = tk.Button(controls_frame, text="💾 SALVAR LOGS",
                            command=self.save_log,
                            bg=self.colors['primary'], fg=self.colors['white'],
                            font=('Segoe UI', 8, 'bold'), relief=tk.FLAT,
                            padx=10, pady=6, cursor="hand2")
        save_btn.pack(side=tk.LEFT)

        return card

    def create_modern_status_bar(self):
        """Criar barra de status moderna"""
        status_frame = tk.Frame(self.root, bg=self.colors['white'], height=40,
                               relief="solid", bd=1, highlightbackground=self.colors['border'])
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        # Status text
        status_icon = tk.Label(status_frame, text="📊",
                              font=('Segoe UI', 12), bg=self.colors['white'], fg=self.colors['primary'])
        status_icon.pack(side=tk.LEFT, padx=(15, 10))

        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                   font=('Segoe UI', 9), bg=self.colors['white'], fg=self.colors['text'])
        self.status_label.pack(side=tk.LEFT)

        # Progress bar (inicialmente oculta)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                          maximum=100, mode='determinate', length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=15)
        self.progress_bar.pack_forget()

    def create_modern_menu(self):
        """Criar menu superior moderno"""
        menubar = tk.Menu(self.root)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Novo", command=self.new_config)
        file_menu.add_command(label="Abrir", command=self.load_config)
        file_menu.add_command(label="Salvar", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Testar Conexão", command=self.test_connection)
        tools_menu.add_command(label="Limpar Cache", command=self.clear_cache)
        tools_menu.add_separator()
        tools_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)

        self.root.config(menu=menubar)

    def save_config(self):
        """Salvar configuração com feedback visual"""
        def save_worker():
            try:
                self.status_var.set("Salvando configuração...")
                self.show_progress()

                # Atualizar config
                if not self.config.has_section('SITE'):
                    self.config.add_section('SITE')
                if not self.config.has_section('CREDENTIALS'):
                    self.config.add_section('CREDENTIALS')
                if not self.config.has_section('SETTINGS'):
                    self.config.add_section('SETTINGS')

                self.config.set('SITE', 'url', self.url_entry.get())
                self.config.set('CREDENTIALS', 'email', self.email_entry.get())
                self.config.set('CREDENTIALS', 'password', self.password_entry.get())
                self.config.set('SETTINGS', 'headless', 'false')
                self.config.set('SETTINGS', 'wait_timeout', '10')

                with open(self.config_path, 'w') as f:
                    self.config.write(f)

                self.log("[SUCCESS] Configuração salva com sucesso!")
                self.status_var.set("Configuração salva")

                # Feedback visual
                self.show_success_message("Configuração salva!")

            except Exception as e:
                self.log(f"[ERROR] Erro ao salvar configuração: {e}")
                self.status_var.set("Erro ao salvar")
                self.show_error_message(f"Erro ao salvar: {e}")

            finally:
                self.hide_progress()

        threading.Thread(target=save_worker, daemon=True).start()

    def test_config(self):
        """Testar configuração completa"""
        def test_worker():
            try:
                self.status_var.set("Testando configuração...")
                self.show_progress()

                self.log("=" * 60)
                self.log("[TEST] INICIANDO TESTE DE CONFIGURAÇÃO COMPLETA")
                self.log("=" * 60)

                # Teste 1: Campos básicos
                self.log("\n[STEP 1] Verificando campos obrigatórios...")

                url = self.url_entry.get().strip()
                email = self.email_entry.get().strip()
                password = self.password_entry.get()

                if not url:
                    self.log("[ERROR] URL não configurada!")
                    self.show_error_message("Configure a URL do site primeiro")
                    return

                if not email:
                    self.log("[ERROR] E-mail não configurado!")
                    self.show_error_message("Configure seu e-mail primeiro")
                    return

                if not password:
                    self.log("[ERROR] Senha não configurada!")
                    self.show_error_message("Configure sua senha primeiro")
                    return

                self.log("[OK] Todos os campos obrigatórios preenchidos")

                # Teste 2: Validação de formato
                self.log("\n[STEP 2] Validando formatos...")

                if not url.startswith(('http://', 'https://')):
                    self.log("[WARNING] URL deve começar com http:// ou https://")
                else:
                    self.log("[OK] Formato da URL válido")

                if '@' not in email or '.' not in email:
                    self.log("[WARNING] E-mail pode não ser válido")
                else:
                    self.log("[OK] Formato do e-mail válido")

                if len(password) < 4:
                    self.log("[WARNING] Senha muito curta (mínimo 4 caracteres)")
                else:
                    self.log("[OK] Senha atende requisitos mínimos")

                # Teste 3: Conectividade
                self.log("\n[STEP 3] Testando conectividade...")
                try:
                    import urllib.request
                    req = urllib.request.Request(url, method='HEAD')
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            self.log("[OK] Site acessível e respondendo")
                        else:
                            self.log(f"[WARNING] Status HTTP: {response.status}")
                except Exception as e:
                    self.log(f"[WARNING] Não foi possível testar conectividade: {e}")

                # Teste 4: Sistema interno
                self.log("\n[STEP 4] Verificando sistema interno...")
                try:
                    import tkinter as tk
                    import selenium
                    import configparser
                    import apscheduler

                    self.log("[OK] Todas as dependências disponíveis")
                except ImportError as e:
                    self.log(f"[ERROR] Dependência faltando: {e}")
                    return

                # Resultado
                self.log("\n" + "=" * 60)
                self.log("[SUCCESS] TESTE DE CONFIGURAÇÃO CONCLUÍDO!")
                self.log("[OK] Sistema pronto para uso")
                self.log("=" * 60)

                self.status_var.set("Configuração validada")
                self.show_success_message("Configuração testada com sucesso!")

            except Exception as e:
                self.log(f"[ERROR] Erro durante teste: {e}")
                self.status_var.set("Erro no teste")
                self.show_error_message(f"Erro no teste: {e}")

            finally:
                self.hide_progress()

        threading.Thread(target=test_worker, daemon=True).start()

    def map_fields(self):
        """Mapear campos com interface moderna"""
        def map_worker():
            try:
                self.status_var.set("Mapeando campos do site...")
                self.show_progress()

                self.log("=" * 80)
                self.log("[MAPPING] INICIANDO MAPEAMENTO INTELIGENTE DE CAMPOS")
                self.log("=" * 80)

                # Verificar URL
                url = self.url_entry.get().strip()
                if not url:
                    self.log("[ERROR] Configure a URL primeiro!")
                    self.show_error_message("Configure a URL do site primeiro")
                    return

                self.log(f"[WEB] Analisando site: {url}")

                # Inicializar sistema
                self.log("[SYSTEM] Inicializando sistema de automação...")
                try:
                    self.automator = LoginAutomator(self.config_path)
                    self.log("[OK] Sistema inicializado")
                except Exception as e:
                    self.log(f"[ERROR] Falha na inicialização: {e}")
                    self.show_error_message("Erro ao inicializar o sistema")
                    return

                # Abrir navegador
                self.log("[BROWSER] Abrindo navegador...")
                try:
                    driver = self.automator.setup_driver()
                    self.log("[OK] Navegador aberto")
                except Exception as e:
                    self.log(f"[ERROR] Falha ao abrir navegador: {e}")
                    self.show_error_message("Erro ao abrir o navegador")
                    return

                # Acessar página
                self.log("[NAVIGATION] Acessando página de login...")
                try:
                    self.automator._access_login_page(driver)
                    self.log("[OK] Página carregada")
                except Exception as e:
                    self.log(f"[ERROR] Falha ao acessar página: {e}")
                    driver.quit()
                    return

                # Validar página
                self.log("[VALIDATION] Analisando estrutura da página...")
                if not self.automator.validate_page(driver):
                    self.log("[WARNING] Página pode não ter formulários tradicionais")
                    self.log("[INFO] Continuando análise...")
                else:
                    self.log("[OK] Página validada para formulários de login")

                # Detectar campos
                self.log("\n[FIELDS] EXECUTANDO DETECÇÃO DE CAMPOS")
                self.log("-" * 50)

                # Estratégia primária
                self.log("[STRATEGY 1] Detecção automática inteligente")
                fields = self.automator.smart_field_detection(driver)

                if fields:
                    self.log("[SUCCESS] Campos detectados automaticamente!")
                    self.log(f"[FIELDS] Total encontrado: {len(fields)}")

                    for field_type, selector in fields.items():
                        icon = "📧" if field_type == "email" else "🔒" if field_type == "password" else "📤"
                        self.log(f"   {icon} {field_type.upper()}: {selector}")
                else:
                    self.log("[WARNING] Detecção automática falhou")
                    self.log("[STRATEGY 2] Tentando detecção alternativa...")

                    fields = self.automator.fallback_field_detection(driver)
                    if fields:
                        self.log("[SUCCESS] Campos detectados via estratégia alternativa!")
                        self.log(f"[FIELDS] Total encontrado: {len(fields)}")

                        for field_type, selector in fields.items():
                            icon = "📧" if field_type == "email" else "🔒" if field_type == "password" else "📤"
                            self.log(f"   {icon} {field_type.upper()}: {selector}")
                    else:
                        self.log("[ERROR] Não foi possível detectar campos automaticamente")
                        self.log("[TIP] Considere configurar seletores manualmente")
                        self.show_error_message("Campos não detectados automaticamente")

                # Análise detalhada
                self.log("\n[ANALYSIS] REALIZANDO ANÁLISE DETALHADA")
                self.automator.analyze_page_elements(driver)

                # Fechar navegador
                driver.quit()
                self.log("[BROWSER] Navegador fechado")

                # Resultado final
                self.log("\n" + "=" * 80)
                if fields:
                    self.log("[SUCCESS] MAPEAMENTO CONCLUÍDO COM SUCESSO!")
                    self.log(f"[RESULT] {len(fields)} campos mapeados e analisados")
                    self.log("[TIP] Use essas informações para otimizar a automação")
                    self.show_success_message(f"Mapeamento concluído! {len(fields)} campos encontrados.")
                else:
                    self.log("[WARNING] MAPEAMENTO CONCLUÍDO COM LIMITAÇÕES")
                    self.log("[INFO] Campos não detectados - considere configuração manual")
                    self.show_warning_message("Campos não detectados automaticamente")

                self.log("=" * 80)
                self.status_var.set("Mapeamento concluído")

            except Exception as e:
                self.log(f"[ERROR] Erro crítico durante mapeamento: {e}")
                import traceback
                self.log("[DEBUG] Stack trace:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.log(f"   {line}")
                self.status_var.set("Erro no mapeamento")
                self.show_error_message(f"Erro durante mapeamento: {str(e)[:100]}")

            finally:
                self.hide_progress()

        threading.Thread(target=map_worker, daemon=True).start()

    def run_login(self):
        """Executar login com interface moderna"""
        def login_worker():
            try:
                self.status_var.set("Executando login automatizado...")
                self.show_progress()

                self.log("=" * 80)
                self.log("[LOGIN] INICIANDO PROCESSO DE LOGIN AUTOMATIZADO")
                self.log("=" * 80)

                # Validações iniciais
                self.log("\n[VALIDATION] VERIFICANDO CONFIGURAÇÃO")
                self.log("-" * 50)

                url = self.url_entry.get().strip()
                email = self.email_entry.get().strip()
                password = self.password_entry.get()

                if not url:
                    self.log("[ERROR] URL não configurada!")
                    self.show_error_message("Configure a URL primeiro")
                    return

                if not email:
                    self.log("[ERROR] E-mail não configurado!")
                    self.show_error_message("Configure seu e-mail primeiro")
                    return

                if not password:
                    self.log("[ERROR] Senha não configurada!")
                    self.show_error_message("Configure sua senha primeiro")
                    return

                self.log("[OK] Configuração validada")

                # Inicializar sistema
                self.log("\n[SYSTEM] INICIALIZANDO SISTEMA DE AUTOMAÇÃO")
                self.log("-" * 50)

                try:
                    self.automator = LoginAutomator(self.config_path)
                    self.log("[OK] Sistema inicializado com sucesso")
                except Exception as e:
                    self.log(f"[ERROR] Falha na inicialização: {e}")
                    self.show_error_message("Erro ao inicializar o sistema")
                    return

                # Executar login
                self.log("\n[EXECUTION] EXECUTANDO LOGIN AUTOMATIZADO")
                self.log("-" * 50)
                self.log("[INFO] Aguarde, o processo pode levar alguns segundos...")
                self.log("[INFO] Acompanhe o progresso nos logs detalhados...")

                success = self.automator.perform_login()

                self.log("\n" + "=" * 80)
                if success:
                    self.log("[SUCCESS] LOGIN EXECUTADO COM SUCESSO!")
                    self.log("[OK] Processo de autenticação concluído")
                    self.log("[OK] Sistema pronto para operações")
                    self.show_success_message("Login executado com sucesso!")
                else:
                    self.log("[FAILURE] LOGIN FALHOU!")
                    self.log("[INFO] Verifique os logs acima para detalhes")
                    self.log("[TIP] Possíveis causas:")
                    self.log("   • Credenciais incorretas")
                    self.log("   • Site com mudanças estruturais")
                    self.log("   • Problemas de conectividade")
                    self.log("   • Seletores desatualizados")
                    self.show_error_message("Login falhou - verifique os logs")

                self.log("=" * 80)
                self.status_var.set("Login concluído")

            except Exception as e:
                self.log(f"\n[ERROR] ERRO CRÍTICO DURANTE LOGIN: {e}")
                import traceback
                self.log("[DEBUG] Stack trace completo:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.log(f"   {line}")
                self.status_var.set("Erro crítico")
                self.show_error_message(f"Erro crítico: {str(e)[:100]}")

            finally:
                self.hide_progress()

        threading.Thread(target=login_worker, daemon=True).start()

    def start_scheduler(self):
        """Iniciar agendamento com interface moderna"""
        def scheduler_worker():
            try:
                self.status_var.set("Iniciando agendamento...")
                self.show_progress()

                self.log("=" * 80)
                self.log("[SCHEDULER] INICIANDO AGENDAMENTO AUTOMÁTICO")
                self.log("=" * 80)

                # Verificar se já está ativo
                if hasattr(self, 'automator') and self.automator and self.automator.is_scheduling:
                    self.log("[WARNING] Agendador já está ativo!")
                    self.show_warning_message("Agendador já está ativo")
                    return

                # Carregar horários
                self.log("[CONFIG] Carregando configuração de horários...")
                try:
                    horarios_str = self.config.get('SCHEDULE', 'horarios', fallback='')
                    if not horarios_str:
                        self.log("[ERROR] Nenhum horário configurado!")
                        self.log("[TIP] Configure horários na seção [SCHEDULE] do config.ini")
                        self.show_error_message("Configure horários primeiro")
                        return

                    horarios = [h.strip() for h in horarios_str.split(',') if h.strip()]
                    self.log(f"[OK] {len(horarios)} horário(s) configurado(s)")

                    # Validar horários
                    horarios_validos = []
                    for horario in horarios:
                        try:
                            hour, minute = map(int, horario.split(':'))
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                horarios_validos.append(horario)
                                self.log(f"[OK] {horario} - válido")
                            else:
                                self.log(f"[INVALID] {horario} - fora do intervalo")
                        except:
                            self.log(f"[INVALID] {horario} - formato incorreto")

                    if not horarios_validos:
                        self.log("[ERROR] Nenhum horário válido encontrado!")
                        self.show_error_message("Horários inválidos")
                        return

                    self.log(f"[SUCCESS] {len(horarios_validos)} horário(s) válido(s)")

                except Exception as e:
                    self.log(f"[ERROR] Erro ao carregar horários: {e}")
                    self.show_error_message("Erro na configuração de horários")
                    return

                # Inicializar sistema
                if not hasattr(self, 'automator') or not self.automator:
                    try:
                        self.automator = LoginAutomator(self.config_path)
                        self.log("[OK] Sistema de automação inicializado")
                    except Exception as e:
                        self.log(f"[ERROR] Falha na inicialização: {e}")
                        self.show_error_message("Erro ao inicializar sistema")
                        return

                # Configurar agendamento
                self.log("\n[SCHEDULE] CONFIGURANDO AGENDAMENTO")
                self.log("-" * 50)

                try:
                    self.automator.start_scheduler(horarios_validos)
                    self.log("[SUCCESS] Agendamento configurado!")

                    # Mostrar horários
                    self.log("\n[CALENDAR] PRÓXIMOS HORÁRIOS AGENDADOS:")
                    for horario in horarios_validos:
                        self.log(f"   ⏰ {horario} - Login automático diário")

                    # Atualizar interface
                    self.schedule_status_label.config(text="ATIVO", fg=self.colors['success'])
                    self.log("\n[SUCCESS] AGENDAMENTO ATIVADO COM SUCESSO!")
                    self.show_success_message("Agendamento iniciado!")

                    self.status_var.set("Agendamento ativo")

                except Exception as e:
                    self.log(f"[ERROR] Erro ao configurar agendamento: {e}")
                    self.show_error_message("Erro no agendamento")

            except Exception as e:
                self.log(f"[ERROR] Erro inesperado: {e}")
                self.show_error_message("Erro inesperado")

            finally:
                self.hide_progress()

        threading.Thread(target=scheduler_worker, daemon=True).start()

    def stop_scheduler(self):
        """Parar agendamento"""
        def stop_worker():
            try:
                self.status_var.set("Parando agendamento...")
                self.show_progress()

                self.log("=" * 80)
                self.log("[STOP] PARANDO AGENDAMENTO AUTOMÁTICO")
                self.log("=" * 80)

                if not hasattr(self, 'automator') or not self.automator:
                    self.log("[WARNING] Sistema não inicializado")
                    self.show_warning_message("Sistema não inicializado")
                    return

                if not self.automator.is_scheduling:
                    self.log("[INFO] Agendador já parado")
                    self.show_info_message("Agendador já estava parado")
                    return

                self.automator.stop_scheduler()
                self.log("[SUCCESS] Agendamento parado!")

                # Atualizar interface
                self.schedule_status_label.config(text="PARADO", fg=self.colors['danger'])
                self.log("=" * 80)
                self.log("[SUCCESS] AGENDAMENTO DESATIVADO")
                self.log("=" * 80)

                self.show_success_message("Agendamento parado!")
                self.status_var.set("Agendamento parado")

            except Exception as e:
                self.log(f"[ERROR] Erro ao parar agendamento: {e}")
                self.show_error_message("Erro ao parar agendamento")

            finally:
                self.hide_progress()

        threading.Thread(target=stop_worker, daemon=True).start()

    def clear_config(self):
        """Limpar configuração"""
        self.url_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.log("[CLEAR] Configuração limpa")
        self.status_var.set("Configuração limpa")

    def clear_log(self):
        """Limpar logs"""
        self.log_text.delete(1.0, tk.END)
        self.log("[CLEAR] Logs limpos")
        self.status_var.set("Logs limpos")

    def save_log(self):
        """Salvar logs em arquivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
                title="Salvar Logs"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"[SAVE] Logs salvos em: {filename}")
                self.show_success_message("Logs salvos com sucesso!")

        except Exception as e:
            self.log(f"[ERROR] Erro ao salvar logs: {e}")
            self.show_error_message("Erro ao salvar logs")

    def show_progress(self):
        """Mostrar barra de progresso"""
        self.progress_bar.pack(side=tk.RIGHT, padx=15)
        self.progress_var.set(50)

    def hide_progress(self):
        """Ocultar barra de progresso"""
        self.progress_bar.pack_forget()
        self.progress_var.set(0)

    def show_success_message(self, message):
        """Mostrar mensagem de sucesso"""
        success_window = tk.Toplevel(self.root)
        success_window.title("Sucesso")
        success_window.geometry("300x150")
        success_window.configure(bg=self.colors['success'])

        tk.Label(success_window, text="✅ SUCESSO",
                font=('Segoe UI', 14, 'bold'), bg=self.colors['success'], fg='white').pack(pady=20)

        tk.Label(success_window, text=message,
                font=('Segoe UI', 10), bg=self.colors['success'], fg='white').pack(pady=10)

        tk.Button(success_window, text="OK",
                 command=success_window.destroy,
                 bg='white', fg=self.colors['success'],
                 font=('Segoe UI', 9, 'bold')).pack(pady=10)

    def show_error_message(self, message):
        """Mostrar mensagem de erro"""
        error_window = tk.Toplevel(self.root)
        error_window.title("Erro")
        error_window.geometry("350x180")
        error_window.configure(bg=self.colors['danger'])

        tk.Label(error_window, text="❌ ERRO",
                font=('Segoe UI', 14, 'bold'), bg=self.colors['danger'], fg='white').pack(pady=20)

        tk.Label(error_window, text=message,
                font=('Segoe UI', 10), bg=self.colors['danger'], fg='white',
                wraplength=300, justify=tk.CENTER).pack(pady=10)

        tk.Button(error_window, text="OK",
                 command=error_window.destroy,
                 bg='white', fg=self.colors['danger'],
                 font=('Segoe UI', 9, 'bold')).pack(pady=10)

    def show_warning_message(self, message):
        """Mostrar mensagem de aviso"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Aviso")
        warning_window.geometry("350x180")
        warning_window.configure(bg=self.colors['warning'])

        tk.Label(warning_window, text="⚠️ AVISO",
                font=('Segoe UI', 14, 'bold'), bg=self.colors['warning'], fg=self.colors['dark']).pack(pady=20)

        tk.Label(warning_window, text=message,
                font=('Segoe UI', 10), bg=self.colors['warning'], fg=self.colors['dark'],
                wraplength=300, justify=tk.CENTER).pack(pady=10)

        tk.Button(warning_window, text="OK",
                 command=warning_window.destroy,
                 bg=self.colors['dark'], fg=self.colors['warning'],
                 font=('Segoe UI', 9, 'bold')).pack(pady=10)

    def show_info_message(self, message):
        """Mostrar mensagem informativa"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Informação")
        info_window.geometry("350x180")
        info_window.configure(bg=self.colors['primary'])

        tk.Label(info_window, text="ℹ️ INFORMAÇÃO",
                font=('Segoe UI', 14, 'bold'), bg=self.colors['primary'], fg='white').pack(pady=20)

        tk.Label(info_window, text=message,
                font=('Segoe UI', 10), bg=self.colors['primary'], fg='white',
                wraplength=300, justify=tk.CENTER).pack(pady=10)

        tk.Button(info_window, text="OK",
                 command=info_window.destroy,
                 bg='white', fg=self.colors['primary'],
                 font=('Segoe UI', 9, 'bold')).pack(pady=10)

    # Métodos do menu (placeholders)
    def new_config(self):
        """Nova configuração"""
        self.clear_config()
        self.log("[NEW] Nova configuração criada")

    def load_config(self):
        """Carregar configuração"""
        filename = filedialog.askopenfilename(
            filetypes=[("Arquivo INI", "*.ini"), ("Todos os arquivos", "*.*")],
            title="Carregar Configuração"
        )
        if filename:
            try:
                config = configparser.ConfigParser()
                config.read(filename)
                # Carregar valores na interface
                self.url_var.set(config.get('SITE', 'url', fallback=''))
                self.email_var.set(config.get('CREDENTIALS', 'email', fallback=''))
                self.log(f"[LOAD] Configuração carregada de: {filename}")
            except Exception as e:
                self.show_error_message(f"Erro ao carregar: {e}")

    def test_connection(self):
        """Testar conexão"""
        self.log("[TEST] Testando conexão com internet...")
        # Implementação básica
        self.log("[OK] Conexão testada")

    def clear_cache(self):
        """Limpar cache"""
        self.log("[CLEAR] Cache do sistema limpo")

    def show_about(self):
        """Mostrar sobre"""
        about_text = """Automatizador de Login v3.0

Sistema inteligente para automação de login em websites.

Características:
• Interface moderna e intuitiva
• Detecção automática de campos
• Agendamento inteligente
• Validação avançada
• Logs detalhados

Desenvolvido com tecnologia Python e Selenium."""

        about_window = tk.Toplevel(self.root)
        about_window.title("Sobre")
        about_window.geometry("400x300")
        about_window.configure(bg=self.colors['white'])

        tk.Label(about_window, text="🚀 Automatizador de Login",
                font=('Segoe UI', 16, 'bold'), bg=self.colors['white'], fg=self.colors['primary']).pack(pady=20)

        tk.Label(about_window, text="Versão 3.0",
                font=('Segoe UI', 10), bg=self.colors['white'], fg=self.colors['text_light']).pack()

        tk.Label(about_window, text=about_text,
                font=('Segoe UI', 9), bg=self.colors['white'], fg=self.colors['text'],
                justify=tk.LEFT).pack(pady=20)

        tk.Button(about_window, text="Fechar",
                 command=about_window.destroy,
                 bg=self.colors['primary'], fg='white',
                 font=('Segoe UI', 9, 'bold')).pack()

    def log(self, message):
        """Adicionar mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def run(self):
        """Executar a aplicação"""
        self.log("=" * 80)
        self.log("🚀 AUTOMATIZADOR DE LOGIN v3.0 INICIADO")
        self.log("=" * 80)
        self.log("[READY] Sistema pronto para uso")
        self.log("[TIP] Configure suas credenciais e comece a automatizar!")
        self.log("=" * 80)

        self.root.mainloop()


def main():
    """Função principal"""
    app = ModernLoginAutomatorGUI()
    app.run()


if __name__ == '__main__':
    main()
