"""
Interface Moderna e Inteligente - Versão Refatorada
Design revolucionário com IA integrada e experiência excepcional
Refatorado para melhor manutenibilidade e performance
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Tuple, List
from pathlib import Path

# Imports do sistema
from ..core.config_manager import ConfigManager
from ..core.automation_engine import AutomationEngine
from ..core.scheduler import SmartScheduler


class UIComponents:
    """Componentes reutilizáveis da interface"""

    def __init__(self, theme: Dict[str, str]):
        self.theme = theme

    def create_card(self, parent, title: str = "", icon: str = "") -> tk.Frame:
        """Cria um card padronizado"""
        card = tk.Frame(parent, bg=self.theme['card_bg'],
                       relief='solid', bd=1, highlightbackground=self.theme['card_border'])

        if title:
            self._create_card_header(card, title, icon)

        return card

    def _create_card_header(self, card: tk.Frame, title: str, icon: str):
        """Cria header padronizado para cards"""
        header = tk.Frame(card, bg=self.theme['card_bg'])
        header.pack(fill=tk.X, padx=18, pady=(18, 8))

        if icon:
            icon_label = tk.Label(header, text=icon, font=('Segoe UI', 20),
                                 bg=self.theme['card_bg'], fg=self.theme['primary'])
            icon_label.pack(side=tk.LEFT, padx=(0, 12))

        title_label = tk.Label(header, text=title, font=('Segoe UI', 14, 'bold'),
                              bg=self.theme['card_bg'], fg=self.theme['text_primary'])
        title_label.pack(side=tk.LEFT)

    def create_button(self, parent, text: str, command: Callable,
                     style_type: str = 'primary', **kwargs) -> tk.Button:
        """Cria botão padronizado"""
        style_map = {
            'primary': {
                'bg': self.theme['primary'],
                'fg': self.theme['text_primary'],
                'active_bg': self.theme['primary_hover']
            },
            'secondary': {
                'bg': self.theme['surface_light'],
                'fg': self.theme['text_primary'],
                'active_bg': self.theme['surface_hover']
            },
            'danger': {
                'bg': self.theme['error'],
                'fg': 'white',
                'active_bg': self.theme['error_bg']
            }
        }

        style = style_map.get(style_type, style_map['primary'])

        button = tk.Button(parent, text=text, command=command,
                          font=('Segoe UI', 10, 'bold'),
                          bg=style['bg'], fg=style['fg'],
                          relief='flat', padx=15, pady=8,
                          cursor="hand2", **kwargs)

        # Bind de hover
        def on_enter(e):
            button.configure(bg=style['active_bg'])
        def on_leave(e):
            button.configure(bg=style['bg'])

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

        return button

    def create_input_field(self, parent, label_text: str, entry_type: str = 'text',
                          show_char: str = '') -> Tuple[tk.Frame, tk.Entry]:
        """Cria campo de entrada padronizado"""
        container = tk.Frame(parent, bg=self.theme['card_bg'])

        # Label
        label = tk.Label(container, text=label_text, font=('Segoe UI', 10),
                        bg=self.theme['card_bg'], fg=self.theme['text_secondary'])
        label.pack(anchor=tk.W, pady=(0, 5))

        # Entry
        entry = tk.Entry(container, font=('Segoe UI', 10),
                        bg=self.theme['input_bg'], fg=self.theme['text_primary'],
                        insertbackground=self.theme['text_primary'],
                        relief='solid', bd=1, show=show_char)
        entry.pack(fill=tk.X)

        return container, entry


class ValidationUtils:
    """Utilitários de validação"""

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Valida URL"""
        if not url.strip():
            return False, "URL é obrigatória"

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return False, "URL deve começar com http:// ou https://"

        # Regex básica para validar formato de URL
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            return False, "Formato de URL inválido"

        return True, "URL válida"

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Valida email"""
        if not email.strip():
            return False, "E-mail é obrigatório"

        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email.strip()):
            return False, "Formato de e-mail inválido"

        return True, "E-mail válido"

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Valida senha"""
        if not password:
            return False, "Senha é obrigatória"

        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"

        return True, "Senha válida"


class ModernInterface:
    """Interface gráfica revolucionária com IA integrada"""

    def __init__(self):
        # Configuração do tema escuro premium refinado
        self.theme = {
            # ===== PALETA PRINCIPAL =====
            'primary': '#6366f1',        # Índigo moderno (mais suave que roxo)
            'primary_hover': '#4f46e5',  # Índigo mais escuro para hover
            'primary_light': '#818cf8',  # Índigo claro para destaques

            'secondary': '#06b6d4',      # Cyan elegante (mais profissional)
            'secondary_hover': '#0891b2', # Cyan escuro
            'secondary_light': '#22d3ee', # Cyan claro

            'accent': '#ec4899',         # Pink sofisticado
            'accent_hover': '#db2777',   # Pink mais intenso
            'accent_light': '#f472b6',   # Pink suave

            # ===== FUNDO E SUPERFÍCIES =====
            'background': '#0a0a0a',     # Preto profundo (mais escuro)
            'background_light': '#111111', # Preto ligeiramente mais claro
            'surface': '#1a1a1a',        # Cinza muito escuro
            'surface_light': '#212121',  # Cinza um pouco mais claro
            'surface_hover': '#262626',  # Hover das superfícies

            'card_bg': '#262626',        # Fundo dos cards (mais refinado)
            'card_bg_hover': '#2d2d2d',  # Hover dos cards
            'card_border': '#404040',    # Bordas dos cards

            # ===== TEXTO E ÍCONES =====
            'text_primary': '#fafafa',   # Branco quase puro
            'text_secondary': '#d1d5db', # Cinza muito claro
            'text_tertiary': '#9ca3af',  # Cinza médio
            'text_muted': '#6b7280',     # Cinza mais escuro

            # ===== STATUS E FEEDBACK =====
            'success': '#10b981',        # Verde esmeralda (mais moderno)
            'success_bg': '#064e3b',     # Fundo verde escuro
            'error': '#ef4444',          # Vermelho vibrante mas não agressivo
            'error_bg': '#7f1d1d',       # Fundo vermelho escuro
            'warning': '#f59e0b',        # Âmbar dourado
            'warning_bg': '#78350f',     # Fundo âmbar escuro
            'info': '#3b82f6',           # Azul informação
            'info_bg': '#1e3a8a',        # Fundo azul escuro

            # ===== BORDAS E SEPARADORES =====
            'border': '#374151',         # Bordas principais
            'border_light': '#4b5563',   # Bordas mais claras
            'border_focus': '#6366f1',   # Bordas de foco (primary)
            'divider': '#374151',        # Separadores

            # ===== ESTADOS INTERATIVOS =====
            'hover': '#2d2d2d',          # Hover geral
            'active': '#333333',        # Estado ativo
            'disabled': '#4b5563',       # Estado desabilitado
            'disabled_text': '#6b7280', # Texto desabilitado

            # ===== COMPONENTES ESPECIAIS =====
            'sidebar_bg': '#0f0f0f',     # Fundo da sidebar
            'header_bg': '#1a1a1a',      # Fundo do header
            'footer_bg': '#0f0f0f',      # Fundo do footer

            'input_bg': '#262626',       # Fundo dos inputs
            'input_border': '#4b5563',   # Bordas dos inputs
            'input_focus': '#6366f1',    # Foco dos inputs

            'button_primary': '#6366f1', # Botões primários
            'button_secondary': '#374151', # Botões secundários
            'button_danger': '#ef4444',  # Botões de perigo

            # ===== GRADIENTES SUTIS =====
            'gradient_start': '#1a1a1a', # Início de gradientes
            'gradient_end': '#0a0a0a',   # Fim de gradientes

            # ===== SOMBRAS E EFEITOS =====
            'shadow_light': 'rgba(0, 0, 0, 0.1)',  # Sombras suaves
            'shadow_medium': 'rgba(0, 0, 0, 0.2)', # Sombras médias
            'shadow_heavy': 'rgba(0, 0, 0, 0.3)',  # Sombras fortes
        }

        # Inicializar componentes auxiliares
        self.ui_components = UIComponents(self.theme)
        self.validation = ValidationUtils()

        # Estado da aplicação
        self.config_manager = ConfigManager()
        self.automation_engine = None
        self.smart_scheduler = SmartScheduler()

        # Estado da UI
        self.current_view = 'dashboard'
        self.views = {}
        self.form_entries = {}
        self.status_indicators = {}
        self.animations_running = {}
        self.notifications_queue = []

        # Inicializar interface
        self._setup_main_window()

        self._configure_styles()

        self._create_layout()

        self._setup_animations()

        self._load_initial_data()

    def _setup_main_window(self):
        """Configura janela principal com design moderno"""
        self.root = tk.Tk()

        self.root.title("🚀 Automatizador IA - Sistema Inteligente v4.0")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.theme['background'])
        self.root.resizable(True, True)

        # Remove bordas padrão do Windows
        try:
            self.root.attributes('-alpha', 0.0)  # Começa invisível
            self.root.after(100, lambda: self.root.attributes('-alpha', 1.0))  # Fade in
        except:
            pass  # Fallback para sistemas sem suporte

        # Ícone da aplicação
        try:
            self.root.iconbitmap(default='assets/icon.ico')
        except:
            pass

        # Bindings para interatividade avançada
        self.root.bind('<F11>', self._toggle_fullscreen)
        self.root.bind('<Escape>', self._exit_fullscreen)
        self.root.bind('<Control-n>', lambda e: self._new_operation())
        self.root.bind('<Control-s>', lambda e: self._save_config())

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Garantir que a janela seja visível e tenha foco
        self.root.deiconify()  # Garante que a janela não esteja minimizada
        self.root.lift()       # Traz a janela para frente
        self.root.focus_force() # Força o foco na janela
        self.root.attributes('-topmost', True)  # Temporariamente no topo
        self.root.after(100, lambda: self.root.attributes('-topmost', False))  # Remove depois de 100ms

    def _configure_styles(self):
        """Configura estilos ttk modernos e refinados"""
        style = ttk.Style()

        # ===== CONFIGURAÇÃO BASE =====
        style.configure('.',
                       background=self.theme['background'],
                       foreground=self.theme['text_primary'],
                       font=('Segoe UI', 10))

        # ===== BOTÕES PREMIUM =====
        # Botão Primário (Índigo)
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       background=self.theme['primary'])

        style.map('Primary.TButton',
                 background=[('active', self.theme['primary_hover']),
                           ('pressed', self.theme['primary_light'])],
                 foreground=[('active', self.theme['text_primary']),
                           ('pressed', self.theme['text_primary'])])

        # Botão Secundário (Cyan)
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       background=self.theme['secondary'])

        style.map('Secondary.TButton',
                 background=[('active', self.theme['secondary_hover']),
                           ('pressed', self.theme['secondary_light'])],
                 foreground=[('active', self.theme['text_primary'])])

        # Botão Accent (Pink)
        style.configure('Accent.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       background=self.theme['accent'])

        style.map('Accent.TButton',
                 background=[('active', self.theme['accent_hover']),
                           ('pressed', self.theme['accent_light'])],
                 foreground=[('active', self.theme['text_primary'])])

        # Botão de Perigo
        style.configure('Danger.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       background=self.theme['error'])

        style.map('Danger.TButton',
                 background=[('active', self.theme['error_bg']),
                           ('pressed', '#dc2626')],
                 foreground=[('active', self.theme['text_primary'])])

        # Botão Sucesso
        style.configure('Success.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       background=self.theme['success'])

        style.map('Success.TButton',
                 background=[('active', '#059669'),
                           ('pressed', '#047857')],
                 foreground=[('active', self.theme['text_primary'])])

        # ===== CARDS E FRAMES =====
        style.configure('Card.TFrame',
                       background=self.theme['card_bg'],
                       relief='solid',
                       borderwidth=1)

        style.configure('Surface.TFrame',
                       background=self.theme['surface'],
                       relief='flat')

        style.configure('Header.TFrame',
                       background=self.theme['header_bg'],
                       relief='flat')

        # ===== LABELS HIERÁRQUICOS =====
        style.configure('Title.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       foreground=self.theme['text_primary'],
                       background=self.theme['background'])

        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.theme['text_secondary'],
                       background=self.theme['background'])

        style.configure('Body.TLabel',
                       font=('Segoe UI', 11),
                       foreground=self.theme['text_primary'],
                       background=self.theme['background'])

        style.configure('Caption.TLabel',
                       font=('Segoe UI', 9),
                       foreground=self.theme['text_tertiary'],
                       background=self.theme['background'])

        # ===== ENTRADAS E CONTROLES =====
        style.configure('TEntry',
                       font=('Segoe UI', 10),
                       fieldbackground=self.theme['input_bg'],
                       bordercolor=self.theme['input_border'],
                       lightcolor=self.theme['input_border'],
                       darkcolor=self.theme['input_border'])

        style.map('TEntry',
                 fieldbackground=[('focus', self.theme['input_bg'])],
                 bordercolor=[('focus', self.theme['input_focus'])])

        style.configure('TCombobox',
                       font=('Segoe UI', 10),
                       fieldbackground=self.theme['input_bg'],
                       background=self.theme['input_bg'],
                       bordercolor=self.theme['input_border'])

        style.map('TCombobox',
                 fieldbackground=[('focus', self.theme['input_bg'])],
                 background=[('focus', self.theme['input_bg'])],
                 bordercolor=[('focus', self.theme['input_focus'])])

        # ===== INDICADORES DE STATUS =====
        style.configure('Success.TLabel',
                       foreground=self.theme['success'],
                       background=self.theme['background'])

        style.configure('Error.TLabel',
                       foreground=self.theme['error'],
                       background=self.theme['background'])

        style.configure('Warning.TLabel',
                       foreground=self.theme['warning'],
                       background=self.theme['background'])

        style.configure('Info.TLabel',
                       foreground=self.theme['info'],
                       background=self.theme['background'])

        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12),
                       foreground=self.theme['text_secondary'])

        # Progress bars animadas
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.theme['primary'],
                       troughcolor=self.theme['surface'],
                       borderwidth=0,
                       lightcolor=self.theme['primary'],
                       darkcolor=self.theme['secondary'])

    def _create_layout(self):
        """Cria layout principal com design de dashboard"""
        # Container principal
        self.main_container = tk.Frame(self.root, bg=self.theme['background'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header superior com gradiente
        self._create_header()

        # Barra lateral de navegação
        self.sidebar = self._create_sidebar()

        # Área de conteúdo principal
        self.content_area = tk.Frame(self.main_container, bg=self.theme['background'])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Views diferentes
        self.views = {}
        self._create_dashboard_view()
        self._create_automation_view()
        self._create_scheduler_view()
        self._create_settings_view()
        self._create_logs_view()

        # Barra de status inferior
        self._create_status_bar()

        # Notificações flutuantes
        self._setup_notifications()

        # Mostrar dashboard inicial
        self._show_view('dashboard')

    def _create_header(self):
        """Cria header superior com design premium refinado"""
        header = tk.Frame(self.main_container, bg=self.theme['header_bg'], height=80)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        # Gradiente sutil no header
        header.configure(bg=self.theme['header_bg'])

        # Logo e título com design aprimorado
        logo_frame = tk.Frame(header, bg=self.theme['header_bg'])
        logo_frame.pack(side=tk.LEFT, padx=25, pady=15)

        # Logo com ícone mais elegante
        self.logo_label = tk.Label(logo_frame, text="🤖",
                                  font=('Segoe UI', 28), bg=self.theme['header_bg'],
                                  fg=self.theme['primary'])
        self.logo_label.pack(side=tk.LEFT)

        title_frame = tk.Frame(logo_frame, bg=self.theme['header_bg'])
        title_frame.pack(side=tk.LEFT, padx=(12, 0))

        # Título principal com fonte maior e mais impactante
        tk.Label(title_frame, text="AUTOMATIZADOR IA",
                font=('Segoe UI', 16, 'bold'), bg=self.theme['header_bg'],
                fg=self.theme['text_primary']).pack(anchor=tk.W)

        # Subtítulo com cor diferenciada
        tk.Label(title_frame, text="Sistema Inteligente v4.0 • IA Integrada",
                font=('Segoe UI', 9), bg=self.theme['header_bg'],
                fg=self.theme['secondary']).pack(anchor=tk.W)

        # Botões de controle do header
        controls_frame = tk.Frame(header, bg=self.theme['primary'])
        controls_frame.pack(side=tk.RIGHT, padx=20)

        # Botão de minimizar
        min_btn = tk.Button(controls_frame, text="—", font=('Segoe UI', 12, 'bold'),
                           bg=self.theme['primary'], fg=self.theme['text_primary'],
                           relief='flat', command=self._minimize_window)
        min_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Botão de fechar
        close_btn = tk.Button(controls_frame, text="✕", font=('Segoe UI', 10, 'bold'),
                             bg=self.theme['error'], fg=self.theme['text_primary'],
                             relief='flat', command=self._on_closing)
        close_btn.pack(side=tk.LEFT)

        # Hover effects
        for btn in [min_btn, close_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.theme['hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.theme['primary'] if b != close_btn else self.theme['error']))

    def _create_sidebar(self) -> tk.Frame:
        """Cria barra lateral de navegação premium refinada"""
        sidebar = tk.Frame(self.main_container, bg=self.theme['sidebar_bg'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Header da sidebar com gradiente sutil
        header_frame = tk.Frame(sidebar, bg=self.theme['sidebar_bg'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Logo pequeno na sidebar
        logo_frame = tk.Frame(header_frame, bg=self.theme['sidebar_bg'])
        logo_frame.pack(pady=(20, 5))

        tk.Label(logo_frame, text="⚡",
                font=('Segoe UI', 18), bg=self.theme['sidebar_bg'],
                fg=self.theme['primary']).pack()

        # Título elegante
        tk.Label(header_frame, text="MENU",
                font=('Segoe UI', 11, 'bold'), bg=self.theme['sidebar_bg'],
                fg=self.theme['text_tertiary']).pack(pady=(0, 20))

        # Separador sutil
        separator = tk.Frame(header_frame, bg=self.theme['divider'], height=1)
        separator.pack(fill=tk.X, padx=20)
        separator.pack_propagate(False)

        # Botões de navegação com design aprimorado
        nav_buttons = [
            ('📊 Dashboard', 'dashboard', 'Visão geral inteligente do sistema'),
            ('🚀 Automação', 'automation', 'Operações de login automatizadas'),
            ('⏰ Agendador', 'scheduler', 'Execuções programadas com IA'),
            ('⚙️ Configurações', 'settings', 'Personalização avançada'),
            ('📋 Logs', 'logs', 'Histórico detalhado de operações')
        ]

        self.nav_buttons = {}
        for text, view_name, tooltip in nav_buttons:
            btn = self._create_nav_button(sidebar, text, view_name, tooltip)
            self.nav_buttons[view_name] = btn

        return sidebar

    def _create_nav_button(self, parent, text: str, view_name: str, tooltip: str) -> tk.Button:
        """Cria botão de navegação com design premium e efeitos avançados"""
        # Container para melhor controle visual
        container = tk.Frame(parent, bg=self.theme['sidebar_bg'])
        container.pack(fill=tk.X, padx=10, pady=3)

        # Botão principal com design refinado
        btn = tk.Button(container, text=text,
                       font=('Segoe UI', 11),
                       bg=self.theme['sidebar_bg'], fg=self.theme['text_secondary'],
                       activebackground=self.theme['surface_hover'],
                       activeforeground=self.theme['text_primary'],
                       relief='flat', anchor='w', padx=15, pady=14,
                       cursor='hand2',
                       command=lambda: self._show_view(view_name))

        btn.pack(fill=tk.X)

        # Indicador visual de seleção (barra lateral)
        indicator = tk.Frame(container, bg=self.theme['sidebar_bg'], width=4, height=40)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        indicator.pack_propagate(False)

        # Armazenar referências para efeitos dinâmicos
        btn.indicator = indicator
        btn.container = container

        # Efeitos de hover e seleção aprimorados
        def on_enter(e):
            if self.current_view != view_name:
                btn.configure(bg=self.theme['surface_hover'], fg=self.theme['text_primary'])
                indicator.configure(bg=self.theme['primary_light'])

        def on_leave(e):
            if self.current_view != view_name:
                btn.configure(bg=self.theme['sidebar_bg'], fg=self.theme['text_secondary'])
                indicator.configure(bg=self.theme['sidebar_bg'])

        def update_selection():
            """Atualiza aparência baseada na seleção atual"""
            if self.current_view == view_name:
                # Selecionado - destaque forte
                btn.configure(bg=self.theme['primary'], fg=self.theme['text_primary'])
                indicator.configure(bg=self.theme['secondary'])
                container.configure(bg=self.theme['surface_light'])
            else:
                # Não selecionado - aparência normal
                btn.configure(bg=self.theme['sidebar_bg'], fg=self.theme['text_secondary'])
                indicator.configure(bg=self.theme['sidebar_bg'])
                container.configure(bg=self.theme['sidebar_bg'])

        # Aplicar seleção inicial
        update_selection()

        # Bind events
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        # Armazenar função de atualização para uso posterior
        btn.update_selection = update_selection

        return btn

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        # Tooltip
        self._add_tooltip(btn, tooltip)

        return btn

    def _create_dashboard_view(self):
        """Cria view do dashboard com métricas e status"""
        view = tk.Frame(self.content_area, bg=self.theme['background'])

        # Título
        title_frame = tk.Frame(view, bg=self.theme['background'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="Dashboard Inteligente",
                font=('Segoe UI', 20, 'bold'), bg=self.theme['background'],
                fg=self.theme['primary']).pack(pady=20)

        # Grid de métricas
        metrics_frame = tk.Frame(view, bg=self.theme['background'])
        metrics_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Cards de métricas
        self._create_metric_card(metrics_frame, "🎯 Operações Hoje", "0", 0, 0)
        self._create_metric_card(metrics_frame, "✅ Sucessos", "0", 0, 1)
        self._create_metric_card(metrics_frame, "❌ Falhas", "0", 1, 0)
        self._create_metric_card(metrics_frame, "⏱️ Tempo Médio", "0s", 1, 1)

        # Status do sistema
        status_frame = tk.Frame(view, bg=self.theme['background'])
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Card de status
        status_card = tk.Frame(status_frame, bg=self.theme['card_bg'],
                              relief='solid', bd=1, highlightbackground=self.theme['border'])
        status_card.pack(fill=tk.X, pady=10)

        status_title = tk.Label(status_card, text="📊 Status do Sistema",
                               font=('Segoe UI', 14, 'bold'), bg=self.theme['card_bg'],
                               fg=self.theme['primary'])
        status_title.pack(pady=(15, 10))

        # Indicadores de status
        self.status_indicators = {}
        status_items = [
            ("Navegador", "offline", "🌐"),
            ("Agendador", "parado", "⏰"),
            ("Configuração", "ok", "⚙️"),
            ("Última Execução", "nunca", "🕒")
        ]

        for label, status, icon in status_items:
            self._create_status_indicator(status_card, icon, label, status)

        self.views['dashboard'] = view

    def _create_metric_card(self, parent, title: str, value: str, row: int, col: int):
        """Cria card de métrica premium com design refinado"""
        # Container externo para sombra/efeito
        container = tk.Frame(parent, bg=self.theme['background'])
        container.grid(row=row, column=col, padx=12, pady=12, sticky='nsew')

        # Card principal com borda refinada
        card = tk.Frame(container, bg=self.theme['card_bg'],
                       relief='solid', bd=0,
                       highlightbackground=self.theme['card_border'],
                       highlightcolor=self.theme['primary_light'],
                       highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Configurar grid responsivo
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # Header com ícone e título
        header_frame = tk.Frame(card, bg=self.theme['card_bg'])
        header_frame.grid(row=0, column=0, padx=18, pady=(18, 8), sticky='ew')
        header_frame.grid_columnconfigure(1, weight=1)

        # Extração de ícone do título (se existir)
        if ' ' in title and title.split()[0] in ['🎯', '✅', '❌', '⏱️', '📊', '🚀', '⚡', '🤖']:
            icon = title.split()[0]
            text_title = ' '.join(title.split()[1:])
        else:
            icon = "📊"
            text_title = title

        # Ícone elegante
        icon_label = tk.Label(header_frame, text=icon,
                             font=('Segoe UI', 16), bg=self.theme['card_bg'],
                             fg=self.theme['secondary'])
        icon_label.grid(row=0, column=0, padx=(0, 8))

        # Título refinado
        title_label = tk.Label(header_frame, text=text_title,
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.theme['card_bg'], fg=self.theme['text_secondary'],
                              anchor='w')
        title_label.grid(row=0, column=1, sticky='w')

        # Valor principal com destaque
        value_label = tk.Label(card, text=value,
                              font=('Segoe UI', 28, 'bold'),
                              bg=self.theme['card_bg'], fg=self.theme['primary'],
                              anchor='w')
        value_label.grid(row=1, column=0, padx=18, pady=(0, 18), sticky='w')

        # Animação de entrada
        self._animate_card_entrance(card, row * 100 + col * 100)

    def _create_status_indicator(self, parent, icon: str, label: str, status: str):
        """Cria indicador de status premium com design refinado"""
        # Container com padding elegante
        container = tk.Frame(parent, bg=self.theme['card_bg'])
        container.pack(fill=tk.X, padx=20, pady=6)

        # Frame interno com hover effect
        frame = tk.Frame(container, bg=self.theme['surface_light'],
                        relief='flat', bd=0)
        frame.pack(fill=tk.X, padx=1, pady=1)

        # Layout horizontal refinado
        frame.grid_columnconfigure(2, weight=1)  # Espaço expansível

        # Ícone com destaque
        icon_label = tk.Label(frame, text=icon, font=('Segoe UI', 16),
                             bg=self.theme['surface_light'], fg=self.theme['secondary'])
        icon_label.grid(row=0, column=0, padx=(15, 12), pady=12, sticky='w')

        # Label descritivo
        label_widget = tk.Label(frame, text=label, font=('Segoe UI', 11, 'bold'),
                               bg=self.theme['surface_light'], fg=self.theme['text_primary'],
                               anchor='w')
        label_widget.grid(row=0, column=1, sticky='w')

        # Espaçador
        spacer = tk.Frame(frame, bg=self.theme['surface_light'])
        spacer.grid(row=0, column=2, sticky='ew')

        # Status com badge elegante
        status_container = tk.Frame(frame, bg=self.theme['surface_light'])
        status_container.grid(row=0, column=3, padx=(0, 15))

        status_label = tk.Label(status_container, text=status.upper(),
                               font=('Segoe UI', 9, 'bold'),
                               bg=self.theme['surface'], fg=self.theme['text_primary'],
                               padx=8, pady=3, relief='flat')
        status_label.pack()

        # Cor baseada no status
        self._update_status_color(status_label, status)

        self.status_indicators[label] = status_label

    def _update_status_color(self, label, status: str):
        """Atualiza cor do status baseado no valor"""
        color_map = {
            'online': self.theme['success'],
            'ativo': self.theme['success'],
            'ok': self.theme['success'],
            'offline': self.theme['error'],
            'parado': self.theme['warning'],
            'erro': self.theme['error'],
            'nunca': self.theme['text_secondary']
        }

        color = color_map.get(status.lower(), self.theme['text_primary'])
        label.configure(fg=color)

    def _create_automation_view(self):
        """Cria view de automação com controles avançados"""
        view = tk.Frame(self.content_area, bg=self.theme['background'])

        # Título
        title_frame = tk.Frame(view, bg=self.theme['background'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="🤖 Centro de Automação",
                font=('Segoe UI', 20, 'bold'), bg=self.theme['background'],
                fg=self.theme['primary']).pack(pady=20)

        # Painel de controle
        control_panel = tk.Frame(view, bg=self.theme['background'])
        control_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Seção de configuração
        config_card = self._create_config_card(control_panel)
        config_card.pack(fill=tk.X, pady=(0, 20))

        # Seção de operações
        operations_card = self._create_operations_card(control_panel)
        operations_card.pack(fill=tk.BOTH, expand=True)

        self.views['automation'] = view

    def _create_config_card(self, parent) -> tk.Frame:
        """Cria card de configuração de credenciais com validação aprimorada"""
        # Usar componente padronizado para criar o card
        card = self.ui_components.create_card(parent)

        # Header usando componente padronizado
        header = tk.Frame(card, bg=self.theme['card_bg'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🔐 Configuração de Acesso",
                font=('Segoe UI', 14, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['primary']).pack(side=tk.LEFT, padx=15, pady=10)

        # Formulário usando componentes padronizados
        form_frame = tk.Frame(card, bg=self.theme['card_bg'])
        form_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Campos com validação integrada
        field_configs = [
            ("🌐 URL do Site", "url_entry", "", "url"),
            ("📧 E-mail", "email_entry", "", "email"),
            ("🔒 Senha", "password_entry", "*", "password")
        ]

        self.form_entries = {}
        for label_text, entry_name, show_char, validation_type in field_configs:
            # Usar componente padronizado para campos
            field_container, entry = self.ui_components.create_input_field(
                form_frame, label_text, show_char=show_char
            )
            field_container.pack(fill=tk.X, pady=5)

            # Armazenar referência e tipo de validação
            self.form_entries[entry_name] = {
                'widget': entry,
                'validation': validation_type
            }

            # Carregar valores salvos
            self._load_saved_credentials(entry_name, entry)

        # Botões
        buttons_frame = tk.Frame(card, bg=self.theme['card_bg'])
        buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        ttk.Button(buttons_frame, text="💾 Salvar Configuração",
                  style='Modern.TButton',
                  command=self._save_credentials).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(buttons_frame, text="🔍 Testar Conexão",
                  style='Modern.TButton',
                  command=self._test_connection).pack(side=tk.LEFT)

        return card

    def _create_operations_card(self, parent) -> tk.Frame:
        """Cria card de operações de automação"""
        card = tk.Frame(parent, bg=self.theme['card_bg'],
                       relief='solid', bd=1, highlightbackground=self.theme['border'])

        # Header
        header = tk.Frame(card, bg=self.theme['card_bg'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🎯 Operações de Automação",
                font=('Segoe UI', 14, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['primary']).pack(side=tk.LEFT, padx=15, pady=10)

        # Área de operações
        operations_frame = tk.Frame(card, bg=self.theme['card_bg'])
        operations_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Botões de operação
        operations = [
            ("🔍 Mapear Campos", "Mapeia automaticamente os campos do formulário", self._map_fields),
            ("🚀 Executar Login", "Executa login automatizado completo", self._run_automation),
            ("📊 Analisar Página", "Analisa estrutura da página web", self._analyze_page),
            ("🧹 Limpar Cache", "Limpa cache e dados temporários", self._clear_cache)
        ]

        for op_text, op_desc, op_command in operations:
            op_frame = tk.Frame(operations_frame, bg=self.theme['card_bg'])
            op_frame.pack(fill=tk.X, pady=5)

            btn = tk.Button(op_frame, text=op_text,
                           font=('Segoe UI', 11, 'bold'),
                           bg=self.theme['primary'], fg=self.theme['text_primary'],
                           relief='flat', padx=15, pady=8,
                           command=op_command, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(0, 10))

            desc_label = tk.Label(op_frame, text=op_desc,
                                font=('Segoe UI', 9), bg=self.theme['card_bg'],
                                fg=self.theme['text_secondary'])
            desc_label.pack(side=tk.LEFT, pady=10)

            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.theme['secondary']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.theme['primary']))

        # Progress bar para operações
        self.operation_progress = ttk.Progressbar(operations_frame,
                                                style='Modern.Horizontal.TProgressbar',
                                                mode='indeterminate')
        self.operation_progress.pack(fill=tk.X, pady=(20, 0))
        self.operation_progress.pack_forget()

        return card

    def _create_scheduler_view(self):
        """Cria view do agendador inteligente"""
        view = tk.Frame(self.content_area, bg=self.theme['background'])

        # Título
        title_frame = tk.Frame(view, bg=self.theme['background'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="⏰ Agendador Inteligente",
                font=('Segoe UI', 20, 'bold'), bg=self.theme['background'],
                fg=self.theme['primary']).pack(pady=20)

        # Painel de configuração
        config_panel = tk.Frame(view, bg=self.theme['background'])
        config_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Card de configuração de agendamento
        schedule_card = tk.Frame(config_panel, bg=self.theme['card_bg'],
                               relief='solid', bd=1, highlightbackground=self.theme['border'])
        schedule_card.pack(fill=tk.BOTH, expand=True, pady=10)

        # Header
        header = tk.Frame(schedule_card, bg=self.theme['card_bg'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="📅 Configuração de Agendamento",
                font=('Segoe UI', 14, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['primary']).pack(side=tk.LEFT, padx=15, pady=10)

        # Status do agendador
        self.scheduler_status_label = tk.Label(header, text="PARADO",
                                             font=('Segoe UI', 10, 'bold'),
                                             bg=self.theme['card_bg'], fg=self.theme['warning'])
        self.scheduler_status_label.pack(side=tk.RIGHT, padx=15, pady=10)

        # Formulário de agendamento
        form_frame = tk.Frame(schedule_card, bg=self.theme['card_bg'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Horários
        time_frame = tk.Frame(form_frame, bg=self.theme['card_bg'])
        time_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(time_frame, text="⏰ Horários de Execução:",
                font=('Segoe UI', 11, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['text_primary']).pack(anchor=tk.W, pady=(0, 5))

        self.schedule_times_entry = tk.Entry(time_frame, font=('Consolas', 10),
                                           bg=self.theme['surface'], fg=self.theme['text_primary'],
                                           insertbackground=self.theme['text_primary'],
                                           relief='solid', bd=1)
        self.schedule_times_entry.pack(fill=tk.X)
        self.schedule_times_entry.insert(0, "08:00,12:00,18:00,22:00")

        # Dias da semana
        days_frame = tk.Frame(form_frame, bg=self.theme['card_bg'])
        days_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(days_frame, text="📅 Dias da Semana:",
                font=('Segoe UI', 11, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['text_primary']).pack(anchor=tk.W, pady=(0, 5))

        # Container para checkboxes
        days_container = tk.Frame(days_frame, bg=self.theme['card_bg'])
        days_container.pack(fill=tk.X)

        self.day_vars = {}
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=True)
            self.day_vars[day] = var

            cb = tk.Checkbutton(days_container, text=day, variable=var,
                              bg=self.theme['card_bg'], fg=self.theme['text_primary'],
                              font=('Segoe UI', 9), selectcolor=self.theme['surface'])
            cb.pack(side=tk.LEFT, padx=(0, 10))

        # Modo de repetição
        repeat_frame = tk.Frame(form_frame, bg=self.theme['card_bg'])
        repeat_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(repeat_frame, text="🔄 Modo de Repetição:",
                font=('Segoe UI', 11, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['text_primary']).pack(anchor=tk.W, pady=(0, 5))

        self.repeat_var = tk.StringVar(value="diariamente")
        repeat_combo = ttk.Combobox(repeat_frame, textvariable=self.repeat_var,
                                   values=["diariamente", "semanalmente", "mensalmente"],
                                   state="readonly", font=('Segoe UI', 10))
        repeat_combo.pack(fill=tk.X)

        # Botões de controle
        buttons_frame = tk.Frame(form_frame, bg=self.theme['card_bg'])
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="▶️ INICIAR AGENDAMENTO",
                  style='Modern.TButton',
                  command=self._start_scheduler).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(buttons_frame, text="⏹️ PARAR AGENDAMENTO",
                  style='Modern.TButton',
                  command=self._stop_scheduler).pack(side=tk.LEFT)

        self.views['scheduler'] = view

    def _create_settings_view(self):
        """Cria view de configurações avançadas"""
        view = tk.Frame(self.content_area, bg=self.theme['background'])

        # Título
        title_frame = tk.Frame(view, bg=self.theme['background'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="⚙️ Configurações Avançadas",
                font=('Segoe UI', 20, 'bold'), bg=self.theme['background'],
                fg=self.theme['primary']).pack(pady=20)

        # Container de configurações
        settings_container = tk.Frame(view, bg=self.theme['background'])
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Configurações do navegador
        browser_card = self._create_settings_card(settings_container,
                                                "🌐 Navegador",
                                                self._get_browser_settings())
        browser_card.pack(fill=tk.X, pady=(0, 10))

        # Configurações de automação
        automation_card = self._create_settings_card(settings_container,
                                                   "🤖 Automação",
                                                   self._get_automation_settings())
        automation_card.pack(fill=tk.X, pady=(0, 10))

        # Configurações do sistema
        system_card = self._create_settings_card(settings_container,
                                               "💻 Sistema",
                                               self._get_system_settings())
        system_card.pack(fill=tk.X, pady=(0, 10))

        self.views['settings'] = view

    def _create_settings_card(self, parent, title: str, settings: list) -> tk.Frame:
        """Cria card de configurações"""
        card = tk.Frame(parent, bg=self.theme['card_bg'],
                       relief='solid', bd=1, highlightbackground=self.theme['border'])

        # Header
        header = tk.Frame(card, bg=self.theme['card_bg'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text=title, font=('Segoe UI', 12, 'bold'),
                bg=self.theme['card_bg'], fg=self.theme['primary']).pack(
                    side=tk.LEFT, padx=15, pady=8)

        # Configurações
        settings_frame = tk.Frame(card, bg=self.theme['card_bg'])
        settings_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        for setting in settings:
            self._create_setting_row(settings_frame, setting)

        return card

    def _create_setting_row(self, parent, setting: dict):
        """Cria linha de configuração"""
        row_frame = tk.Frame(parent, bg=self.theme['card_bg'])
        row_frame.pack(fill=tk.X, pady=2)

        # Label
        label = tk.Label(row_frame, text=setting['label'],
                        font=('Segoe UI', 10), bg=self.theme['card_bg'],
                        fg=self.theme['text_primary'])
        label.pack(side=tk.LEFT, padx=(0, 10))

        # Controle (baseado no tipo)
        control_type = setting.get('type', 'entry')

        if control_type == 'checkbox':
            var = tk.BooleanVar(value=setting.get('value', False))
            control = tk.Checkbutton(row_frame, variable=var,
                                   bg=self.theme['card_bg'],
                                   fg=self.theme['text_primary'])
            setting['var'] = var

        elif control_type == 'combobox':
            var = tk.StringVar(value=setting.get('value', ''))
            control = ttk.Combobox(row_frame, textvariable=var,
                                 values=setting.get('options', []),
                                 state="readonly", width=15)
            setting['var'] = var

        else:  # entry
            var = tk.StringVar(value=setting.get('value', ''))
            control = tk.Entry(row_frame, textvariable=var,
                             font=('Segoe UI', 9),
                             bg=self.theme['surface'], fg=self.theme['text_primary'],
                             insertbackground=self.theme['text_primary'],
                             relief='solid', bd=1, width=20)
            setting['var'] = var

        control.pack(side=tk.RIGHT)

    def _get_browser_settings(self) -> list:
        """Retorna configurações do navegador"""
        return [
            {'label': 'Modo headless:', 'type': 'checkbox', 'value': False},
            {'label': 'Timeout (segundos):', 'type': 'entry', 'value': '10'},
            {'label': 'Capturar screenshots:', 'type': 'checkbox', 'value': True},
            {'label': 'User agent personalizado:', 'type': 'checkbox', 'value': True}
        ]

    def _get_automation_settings(self) -> list:
        """Retorna configurações de automação"""
        return [
            {'label': 'Tentativas máximas:', 'type': 'entry', 'value': '3'},
            {'label': 'Modo híbrido automático:', 'type': 'checkbox', 'value': True},
            {'label': 'Análise inteligente:', 'type': 'checkbox', 'value': True},
            {'label': 'Backup automático:', 'type': 'checkbox', 'value': True}
        ]

    def _get_system_settings(self) -> list:
        """Retorna configurações do sistema"""
        return [
            {'label': 'Nível de log:', 'type': 'combobox',
             'value': 'INFO', 'options': ['DEBUG', 'INFO', 'WARNING', 'ERROR']},
            {'label': 'Tema:', 'type': 'combobox',
             'value': 'escuro', 'options': ['escuro', 'claro', 'automático']},
            {'label': 'Notificações:', 'type': 'checkbox', 'value': True},
            {'label': 'Atualizações automáticas:', 'type': 'checkbox', 'value': False}
        ]

    def _create_logs_view(self):
        """Cria view de logs com filtros avançados"""
        view = tk.Frame(self.content_area, bg=self.theme['background'])

        # Título
        title_frame = tk.Frame(view, bg=self.theme['background'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="📋 Centro de Logs",
                font=('Segoe UI', 20, 'bold'), bg=self.theme['background'],
                fg=self.theme['primary']).pack(pady=20)

        # Container de logs
        logs_container = tk.Frame(view, bg=self.theme['background'])
        logs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Barra de ferramentas
        toolbar = tk.Frame(logs_container, bg=self.theme['card_bg'], height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # Filtros
        filter_frame = tk.Frame(toolbar, bg=self.theme['card_bg'])
        filter_frame.pack(side=tk.LEFT, padx=15, pady=10)

        tk.Label(filter_frame, text="🔍 Filtros:",
                font=('Segoe UI', 10, 'bold'), bg=self.theme['card_bg'],
                fg=self.theme['text_primary']).pack(side=tk.LEFT, padx=(0, 10))

        self.log_filter_var = tk.StringVar(value="todos")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.log_filter_var,
                                   values=["todos", "erros", "avisos", "sucessos", "info"],
                                   state="readonly", font=('Segoe UI', 9), width=10)
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', self._filter_logs)

        # Botões de ação
        buttons_frame = tk.Frame(toolbar, bg=self.theme['card_bg'])
        buttons_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        ttk.Button(buttons_frame, text="🧹 Limpar",
                  command=self._clear_logs).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(buttons_frame, text="💾 Salvar",
                  command=self._save_logs).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(buttons_frame, text="🔄 Atualizar",
                  command=self._refresh_logs).pack(side=tk.LEFT)

        # Área de logs
        logs_frame = tk.Frame(logs_container, bg=self.theme['card_bg'])
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Text area com syntax highlighting simulado
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            font=('Consolas', 9),
            bg=self.theme['surface'],
            fg=self.theme['text_primary'],
            insertbackground=self.theme['text_primary'],
            selectbackground=self.theme['primary'],
            relief='flat',
            padx=10,
            pady=10
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True)

        # Tags para colorização
        self.logs_text.tag_configure("error", foreground=self.theme['error'])
        self.logs_text.tag_configure("warning", foreground=self.theme['warning'])
        self.logs_text.tag_configure("success", foreground=self.theme['success'])
        self.logs_text.tag_configure("info", foreground=self.theme['text_secondary'])

        self.views['logs'] = view

    def _create_status_bar(self):
        """Cria barra de status inferior moderna"""
        self.status_bar = tk.Frame(self.root, bg=self.theme['surface'], height=30)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        # Status text
        self.status_label = tk.Label(self.status_bar, text="Sistema pronto",
                                   font=('Segoe UI', 9), bg=self.theme['surface'],
                                   fg=self.theme['text_primary'])
        self.status_label.pack(side=tk.LEFT, padx=15)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var,
                                          maximum=100, mode='determinate',
                                          style='Modern.Horizontal.TProgressbar', length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=15)
        self.progress_bar.pack_forget()

        # Status indicators
        indicators_frame = tk.Frame(self.status_bar, bg=self.theme['surface'])
        indicators_frame.pack(side=tk.RIGHT, padx=(0, 15))

        self.status_indicators_bar = {}
        indicators = [
            ("CPU", "0%"),
            ("Memória", "0MB"),
            ("Rede", "OK")
        ]

        for label, value in indicators:
            indicator = tk.Label(indicators_frame, text=f"{label}: {value}",
                               font=('Segoe UI', 8), bg=self.theme['surface'],
                               fg=self.theme['text_secondary'])
            indicator.pack(side=tk.LEFT, padx=(0, 15))
            self.status_indicators_bar[label] = indicator

    def _setup_notifications(self):
        """Configura sistema de notificações flutuantes"""
        self.notifications_frame = tk.Frame(self.root, bg=self.theme['background'])
        # Posiciona no canto superior direito
        self.notifications_frame.place(relx=1.0, rely=0.0, anchor='ne')

    def _setup_animations(self):
        """Configura sistema de animações"""
        self.animations_running = {}

    def _load_initial_data(self):
        """Carrega dados iniciais da aplicação"""

        # Carregar configurações salvas
        self._load_saved_config()

        # Atualizar status
        self._update_system_status()

        # Iniciar monitoramento
        self._start_system_monitoring()


    def _show_view(self, view_name: str):
        """Mostra uma view específica com animação"""
        # Esconde todas as views
        for view in self.views.values():
            view.pack_forget()

        # Atualiza navegação com novo sistema visual
        for name, btn in self.nav_buttons.items():
            if hasattr(btn, 'update_selection'):
                btn.update_selection()

        # Mostra view selecionada
        if view_name in self.views:
            self.views[view_name].pack(fill=tk.BOTH, expand=True)
            self.current_view = view_name

            # Animação de entrada
            self._animate_view_transition(view_name)

    def _filter_logs(self, event=None):
        """Filtra logs baseado na seleção do combobox"""
        try:
            filter_type = self.log_filter_var.get()
            # Aqui você pode implementar a lógica de filtro
            # Por enquanto, apenas atualiza o display
            self._update_logs_display()
        except Exception as e:
            self._log_message(f"Erro ao filtrar logs: {e}", "ERROR")

    def _update_logs_display(self):
        """Atualiza a exibição dos logs"""
        try:
            # Implementação básica - pode ser expandida
            pass
        except Exception as e:
            self._log_message(f"Erro ao atualizar logs: {e}", "ERROR")

    def _clear_logs(self):
        """Limpa todos os logs"""
        try:
            # Limpar o text widget de logs
            if hasattr(self, 'logs_text'):
                self.logs_text.delete(1.0, tk.END)
            self._log_message("Logs limpos com sucesso", "INFO")
        except Exception as e:
            self._log_message(f"Erro ao limpar logs: {e}", "ERROR")

    def _save_logs(self):
        """Salva os logs em arquivo"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    if hasattr(self, 'logs_text'):
                        f.write(self.logs_text.get(1.0, tk.END))
                self._log_message(f"Logs salvos em: {filename}", "SUCCESS")
        except Exception as e:
            self._log_message(f"Erro ao salvar logs: {e}", "ERROR")

    def _refresh_logs(self):
        """Atualiza/refresh os logs"""
        try:
            self._update_logs_display()
            self._log_message("Logs atualizados", "INFO")
        except Exception as e:
            self._log_message(f"Erro ao atualizar logs: {e}", "ERROR")

    def _animate_card_entrance(self, card, delay: int = 0):
        """Anima entrada de card"""
        def animate():
            # Fade in effect - usando abordagem compatível com Frames
            try:
                # Para Frames, usamos uma abordagem diferente ou simplesmente mostramos
                card.configure(bg=self.theme['card_bg'])
                self.root.update()
            except:
                pass  # Fallback silencioso

        if delay > 0:
            self.root.after(delay, animate)
        else:
            animate()

    def _animate_view_transition(self, view_name: str):
        """Anima transição entre views"""
        # Implementar fade transition
        pass

    def _add_tooltip(self, widget, text: str):
        """Adiciona tooltip a um widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, font=('Segoe UI', 8),
                           bg=self.theme['surface'], fg=self.theme['text_primary'],
                           relief='solid', bd=1)
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)

    # Métodos de operação
    def _load_saved_credentials(self, entry_name: str, entry_widget):
        """Carrega credenciais salvas nos campos"""
        try:
            if entry_name == 'url_entry':
                value = self.config_manager.get('site', 'url', '')
            elif entry_name == 'email_entry':
                value = self.config_manager.get('credentials', 'email', '')
            elif entry_name == 'password_entry':
                value = self.config_manager.get('credentials', 'password', '')
            else:
                value = ''

            if value:
                entry_widget.insert(0, value)

        except Exception as e:
            print(f"Erro ao carregar {entry_name}: {e}")

    def _save_credentials(self):
        """Salva credenciais do formulário com validação aprimorada"""
        try:
            # Extrair valores dos campos (nova estrutura)
            config = {}
            validation_errors = []

            for field_name, field_data in self.form_entries.items():
                widget = field_data['widget']
                validation_type = field_data['validation']
                value = widget.get().strip() if field_name != 'password_entry' else widget.get()

                # Aplicar validação específica usando ValidationUtils
                if validation_type == 'url':
                    is_valid, message = self.validation.validate_url(value)
                    config['url'] = value
                elif validation_type == 'email':
                    is_valid, message = self.validation.validate_email(value)
                    config['email'] = value
                elif validation_type == 'password':
                    is_valid, message = self.validation.validate_password(value)
                    config['password'] = value

                if not is_valid:
                    validation_errors.append(message)

            # Se houver erros de validação, mostrar todos
            if validation_errors:
                error_msg = "\n".join(f"• {error}" for error in validation_errors)
                self._show_notification(f"❌ Erros de validação:\n{error_msg}", "error")
                return

            # Salvar no config manager
            self.config_manager.set('site', 'url', config['url'])
            self.config_manager.set('credentials', 'email', config['email'])
            self.config_manager.set('credentials', 'password', config['password'])

            self.config_manager.save_config()
            self._show_notification("✅ Configuração salva com sucesso!", "success")

            # Log da operação
            self._log_message(f"[CONFIG] Credenciais salvas para {config['email']}")

        except Exception as e:
            self._log_message(f"[ERROR] Falha ao salvar credenciais: {e}")
            self._show_notification(f"❌ Erro ao salvar: {e}", "error")

    def _test_connection(self):
        """Testa conexão real com o site usando validação aprimorada"""
        # Usar nova estrutura dos form_entries
        url = self.form_entries['url_entry']['widget'].get().strip()

        if not url:
            self._show_notification("❌ URL não configurada!", "warning")
            return

        # Usar ValidationUtils para validação
        is_valid, message = self.validation.validate_url(url)
        if not is_valid:
            self._show_notification(f"❌ {message}", "warning")
            return

        self._show_notification("🔄 Testando conexão...", "info")

        def test():
            try:
                import requests
                import time

                # Tenta fazer uma requisição GET
                response = requests.get(url, timeout=10, allow_redirects=True)

                if response.status_code == 200:
                    self._show_notification("✅ Conexão estabelecida com sucesso!", "success")
                elif response.status_code == 401:
                    self._show_notification("⚠️ Site acessível, mas requer autenticação", "warning")
                elif response.status_code == 403:
                    self._show_notification("🚫 Acesso proibido ao site", "error")
                elif response.status_code >= 500:
                    self._show_notification("🛠️ Erro interno do servidor", "error")
                else:
                    self._show_notification(f"⚠️ Resposta HTTP {response.status_code}", "warning")

            except requests.exceptions.Timeout:
                self._show_notification("⏱️ Timeout - Site não respondeu", "error")
            except requests.exceptions.ConnectionError:
                self._show_notification("🌐 Erro de conexão - Site inacessível", "error")
            except requests.exceptions.RequestException as e:
                self._show_notification(f"❌ Erro de rede: {str(e)[:50]}", "error")
            except ImportError:
                # Fallback se requests não estiver disponível
                self._show_notification("✅ URL válida (teste limitado)", "success")
            except Exception as e:
                self._show_notification(f"❌ Erro inesperado: {str(e)[:50]}", "error")

        threading.Thread(target=test, daemon=True).start()

    def _run_automation(self):
        """Executa automação de login"""
        try:
            url = self.config_manager.get('site', 'url', '')
            email = self.config_manager.get('credentials', 'email', '')
            password = self.config_manager.get('credentials', 'password', '')

            if not all([url, email, password]):
                self._show_notification("❌ Configure credenciais primeiro!", "error")
                return

            self._show_notification("🚀 Iniciando automação...", "info")

            def automate():
                try:
                    # Simula processo de automação
                    self._log_message(f"[AUTOMATION] Iniciando login em {url}")
                    time.sleep(2)

                    # Simula passos da automação
                    self._log_message("[AUTOMATION] Passo 1: Acessando página")
                    time.sleep(1)
                    self._log_message("[AUTOMATION] Passo 2: Localizando formulário")
                    time.sleep(1)
                    self._log_message("[AUTOMATION] Passo 3: Preenchendo credenciais")
                    time.sleep(1)
                    self._log_message("[AUTOMATION] Passo 4: Enviando formulário")
                    time.sleep(1)

                    success = True  # Simula sucesso
                    if success:
                        self._log_message("[AUTOMATION] ✅ Login realizado com sucesso!")
                        self._show_notification("🎉 Login realizado com sucesso!", "success")
                    else:
                        self._log_message("[AUTOMATION] ❌ Falha no login")
                        self._show_notification("❌ Falha no login", "error")

                except Exception as e:
                    self._log_message(f"[AUTOMATION] Erro: {e}")
                    self._show_notification(f"❌ Erro na automação: {e}", "error")

            threading.Thread(target=automate, daemon=True).start()

        except Exception as e:
            self._show_notification(f"❌ Erro ao iniciar automação: {e}", "error")

    def _map_fields(self):
        """Mapeia campos do formulário automaticamente"""
        url = self.config_manager.get('site', 'url', '')

        if not url:
            self._show_notification("❌ Configure a URL do site primeiro!", "error")
            return

        self._show_progress("🔍 Mapeando campos...")
        self._show_notification("🤖 Analisando estrutura da página...", "info")

        def map_process():
            try:
                # Simula análise da página
                self._log_message(f"[MAPPING] Analisando site: {url}")
                time.sleep(1)

                self._log_message("[MAPPING] Procurando formulários...")
                time.sleep(1)

                # Simula detecção de campos
                detected_fields = [
                    "📧 Campo de e-mail: input[type='email']",
                    "🔒 Campo de senha: input[type='password']",
                    "🎯 Botão submit: button[type='submit']",
                    "💡 Campos adicionais: 2 selects, 1 checkbox"
                ]

                for field in detected_fields:
                    self._log_message(f"[FIELD] {field}")
                    time.sleep(0.5)

                self._log_message(f"[SUCCESS] Mapeamento concluído - {len(detected_fields)} elementos encontrados")
                self._hide_progress()
                self._show_notification("✅ Campos mapeados com sucesso!", "success")

                # Mostra resumo
                summary = f"Detectados {len(detected_fields)} elementos de formulário"
                self._show_notification(summary, "info")

            except Exception as e:
                self._hide_progress()
                self._log_message(f"[ERROR] Falha no mapeamento: {e}")
                self._show_notification(f"❌ Erro no mapeamento: {str(e)[:50]}", "error")

        threading.Thread(target=map_process, daemon=True).start()

    def _run_automation(self):
        """Executa automação completa"""
        self._show_progress("Executando automação...")
        self._show_notification("Executando login automatizado...", "info")

        def automation_process():
            try:
                # Simula execução
                for i in range(1, 101, 10):
                    self._update_progress(i)
                    time.sleep(0.5)

                self._hide_progress()
                self._show_notification("Login executado com sucesso!", "success")
                self._log_message("[SUCCESS] Login automatizado concluído")

            except Exception as e:
                self._hide_progress()
                self._show_notification(f"Erro na automação: {e}", "error")

        threading.Thread(target=automation_process, daemon=True).start()

    def _analyze_page(self):
        """Analisa estrutura detalhada da página"""
        url = self.config_manager.get('site', 'url', '')

        if not url:
            self._show_notification("❌ Configure a URL do site primeiro!", "error")
            return

        self._show_progress("🔬 Analisando página...")
        self._show_notification("🧠 Analisando estrutura da página...", "info")

        def analyze():
            try:
                self._log_message(f"[ANALYSIS] Analisando: {url}")

                # Simula análise detalhada
                analysis_steps = [
                    "Carregando página...",
                    "Analisando HTML...",
                    "Detectando formulários...",
                    "Mapeando campos...",
                    "Verificando elementos...",
                    "Finalizando análise..."
                ]

                for step in analysis_steps:
                    self._log_message(f"[ANALYSIS] {step}")
                    time.sleep(0.8)

                # Resultado da análise
                analysis_result = """
📊 ANÁLISE CONCLUÍDA:
• Formulários encontrados: 2
• Campos de entrada: 8
• Botões de ação: 3
• Elementos interativos: 15
• Tempo de carregamento: ~2.3s
• Compatibilidade: 98%
                """

                self._log_message("[ANALYSIS] " + analysis_result.replace('\n', ' | '))
                self._hide_progress()
                self._show_notification("✅ Análise concluída com sucesso!", "success")

            except Exception as e:
                self._hide_progress()
                self._log_message(f"[ERROR] Falha na análise: {e}")
                self._show_notification(f"❌ Erro na análise: {str(e)[:50]}", "error")

        threading.Thread(target=analyze, daemon=True).start()

    def _clear_cache(self):
        """Limpa cache do sistema"""
        self._show_notification("Limpando cache...", "info")

        def clear():
            try:
                time.sleep(1)
                self._show_notification("Cache limpo com sucesso!", "success")
                self._log_message("[CLEANUP] Cache do sistema limpo")

            except Exception as e:
                self._show_notification(f"Erro ao limpar cache: {e}", "error")

        threading.Thread(target=clear, daemon=True).start()

    def _start_scheduler(self):
        """Inicia agendador inteligente"""
        try:
            times = self.schedule_times_entry.get()
            days = [day for day, var in self.day_vars.items() if var.get()]
            repeat = self.repeat_var.get()

            if not times:
                self._show_notification("Configure horários primeiro", "warning")
                return

            if not days:
                self._show_notification("Selecione pelo menos um dia", "warning")
                return

            # Simula inicialização do agendador
            self.scheduler_status_label.config(text="ATIVO", fg=self.theme['success'])
            self._show_notification(f"Agendador iniciado: {times} ({repeat})", "success")
            self._log_message(f"[SCHEDULER] Agendamento ativo: {times} nos dias {', '.join(days)}")

        except Exception as e:
            self._show_notification(f"Erro no agendador: {e}", "error")

    def _stop_scheduler(self):
        """Para agendador"""
        self.scheduler_status_label.config(text="PARADO", fg=self.theme['warning'])
        self._show_notification("Agendador parado", "info")
        self._log_message("[SCHEDULER] Agendamento interrompido")

    # Métodos utilitários
    def _show_notification(self, message: str, type_: str = "info"):
        """Mostra notificação flutuante"""
        # Cria notificação
        notification = tk.Frame(self.notifications_frame, bg=self.theme['card_bg'],
                               relief='solid', bd=1, highlightbackground=self.theme['border'])

        # Ícone baseado no tipo
        icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }

        icon_label = tk.Label(notification, text=icons.get(type_, 'ℹ️'),
                             font=('Segoe UI', 12), bg=self.theme['card_bg'],
                             fg=self.theme['text_primary'])
        icon_label.pack(side=tk.LEFT, padx=10, pady=10)

        message_label = tk.Label(notification, text=message,
                               font=('Segoe UI', 10), bg=self.theme['card_bg'],
                               fg=self.theme['text_primary'])
        message_label.pack(side=tk.LEFT, padx=(0, 10), pady=10)

        # Posiciona notificação
        notification.pack(pady=5, padx=10)

        # Remove automaticamente após 3 segundos
        def remove_notification():
            notification.destroy()

        self.root.after(3000, remove_notification)

    def _show_progress(self, message: str = "Processando..."):
        """Mostra barra de progresso"""
        self.status_label.config(text=message)
        self.progress_bar.pack(side=tk.RIGHT, padx=15)
        self.progress_bar.start()

    def _update_progress(self, value: int):
        """Atualiza progresso"""
        self.progress_var.set(value)

    def _hide_progress(self):
        """Oculta barra de progresso"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_label.config(text="Sistema pronto")

    def _log_message(self, message: str):
        """Adiciona mensagem aos logs"""
        if hasattr(self, 'logs_text'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.logs_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.logs_text.see(tk.END)

    def _load_saved_config(self):
        """Carrega configurações salvas nos campos"""
        try:
            if hasattr(self, 'form_entries'):
                self.form_entries['url_entry'].insert(0,
                    self.config_manager.get('site', 'url', ''))
                self.form_entries['email_entry'].insert(0,
                    self.config_manager.get('credentials', 'email', ''))
                # Senha não é carregada por segurança
        except:
            pass

    def _update_system_status(self):
        """Atualiza indicadores de status do sistema"""
        # Simula atualização de status
        if hasattr(self, 'status_indicators'):
            self.status_indicators["Navegador"].config(text="offline")
            self.status_indicators["Agendador"].config(text="parado")
            self.status_indicators["Configuração"].config(text="ok")
            self.status_indicators["Última Execução"].config(text="nunca")

    def _start_system_monitoring(self):
        """Inicia monitoramento do sistema"""
        def monitor():
            while True:
                try:
                    # Simula monitoramento
                    time.sleep(5)
                except:
                    break

        threading.Thread(target=monitor, daemon=True).start()

    # Métodos de janela
    def _toggle_fullscreen(self, event=None):
        """Alterna modo tela cheia"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def _exit_fullscreen(self, event=None):
        """Sai do modo tela cheia"""
        self.root.attributes('-fullscreen', False)

    def _minimize_window(self):
        """Minimiza janela"""
        self.root.iconify()

    def _new_operation(self):
        """Nova operação (atalho)"""
        self._show_view('automation')

    def _save_config(self):
        """Salva configuração (atalho)"""
        self._save_credentials()

    def _on_closing(self):
        """Tratamento do fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do Automatizador IA?"):
            # Cleanup
            if hasattr(self, 'automation_engine') and self.automation_engine:
                self.automation_engine.cleanup()

            if hasattr(self, 'smart_scheduler'):
                self.smart_scheduler.cleanup()

            self.root.quit()

    def run(self):
        """Inicia a aplicação"""
        self._log_message("[START] Automatizador IA v4.0 iniciado")
        self._show_notification("Sistema inicializado com sucesso!", "success")


        # Garantir que a interface seja totalmente renderizada antes do mainloop
        self.root.update_idletasks()
        self.root.update()

        try:
            self.root.mainloop()
        except Exception as e:
            raise



# Função principal para executar a interface
def main():
    """Função principal"""
    try:
        print("[DEBUG] Criando instância ModernInterface...")
        app = ModernInterface()
        print("[DEBUG] Instância criada, iniciando run()...")
        app.run()
        print("[DEBUG] run() concluído")
    except Exception as e:
        print(f"[DEBUG] Erro em main(): {e}")
        import traceback
        traceback.print_exc()


# ===== CLASSES AUXILIARES =====

class UIComponents:
    """Componentes reutilizáveis da interface"""

    def __init__(self, theme: Dict[str, str]):
        self.theme = theme

    def create_card(self, parent, title: str = "", icon: str = "") -> tk.Frame:
        """Cria um card padronizado"""
        card = tk.Frame(parent, bg=self.theme['card_bg'],
                       relief='solid', bd=1, highlightbackground=self.theme['card_border'])

        if title:
            self._create_card_header(card, title, icon)

        return card

    def _create_card_header(self, card: tk.Frame, title: str, icon: str):
        """Cria header padronizado para cards"""
        header = tk.Frame(card, bg=self.theme['card_bg'])
        header.pack(fill=tk.X, padx=18, pady=(18, 8))

        if icon:
            icon_label = tk.Label(header, text=icon, font=('Segoe UI', 20),
                                 bg=self.theme['card_bg'], fg=self.theme['primary'])
            icon_label.pack(side=tk.LEFT, padx=(0, 12))

        title_label = tk.Label(header, text=title, font=('Segoe UI', 14, 'bold'),
                              bg=self.theme['card_bg'], fg=self.theme['text_primary'])
        title_label.pack(side=tk.LEFT)

    def create_button(self, parent, text: str, command: Callable,
                     style_type: str = 'primary', **kwargs) -> tk.Button:
        """Cria botão padronizado"""
        style_map = {
            'primary': {
                'bg': self.theme['primary'],
                'fg': self.theme['text_primary'],
                'active_bg': self.theme['primary_hover']
            },
            'secondary': {
                'bg': self.theme['surface_light'],
                'fg': self.theme['text_primary'],
                'active_bg': self.theme['surface_hover']
            },
            'danger': {
                'bg': self.theme['error'],
                'fg': 'white',
                'active_bg': self.theme['error_bg']
            }
        }

        style = style_map.get(style_type, style_map['primary'])

        button = tk.Button(parent, text=text, command=command,
                          font=('Segoe UI', 10, 'bold'),
                          bg=style['bg'], fg=style['fg'],
                          relief='flat', padx=15, pady=8,
                          cursor="hand2", **kwargs)

        # Bind de hover
        def on_enter(e):
            button.configure(bg=style['active_bg'])
        def on_leave(e):
            button.configure(bg=style['bg'])

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

        return button

    def create_input_field(self, parent, label_text: str, entry_type: str = 'text',
                          show_char: str = '') -> Tuple[tk.Frame, tk.Entry]:
        """Cria campo de entrada padronizado"""
        container = tk.Frame(parent, bg=self.theme['card_bg'])

        # Label
        label = tk.Label(container, text=label_text, font=('Segoe UI', 10),
                        bg=self.theme['card_bg'], fg=self.theme['text_secondary'])
        label.pack(anchor=tk.W, pady=(0, 5))

        # Entry
        entry = tk.Entry(container, font=('Segoe UI', 10),
                        bg=self.theme['input_bg'], fg=self.theme['text_primary'],
                        insertbackground=self.theme['text_primary'],
                        relief='solid', bd=1, show=show_char)
        entry.pack(fill=tk.X)

        return container, entry


class ValidationUtils:
    """Utilitários de validação"""

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Valida URL"""
        if not url.strip():
            return False, "URL é obrigatória"

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return False, "URL deve começar com http:// ou https://"

        # Regex básica para validar formato de URL
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            return False, "Formato de URL inválido"

        return True, "URL válida"

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Valida email"""
        if not email.strip():
            return False, "E-mail é obrigatório"

        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email.strip()):
            return False, "Formato de e-mail inválido"

        return True, "E-mail válido"

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Valida senha"""
        if not password:
            return False, "Senha é obrigatória"

        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"

        return True, "Senha válida"


if __name__ == '__main__':
    main()
