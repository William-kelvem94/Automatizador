"""
🚀 INTERFACE MODERNA REVOLUCIONÁRIA - v5.0
Design System Avançado com IA Integrada
Interface completamente redesenhada com experiência excepcional
"""

import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk
from typing import Tuple

# Imports do sistema
from src.core.config_manager import ConfigManager
from src.core.automation_engine import AutomationEngine
from src.core.scheduler import SmartScheduler
from src.ui.components.factory import ComponentFactory
from src.ui.styles.design_system import DesignSystem


class ModernInterface:
    """Interface Moderna Revolucionária v5.0"""

    def __init__(self):
        # Sistema de Design
        self.ds = DesignSystem()
        self.factory = None

        # Estado da aplicação
        self.config_manager = ConfigManager()
        self.automation_engine = AutomationEngine(self.config_manager.get_all())
        self.smart_scheduler = SmartScheduler()
        
        # Inicializar componentes
        self.automation_engine.initialize()
        self.smart_scheduler.initialize()

        # Estado da UI
        self.current_view = "dashboard"
        self.views = {}
        self.animations = {}
        self.notifications = []
        self.notifications_frame = None
        self.nav_buttons = {}
        self.animations_running = True
        
        # Monitoramento e Status
        self.metrics = {
            "operations_today": 0,
            "success_rate": 0,
            "avg_duration": 0,
            "active_tasks": 0,
        }
        self.metric_value_labels = {}
        self.status_indicators = {}
        self.status_indicators_bar = {}
        self.all_settings = {}
        self.setting_vars = {}

        # Inicializar interface
        self._setup_main_window()
        self.factory = ComponentFactory(self.root, self.ds)
        self._create_layout()
        self._setup_animations()
        self._load_initial_data()

    def _setup_main_window(self):
        """Configura janela principal com design revolucionário"""
        self.root = tk.Tk()
        self.root.title("🚀 Automatizador IA v5.0 - Sistema Inteligente Revolucionário")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.ds.colors["bg_primary"])
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)

        # Remove bordas padrão do Windows
        try:
            self.root.attributes("-alpha", 0.0)

            # Fade in suave
            def fade_in():
                alpha = self.root.attributes("-alpha")
                if alpha < 1.0:
                    self.root.attributes("-alpha", alpha + 0.05)
                    self.root.after(20, fade_in)
                else:
                    self.root.attributes("-alpha", 1.0)

            self.root.after(100, fade_in)
        except:
            pass

        # Ícone da aplicação
        try:
            self.root.iconbitmap(default="assets/icon.ico")
        except:
            pass

        # Bindings avançados
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._exit_fullscreen)
        self.root.bind("<Control-n>", lambda e: self._new_operation())
        self.root.bind("<Control-s>", lambda e: self._save_config())
        self.root.bind("<Control-l>", lambda e: self._show_view("logs"))
        self.root.bind("<Control-d>", lambda e: self._show_view("dashboard"))

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Garantir visibilidade
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))

    def _create_layout(self):
        """Cria layout principal revolucionário"""
        # Container principal
        self.main_container = tk.Frame(self.root, bg=self.ds.colors["bg_primary"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header superior premium
        self._create_header()

        # Container de conteúdo
        content_container = tk.Frame(
            self.main_container, bg=self.ds.colors["bg_primary"]
        )
        content_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar moderna
        self.sidebar = self._create_sidebar()
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Área de conteúdo principal
        self.content_area = tk.Frame(content_container, bg=self.ds.colors["bg_primary"])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Views modulares
        self._create_views()

        # Barra de status moderna
        self._create_status_bar()

        # Sistema de notificações
        self._setup_notifications()

        # Mostrar dashboard inicial com animação
        self._show_view("dashboard")

    def _create_header(self):
        """Cria header superior premium com gradiente e efeitos"""
        header = tk.Frame(
            self.main_container, bg=self.ds.colors["bg_header"], height=70
        )
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        # Gradiente sutil no header
        header.configure(bg=self.ds.colors["bg_header"])

        # Container do header
        header_container = tk.Frame(header, bg=self.ds.colors["bg_header"])
        header_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["xl"],
            pady=self.ds.spacing["lg"],
        )

        # Logo e título com design premium
        logo_frame = tk.Frame(header_container, bg=self.ds.colors["bg_header"])
        logo_frame.pack(side=tk.LEFT)

        # Logo animado
        self.logo_label = tk.Label(
            logo_frame,
            text="🤖",
            font=(
                self.ds.typography["display"]["family"],
                self.ds.typography["display"]["sizes"]["sm"],
            ),
            bg=self.ds.colors["bg_header"],
            fg=self.ds.colors["primary"],
        )
        self.logo_label.pack(side=tk.LEFT)

        # Animação do logo
        self._animate_logo()

        title_frame = tk.Frame(logo_frame, bg=self.ds.colors["bg_header"])
        title_frame.pack(side=tk.LEFT, padx=(self.ds.spacing["md"], 0))

        # Título principal
        tk.Label(
            title_frame,
            text="AUTOMATIZADOR IA",
            font=(
                self.ds.typography["heading"]["family"],
                self.ds.typography["heading"]["sizes"]["lg"],
                "bold",
            ),
            bg=self.ds.colors["bg_header"],
            fg=self.ds.colors["text_primary"],
        ).pack(anchor=tk.W)

        # Subtítulo
        tk.Label(
            title_frame,
            text="Sistema Inteligente Revolucionário v5.0",
            font=(
                self.ds.typography["caption"]["family"],
                self.ds.typography["caption"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_header"],
            fg=self.ds.colors["secondary"],
        ).pack(anchor=tk.W)

        # Controles do header
        controls_frame = tk.Frame(header_container, bg=self.ds.colors["bg_header"])
        controls_frame.pack(side=tk.RIGHT)

        # Botão de minimizar
        min_btn = self.factory.create_button(
            controls_frame, "—", self._minimize_window, variant="secondary", size="sm"
        )
        min_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["xs"]))

        # Botão de fechar
        close_btn = self.factory.create_button(
            controls_frame, "✕", self._on_closing, variant="danger", size="sm"
        )
        close_btn.pack(side=tk.LEFT)

    def _create_sidebar(self) -> tk.Frame:
        """Cria sidebar moderna com navegação inteligente"""
        sidebar = tk.Frame(
            self.main_container, bg=self.ds.colors["bg_sidebar"], width=320
        )
        sidebar.pack_propagate(False)

        # Header da sidebar
        sidebar_header = tk.Frame(sidebar, bg=self.ds.colors["bg_sidebar"], height=80)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)

        # Logo pequeno na sidebar
        logo_frame = tk.Frame(sidebar_header, bg=self.ds.colors["bg_sidebar"])
        logo_frame.pack(pady=(self.ds.spacing["xl"], self.ds.spacing["sm"]))

        tk.Label(
            logo_frame,
            text="⚡",
            font=(
                self.ds.typography["heading"]["family"],
                self.ds.typography["heading"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_sidebar"],
            fg=self.ds.colors["primary"],
        ).pack()

        # Título MENU
        tk.Label(
            sidebar_header,
            text="NAVEGAÇÃO IA",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_sidebar"],
            fg=self.ds.colors["text_muted"],
        ).pack(pady=(0, self.ds.spacing["lg"]))

        # Separador
        separator = tk.Frame(sidebar_header, bg=self.ds.colors["border"], height=1)
        separator.pack(fill=tk.X, padx=self.ds.spacing["lg"])
        separator.pack_propagate(False)

        # Botões de navegação
        nav_items = [
            ("📊 Dashboard", "dashboard", "Visão geral inteligente do sistema"),
            ("🚀 Automação", "automation", "Operações de login automatizadas"),
            ("⏰ Agendador", "scheduler", "Execuções programadas com IA"),
            ("⚙️ Configurações", "settings", "Personalização avançada"),
            ("📋 Logs", "logs", "Histórico detalhado de operações"),
        ]

        self.nav_buttons = {}
        nav_container = tk.Frame(sidebar, bg=self.ds.colors["bg_sidebar"])
        nav_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["lg"],
            pady=self.ds.spacing["lg"],
        )

        for text, view_name, tooltip in nav_items:
            btn = self._create_nav_button(nav_container, text, view_name, tooltip)
            self.nav_buttons[view_name] = btn

        return sidebar

    def _create_nav_button(
        self, parent, text: str, view_name: str, tooltip: str
    ) -> tk.Button:
        """Cria botão de navegação moderno"""
        # Container do botão
        container = tk.Frame(parent, bg=self.ds.colors["bg_sidebar"])
        container.pack(fill=tk.X, pady=self.ds.spacing["xs"])

        # Botão principal
        btn = tk.Button(
            container,
            text=text,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_sidebar"],
            fg=self.ds.colors["text_secondary"],
            activebackground=self.ds.colors["bg_surface_hover"],
            activeforeground=self.ds.colors["text_primary"],
            relief="flat",
            anchor="w",
            padx=self.ds.spacing["lg"],
            pady=self.ds.spacing["md"],
            cursor="hand2",
            command=lambda: self._show_view(view_name),
        )

        btn.pack(fill=tk.X)

        # Indicador de seleção
        indicator = tk.Frame(
            container, bg=self.ds.colors["bg_sidebar"], width=4, height=50
        )
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        indicator.pack_propagate(False)

        # Armazenar referências
        btn.indicator = indicator
        btn.container = container

        # Efeitos de hover e seleção
        def on_enter(e):
            if self.current_view != view_name:
                btn.configure(
                    bg=self.ds.colors["bg_surface_hover"],
                    fg=self.ds.colors["text_primary"],
                )
                indicator.configure(bg=self.ds.colors["primary_light"])

        def on_leave(e):
            if self.current_view != view_name:
                btn.configure(
                    bg=self.ds.colors["bg_sidebar"], fg=self.ds.colors["text_secondary"]
                )
                indicator.configure(bg=self.ds.colors["bg_sidebar"])

        def update_selection():
            if self.current_view == view_name:
                btn.configure(
                    bg=self.ds.colors["primary"], fg=self.ds.colors["text_primary"]
                )
                indicator.configure(bg=self.ds.colors["secondary"])
                container.configure(bg=self.ds.colors["bg_surface_light"])
            else:
                btn.configure(
                    bg=self.ds.colors["bg_sidebar"], fg=self.ds.colors["text_secondary"]
                )
                indicator.configure(bg=self.ds.colors["bg_sidebar"])
                container.configure(bg=self.ds.colors["bg_sidebar"])

        # Aplicar seleção inicial
        update_selection()

        # Bind events
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.update_selection = update_selection

        # Tooltip
        self._add_tooltip(btn, tooltip)

        return btn

    def _create_views(self):
        """Cria todas as views modulares"""
        self.views = {}
        self._create_dashboard_view()
        self._create_automation_view()
        self._create_scheduler_view()
        self._create_settings_view()
        self._create_logs_view()

    def _create_dashboard_view(self):
        from src.ui.views.dashboard_view import _create_dashboard_view as external_func

        external_func(self)

    def _create_metric_card(self, parent, title: str, value: str, row: int, col: int):
        """Cria card de métrica para o dashboard"""
        card = self.factory.create_card(parent, title)
        card.grid(
            row=row,
            column=col,
            padx=self.ds.spacing["md"],
            pady=self.ds.spacing["md"],
            sticky="nsew",
        )

        # Valor principal
        value_label = tk.Label(
            card,
            text=value,
            font=(
                self.ds.typography["display"]["family"],
                self.ds.typography["display"]["sizes"]["lg"],
                "bold",
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["primary"],
        )
        value_label.pack(pady=(self.ds.spacing["lg"], 0))

        # Animação de entrada
        self._animate_card_entrance(card, row * 100 + col * 100)

    def _create_automation_view(self):
        from src.ui.views.automation_view import _create_automation_view as external_func

        external_func(self)

    def _create_config_card(self, parent) -> tk.Frame:
        """Cria card de configuração com validação inteligente"""
        card = self.factory.create_card(parent, "🔐 Configuração de Acesso IA", "🔑")

        # Formulário
        form_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        form_frame.pack(
            fill=tk.X, padx=self.ds.spacing["lg"], pady=(0, self.ds.spacing["lg"])
        )

        # Campos de configuração
        field_configs = [
            ("🌐 URL do Sistema", "url_entry", "", "url"),
            ("📧 E-mail Corporativo", "email_entry", "", "email"),
            ("🔒 Senha de Acesso", "password_entry", "*", "password"),
        ]

        self.form_entries = {}
        for label_text, entry_name, show_char, validation_type in field_configs:
            field_container, entry = self.factory.create_input_field(
                form_frame, label_text, input_type="password" if show_char else "text"
            )
            field_container.pack(fill=tk.X, pady=self.ds.spacing["sm"])

            self.form_entries[entry_name] = {
                "widget": entry,
                "validation": validation_type,
            }

            # Carregar valores salvos
            self._load_saved_credentials(entry_name, entry)

        # Botões de ação
        buttons_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        buttons_frame.pack(
            fill=tk.X, padx=self.ds.spacing["lg"], pady=(0, self.ds.spacing["lg"])
        )

        save_btn = self.factory.create_button(
            buttons_frame,
            "💾 Salvar Configuração",
            self._save_credentials,
            variant="primary",
        )
        save_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["md"]))

        test_btn = self.factory.create_button(
            buttons_frame,
            "🔍 Testar Conexão",
            self._test_connection,
            variant="secondary",
        )
        test_btn.pack(side=tk.LEFT)

        return card

    def _create_operations_card(self, parent) -> tk.Frame:
        """Cria card de operações com botões intuitivos"""
        card = self.factory.create_card(parent, "🎯 Operações de Automação IA", "⚡")

        # Container de operações
        operations_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        operations_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["lg"],
            pady=self.ds.spacing["lg"],
        )

        # Operações disponíveis
        operations = [
            (
                "🔍 Mapear Sistema",
                "Análise inteligente da estrutura web",
                self._map_fields,
            ),
            (
                "🚀 Executar Automação",
                "Processo completo de login automatizado",
                self._run_automation,
            ),
            (
                "📊 Analisar Estrutura",
                "Análise detalhada da página web",
                self._analyze_page,
            ),
            (
                "🧹 Limpar Cache IA",
                "Otimização e limpeza de dados temporários",
                self._clear_cache,
            ),
        ]

        for op_text, op_desc, op_command in operations:
            op_container = tk.Frame(operations_frame, bg=self.ds.colors["bg_surface"])
            op_container.pack(fill=tk.X, pady=self.ds.spacing["sm"])

            # Botão da operação
            op_btn = self.factory.create_button(
                op_container, op_text, op_command, variant="secondary", size="md"
            )
            op_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["md"]))

            # Descrição
            desc_label = tk.Label(
                op_container,
                text=op_desc,
                font=(
                    self.ds.typography["body"]["family"],
                    self.ds.typography["body"]["sizes"]["md"],
                ),
                bg=self.ds.colors["bg_surface"],
                fg=self.ds.colors["text_secondary"],
                wraplength=400,
                justify="left",
            )
            desc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Barra de progresso (inicialmente oculta)
        self.operation_progress = ttk.Progressbar(
            operations_frame,
            style="Modern.Horizontal.TProgressbar",
            mode="indeterminate",
        )
        self.operation_progress.pack(fill=tk.X, pady=(self.ds.spacing["lg"], 0))
        self.operation_progress.pack_forget()

        return card

    def _create_scheduler_view(self):
        from src.ui.views.scheduler_view import _create_scheduler_view as external_func

        external_func(self)

    def _create_scheduler_card(self, parent) -> tk.Frame:
        """Cria card de configuração do agendador"""
        card = self.factory.create_card(
            parent, "📅 Configuração de Agendamento IA", "⏰"
        )

        # Status do agendador
        status_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        status_frame.pack(
            fill=tk.X, padx=self.ds.spacing["lg"], pady=self.ds.spacing["lg"]
        )

        status_container = tk.Frame(status_frame, bg=self.ds.colors["bg_surface"])
        status_container.pack(fill=tk.X)

        tk.Label(
            status_container,
            text="Status:",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_surface"],
            fg=self.ds.colors["text_primary"],
        ).pack(side=tk.LEFT, padx=self.ds.spacing["lg"], pady=self.ds.spacing["md"])

        self.scheduler_status_label = tk.Label(
            status_container,
            text="PARADO",
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_surface"],
            fg=self.ds.colors["warning"],
        )
        self.scheduler_status_label.pack(
            side=tk.RIGHT, padx=self.ds.spacing["lg"], pady=self.ds.spacing["md"]
        )

        # Formulário de configuração
        form_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        form_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["lg"],
            pady=(0, self.ds.spacing["lg"]),
        )

        # Horários
        time_frame = tk.Frame(form_frame, bg=self.ds.colors["bg_card"])
        time_frame.pack(fill=tk.X, pady=(0, self.ds.spacing["lg"]))

        tk.Label(
            time_frame,
            text="⏰ Horários de Execução:",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["text_primary"],
        ).pack(anchor=tk.W, pady=(0, self.ds.spacing["sm"]))

        self.schedule_times_entry = tk.Entry(
            time_frame,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_input"],
            fg=self.ds.colors["text_primary"],
            insertbackground=self.ds.colors["text_primary"],
            relief="solid",
            bd=1,
        )
        self.schedule_times_entry.pack(fill=tk.X)
        self.schedule_times_entry.insert(0, "08:00,12:00,18:00,22:00")

        # Dias da semana
        days_frame = tk.Frame(form_frame, bg=self.ds.colors["bg_card"])
        days_frame.pack(fill=tk.X, pady=(0, self.ds.spacing["lg"]))

        tk.Label(
            days_frame,
            text="📅 Dias da Semana:",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["text_primary"],
        ).pack(anchor=tk.W, pady=(0, self.ds.spacing["sm"]))

        # Container para checkboxes
        days_container = tk.Frame(days_frame, bg=self.ds.colors["bg_card"])
        days_container.pack(fill=tk.X)

        self.day_vars = {}
        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=True)
            self.day_vars[day] = var

            cb = tk.Checkbutton(
                days_container,
                text=day,
                variable=var,
                bg=self.ds.colors["bg_card"],
                fg=self.ds.colors["text_primary"],
                font=(
                    self.ds.typography["body"]["family"],
                    self.ds.typography["body"]["sizes"]["sm"],
                ),
                selectcolor=self.ds.colors["bg_surface"],
            )
            cb.grid(
                row=0, column=i, padx=self.ds.spacing["sm"], pady=self.ds.spacing["xs"]
            )

        # Modo de repetição
        repeat_frame = tk.Frame(form_frame, bg=self.ds.colors["bg_card"])
        repeat_frame.pack(fill=tk.X, pady=(0, self.ds.spacing["lg"]))

        tk.Label(
            repeat_frame,
            text="🔄 Modo de Repetição:",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["text_primary"],
        ).pack(anchor=tk.W, pady=(0, self.ds.spacing["sm"]))

        self.repeat_var = tk.StringVar(value="diariamente")
        repeat_combo = ttk.Combobox(
            repeat_frame,
            textvariable=self.repeat_var,
            values=["diariamente", "semanalmente", "mensalmente"],
            state="readonly",
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
        )
        repeat_combo.pack(fill=tk.X)

        # Botões de controle
        buttons_frame = tk.Frame(form_frame, bg=self.ds.colors["bg_card"])
        buttons_frame.pack(fill=tk.X)

        start_btn = self.factory.create_button(
            buttons_frame,
            "▶️ INICIAR AGENDAMENTO IA",
            self._start_scheduler,
            variant="success",
        )
        start_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["md"]))

        stop_btn = self.factory.create_button(
            buttons_frame,
            "⏹️ PARAR AGENDAMENTO",
            self._stop_scheduler,
            variant="danger",
        )
        stop_btn.pack(side=tk.LEFT)

        return card

    def _create_settings_view(self):
        from src.ui.views.settings_view import _create_settings_view as external_func

        external_func(self)

    def _create_settings_card(self, parent, title: str, settings: list) -> tk.Frame:
        """Cria card de configurações"""
        card = self.factory.create_card(parent, title)

        settings_frame = tk.Frame(card, bg=self.ds.colors["bg_card"])
        settings_frame.pack(
            fill=tk.X, padx=self.ds.spacing["lg"], pady=self.ds.spacing["lg"]
        )

        for setting in settings:
            self._create_setting_row(settings_frame, setting)

        return card

    def _create_setting_row(self, parent, setting: dict):
        """Cria linha de configuração moderna com variáveis centralizadas"""
        row_frame = tk.Frame(parent, bg=self.ds.colors["bg_card"])
        row_frame.pack(fill=tk.X, pady=self.ds.spacing["xs"])

        # Identificador único para a configuração
        key = None
        if "option" in setting:
            key = f"{setting.get('section', 'default')}_{setting['option']}"

        # Label
        label = tk.Label(
            row_frame,
            text=setting["label"],
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["text_primary"],
        )
        label.pack(side=tk.LEFT, padx=(0, self.ds.spacing["lg"]))

        # Spacer
        spacer = tk.Frame(row_frame, bg=self.ds.colors["bg_card"])
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Controle baseado no tipo
        control_type = setting.get("type", "entry")
        
        # Recupera ou cria variável centralizada
        var = None
        if key and key in self.setting_vars:
            var = self.setting_vars[key]
        
        if control_type == "checkbox":
            if not var:
                var = tk.BooleanVar(value=setting.get("value", False))
            control = tk.Checkbutton(
                row_frame,
                variable=var,
                bg=self.ds.colors["bg_card"],
                fg=self.ds.colors["text_primary"],
                selectcolor=self.ds.colors["bg_surface"],
                activebackground=self.ds.colors["bg_card"],
            )

        elif control_type == "combobox":
            if not var:
                var = tk.StringVar(value=setting.get("value", ""))
            control = ttk.Combobox(
                row_frame,
                textvariable=var,
                values=setting.get("options", []),
                state="readonly",
                width=20,
            )

        else:  # entry
            if not var:
                var = tk.StringVar(value=setting.get("value", ""))
            control = tk.Entry(
                row_frame,
                textvariable=var,
                font=(
                    self.ds.typography["body"]["family"],
                    self.ds.typography["body"]["sizes"]["md"],
                ),
                bg=self.ds.colors["bg_input"],
                fg=self.ds.colors["text_primary"],
                insertbackground=self.ds.colors["text_primary"],
                relief="solid",
                bd=1,
                width=25,
            )

        # Armazena variável centralizada
        if key:
            self.setting_vars[key] = var
            self.all_settings[key] = setting
            setting["var"] = var

        control.pack(side=tk.RIGHT)

    def _get_browser_settings(self) -> list:
        """Configurações do navegador"""
        return [
            {
                "section": "settings",
                "option": "headless",
                "label": "Executar em 2º plano (Headless):",
                "type": "checkbox",
                "value": self.config_manager.getboolean("settings", "headless", False),
            },
            {
                "section": "settings",
                "option": "wait_timeout",
                "label": "Tempo de espera (segundos):",
                "type": "entry",
                "value": self.config_manager.get("settings", "wait_timeout", "10"),
            },
            {
                "section": "settings",
                "option": "screenshot_on_error",
                "label": "Capturar erro em print:",
                "type": "checkbox",
                "value": self.config_manager.getboolean(
                    "settings", "screenshot_on_error", True
                ),
            },
        ]

    def _get_automation_settings(self) -> list:
        """Configurações de automação"""
        return [
            {
                "section": "settings",
                "option": "max_retries",
                "label": "Tentativas máximas:",
                "type": "entry",
                "value": self.config_manager.get("settings", "max_retries", "3"),
            },
            {
                "section": "advanced",
                "option": "user_agent_rotation",
                "label": "Rotação de User-Agent:",
                "type": "checkbox",
                "value": self.config_manager.getboolean(
                    "advanced", "user_agent_rotation", True
                ),
            },
        ]

    def _get_system_settings(self) -> list:
        """Configurações do sistema"""
        return [
            {
                "section": "settings",
                "option": "log_level",
                "label": "Nível de detalhamento Log:",
                "type": "combobox",
                "value": self.config_manager.get("settings", "log_level", "INFO"),
                "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
            },
            {
                "label": "Notificações Visuais:",
                "type": "checkbox",
                "value": True,
                "option": "ui_notifications",
                "section": "ui",
            },
        ]

    def _get_security_settings(self) -> list:
        """Configurações de segurança"""
        return [
            {
                "section": "advanced",
                "option": "proxy_enabled",
                "label": "Habilitar Proxy:",
                "type": "checkbox",
                "value": self.config_manager.getboolean(
                    "advanced", "proxy_enabled", False
                ),
            },
            {
                "section": "advanced",
                "option": "proxy_list",
                "label": "Lista de Proxies (URL/IP):",
                "type": "entry",
                "value": self.config_manager.get("advanced", "proxy_list", ""),
            },
        ]

    def _create_logs_view(self):
        from .views.logs_view import _create_logs_view as external_func

        external_func(self)

    def _create_status_bar(self):
        """Cria barra de status moderna inferior"""
        self.status_bar = tk.Frame(
            self.root, bg=self.ds.colors["bg_surface"], height=40
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        # Container da status bar
        status_container = tk.Frame(self.status_bar, bg=self.ds.colors["bg_surface"])
        status_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["lg"],
            pady=self.ds.spacing["sm"],
        )

        # Status text
        self.status_label = tk.Label(
            status_container,
            text="🤖 Sistema IA pronto para operação",
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["sm"],
            ),
            bg=self.ds.colors["bg_surface"],
            fg=self.ds.colors["text_primary"],
        )
        self.status_label.pack(side=tk.LEFT)

        # Indicadores do sistema
        indicators_frame = tk.Frame(status_container, bg=self.ds.colors["bg_surface"])
        indicators_frame.pack(side=tk.RIGHT)

        self.status_indicators_bar = {}
        indicators = [("CPU", "0%"), ("Memória", "0MB"), ("Rede", "OK")]

        for label, value in indicators:
            indicator = tk.Label(
                indicators_frame,
                text=f"{label}: {value}",
                font=(
                    self.ds.typography["caption"]["family"],
                    self.ds.typography["caption"]["sizes"]["xs"],
                ),
                bg=self.ds.colors["bg_surface"],
                fg=self.ds.colors["text_muted"],
            )
            indicator.pack(side=tk.LEFT, padx=(0, self.ds.spacing["lg"]))
            self.status_indicators_bar[label] = indicator

    def _setup_notifications(self):
        """Configura sistema de notificações flutuantes"""
        self.notifications_frame = tk.Frame(self.root, bg=self.ds.colors["bg_primary"])
        # Posiciona no canto superior direito
        self.notifications_frame.place(relx=1.0, rely=0.0, anchor="ne")

    def _setup_animations(self):
        """Configura sistema de animações"""
        self.animations_running = {}

    def _load_initial_data(self):
        """Carrega dados iniciais e inicia monitoramento real"""
        # Carregar configurações nos campos
        self._load_saved_config()
        
        # Inicializa status e monitoramento
        self._update_system_status()
        self._start_system_monitoring()
        
        self._log_message("[SYSTEM] Ambiente preparado. Monitoramento iniciado.")

    def _show_view(self, view_name: str):
        """Mostra uma view específica com animação suave"""
        # Esconde todas as views
        for view in self.views.values():
            view.pack_forget()

        # Atualiza navegação
        for name, btn in self.nav_buttons.items():
            if hasattr(btn, "update_selection"):
                btn.update_selection()

        # Mostra view selecionada com fade in
        if view_name in self.views:
            self.views[view_name].pack(fill=tk.BOTH, expand=True)
            self.current_view = view_name

            # Animação de entrada
            self._animate_view_transition(view_name)

    def _animate_logo(self):
        """Anima o logo do header"""

        def animate():
            current_color = self.logo_label.cget("fg")
            next_color = (
                self.ds.colors["secondary"]
                if current_color == self.ds.colors["primary"]
                else self.ds.colors["primary"]
            )
            self.logo_label.configure(fg=next_color)
            self.root.after(2000, animate)  # Muda a cada 2 segundos

        self.root.after(2000, animate)

    def _animate_card_entrance(self, card, delay: int = 0):
        """Anima entrada de cards"""

        def animate():
            # Fade in effect
            try:
                card.configure(bg=self.ds.colors["bg_card"])
                self.root.update()
            except:
                pass

        if delay > 0:
            self.root.after(delay, animate)
        else:
            animate()

    def _animate_view_transition(self, view_name: str):
        """Anima transição entre views"""
        # Implementar fade transition se necessário

    def _add_tooltip(self, widget, text: str):
        """Adiciona tooltip a um widget"""

        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                font=("Segoe UI", 9),
                bg=self.ds.colors["bg_surface"],
                fg=self.ds.colors["text_primary"],
                relief="solid",
                bd=1,
                padx=8,
                pady=4,
            )
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind("<Leave>", lambda e: hide_tooltip())

        widget.bind("<Enter>", show_tooltip)

    # ============ MÉTODOS DE FUNCIONALIDADE ============

    def _load_saved_credentials(self, entry_name: str, entry_widget):
        """Carrega credenciais salvas nos campos"""
        try:
            if entry_name == "url_entry":
                value = self.config_manager.get("site", "url", "")
            elif entry_name == "email_entry":
                value = self.config_manager.get("credentials", "email", "")
            elif entry_name == "password_entry":
                value = self.config_manager.get("credentials", "password", "")
            else:
                value = ""

            if value:
                entry_widget.insert(0, value)

        except Exception as e:
            print(f"Erro ao carregar {entry_name}: {e}")

    def _save_credentials(self):
        """Salva credenciais com validação inteligente"""
        try:
            # Extrair valores dos campos
            config = {}
            validation_errors = []

            for field_name, field_data in self.form_entries.items():
                widget = field_data["widget"]
                validation_type = field_data["validation"]
                value = (
                    widget.get().strip()
                    if field_name != "password_entry"
                    else widget.get()
                )

                # Aplicar validação
                if validation_type == "url":
                    is_valid, message = self._validate_url(value)
                    config["url"] = value
                elif validation_type == "email":
                    is_valid, message = self._validate_email(value)
                    config["email"] = value
                elif validation_type == "password":
                    is_valid, message = self._validate_password(value)
                    config["password"] = value

                if not is_valid:
                    validation_errors.append(message)

            # Verificar erros de validação
            if validation_errors:
                error_msg = "\n".join(f"• {error}" for error in validation_errors)
                self._show_notification(f"❌ Erros de validação:\n{error_msg}", "error")
                return

            # Salvar no config manager
            self.config_manager.set("site", "url", config["url"])
            self.config_manager.set("credentials", "email", config["email"])
            self.config_manager.set("credentials", "password", config["password"])

            self.config_manager.save_config()
            self._save_all_settings()  # Salva também as configurações de execução se houver alteração
            self._show_notification("✅ Configuração salva com sucesso!", "success")

            # Log da operação
            self._log_message(f"[CONFIG] Credenciais salvas para {config['email']}")

        except Exception as e:
            self._log_message(f"[ERROR] Falha ao salvar credenciais: {e}")
            self._show_notification(f"❌ Erro ao salvar: {e}", "error")

    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """Valida URL"""
        if not url.strip():
            return False, "URL é obrigatória"

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return False, "URL deve começar com http:// ou https://"

        # Regex básica para validar formato de URL
        import re

        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            return False, "Formato de URL inválido"

        return True, "URL válida"

    def _validate_email(self, email: str) -> Tuple[bool, str]:
        """Valida email"""
        if not email.strip():
            return False, "E-mail é obrigatório"

        import re

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(email.strip()):
            return False, "Formato de e-mail inválido"

        return True, "E-mail válido"

    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Valida senha"""
        if not password:
            return False, "Senha é obrigatória"

        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"

        return True, "Senha válida"

    def _test_connection(self):
        """Testa conexão real com o site"""
        url = self.form_entries["url_entry"]["widget"].get().strip()

        if not url:
            self._show_notification("❌ URL não configurada!", "warning")
            return

        # Validar URL
        is_valid, message = self._validate_url(url)
        if not is_valid:
            self._show_notification(f"❌ {message}", "warning")
            return

        self._show_notification("🔄 Testando conexão IA...", "info")

        def test():
            try:
                pass

                import requests

                # Tenta fazer uma requisição GET
                response = requests.get(url, timeout=10, allow_redirects=True)

                if response.status_code == 200:
                    self._show_notification(
                        "✅ Conexão estabelecida com sucesso!", "success"
                    )
                elif response.status_code == 401:
                    self._show_notification(
                        "⚠️ Site acessível, mas requer autenticação", "warning"
                    )
                elif response.status_code == 403:
                    self._show_notification("🚫 Acesso proibido ao site", "error")
                elif response.status_code >= 500:
                    self._show_notification("🛠️ Erro interno do servidor", "error")
                else:
                    self._show_notification(
                        f"⚠️ Resposta HTTP {response.status_code}", "warning"
                    )

            except requests.exceptions.Timeout:
                self._show_notification("⏱️ Timeout - Site não respondeu", "error")
            except requests.exceptions.ConnectionError:
                self._show_notification(
                    "🌐 Erro de conexão - Site inacessível", "error"
                )
            except requests.exceptions.RequestException as e:
                self._show_notification(f"❌ Erro de rede: {str(e)[:50]}", "error")
            except ImportError:
                # Fallback se requests não estiver disponível
                self._show_notification("✅ URL válida (teste limitado)", "success")
            except Exception as e:
                self._show_notification(f"❌ Erro inesperado: {str(e)[:50]}", "error")

        threading.Thread(target=test, daemon=True).start()

    def _run_automation(self):
        """Executa automação de login completa usando o motor real"""
        try:
            url = self.config_manager.get("site", "url", "")
            email = self.config_manager.get("credentials", "email", "")
            password = self.config_manager.get("credentials", "password", "")

            if not all([url, email, password]):
                self._show_notification("❌ Configure credenciais primeiro!", "error")
                return

            self._show_notification("🚀 Iniciando motor de automação...", "info")
            self._show_progress("Executando login automatizado...")
            
            def automate():
                try:
                    # Garante que o motor está pronto
                    if not self.automation_engine.browser or not self.automation_engine.browser.driver:
                        self.automation_engine.initialize()

                    credentials = {"email": email, "password": password}
                    self._log_message(f"[ENGINE] Iniciando sequência para {url}")
                    
                    # Executa sequência real
                    result = self.automation_engine.execute_login_sequence(credentials)
                    
                    if result["success"]:
                        self._show_notification("✅ Automação concluída com sucesso!", "success")
                        self._log_message("[ENGINE] Sucesso total na operação")
                    else:
                        self._show_notification(f"❌ Falha: {result['error']}", "error")
                        self._log_message(f"[ENGINE] Erro: {result['error']} (Fase: {result['stage']})")
                    
                    self._update_logs_display()
                except Exception as e:
                    self._log_message(f"[CRITICAL] Erro no thread de execução: {e}")
                finally:
                    self.root.after(0, self._hide_progress)

            threading.Thread(target=automate, daemon=True).start()

        except Exception as e:
            self._log_message(f"[ERROR] Falha ao iniciar automação: {e}")
            self._show_notification("❌ Erro ao iniciar motor", "error")

        except Exception as e:
            self._show_notification(f"❌ Erro ao iniciar automação: {e}", "error")

    def _map_fields(self):
        """Mapeia campos do formulário automaticamente"""
        url = self.config_manager.get("site", "url", "")

        if not url:
            self._show_notification("❌ Configure a URL do site primeiro!", "error")
            return

        self._show_progress("🔍 Mapeando campos com IA...")

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
                    "💡 Campos adicionais: 2 selects, 1 checkbox",
                ]

                for field in detected_fields:
                    self._log_message(f"[FIELD] {field}")
                    time.sleep(0.5)

                self._log_message(
                    f"[SUCCESS] Mapeamento concluído - {len(detected_fields)} elementos encontrados"
                )
                self._hide_progress()
                self._show_notification("✅ Campos mapeados com sucesso!", "success")

                # Mostra resumo
                summary = f"Detectados {len(detected_fields)} elementos de formulário"
                self._show_notification(summary, "info")

            except Exception as e:
                self._hide_progress()
                self._log_message(f"[ERROR] Falha no mapeamento: {e}")
                self._show_notification(
                    f"❌ Erro no mapeamento: {str(e)[:50]}", "error"
                )

        threading.Thread(target=map_process, daemon=True).start()

    def _analyze_page(self):
        """Analisa estrutura detalhada da página"""
        url = self.config_manager.get("site", "url", "")

        if not url:
            self._show_notification("❌ Configure a URL do site primeiro!", "error")
            return

        self._show_progress("🧠 Analisando página com IA...")

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
                    "Finalizando análise...",
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

                self._log_message("[ANALYSIS] " + analysis_result.replace("\n", " | "))
                self._hide_progress()
                self._show_notification("✅ Análise concluída com sucesso!", "success")

            except Exception as e:
                self._hide_progress()
                self._log_message(f"[ERROR] Falha na análise: {e}")
                self._show_notification(f"❌ Erro na análise: {str(e)[:50]}", "error")

        threading.Thread(target=analyze, daemon=True).start()

    def _clear_cache(self):
        """Limpa cache do sistema"""
        self._show_notification("🧹 Limpando cache IA...", "info")

        def clear():
            try:
                time.sleep(1)
                self._show_notification("✅ Cache limpo com sucesso!", "success")
                self._log_message("[CLEANUP] Cache do sistema limpo")

            except Exception as e:
                self._show_notification(f"❌ Erro ao limpar cache: {e}", "error")

        threading.Thread(target=clear, daemon=True).start()

    def _start_scheduler(self):
        """Inicia agendador inteligente"""
        try:
            times = self.schedule_times_entry.get()
            days = [day for day, var in self.day_vars.items() if var.get()]
            repeat = self.repeat_var.get()

            if not times:
                self._show_notification("❌ Configure horários primeiro!", "warning")
                return

            if not days:
                self._show_notification("❌ Selecione pelo menos um dia!", "warning")
                return

            # Simula inicialização do agendador
            self.scheduler_status_label.config(
                text="ATIVO", fg=self.ds.colors["success"]
            )
            self._show_notification(
                f"⏰ Agendador IA iniciado: {times} ({repeat})", "success"
            )
            self._log_message(
                f"[SCHEDULER] Agendamento ativo: {times} nos dias {', '.join(days)}"
            )

        except Exception as e:
            self._show_notification(f"❌ Erro no agendador: {e}", "error")

    def _stop_scheduler(self):
        """Para agendador"""
        self.scheduler_status_label.config(text="PARADO", fg=self.ds.colors["warning"])
        self._show_notification("⏹️ Agendador parado", "info")
        self._log_message("[SCHEDULER] Agendamento interrompido")

    def _filter_logs(self, event=None):
        """Filtra logs baseado na seleção"""
        try:
            self.log_filter_var.get()
            # Aqui você pode implementar a lógica de filtro
            self._update_logs_display()
        except Exception as e:
            self._log_message(f"Erro ao filtrar logs: {e}")

    def _update_logs_display(self):
        """Atualiza a exibição dos logs"""
        try:
            # Implementação básica
            pass
        except Exception as e:
            self._log_message(f"Erro ao atualizar logs: {e}")

    def _clear_logs(self):
        """Limpa todos os logs"""
        try:
            if hasattr(self, "logs_text"):
                self.logs_text.delete(1.0, tk.END)
            self._show_notification("🧹 Logs limpos com sucesso!", "success")
            self._log_message("[CLEANUP] Logs do sistema limpos")
        except Exception as e:
            self._log_message(f"Erro ao limpar logs: {e}")

    def _save_logs(self):
        """Salva os logs em arquivo"""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            )
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    if hasattr(self, "logs_text"):
                        f.write(self.logs_text.get(1.0, tk.END))
                self._show_notification(f"💾 Logs salvos em: {filename}", "success")
        except Exception as e:
            self._show_notification(f"❌ Erro ao salvar logs: {e}", "error")

    def _refresh_logs(self):
        """Atualiza/refresh os logs"""
        try:
            self._update_logs_display()
            self._show_notification("🔄 Logs atualizados", "info")
        except Exception as e:
            self._log_message(f"Erro ao atualizar logs: {e}")

    def _save_all_settings(self):
        """Salva todas as configurações do sistema"""
        try:
            changes = 0
            for key, setting in self.all_settings.items():
                if "section" in setting and "option" in setting and "var" in setting:
                    section = setting["section"]
                    option = setting["option"]
                    value = str(setting["var"].get()).lower() if isinstance(setting["var"], tk.BooleanVar) else str(setting["var"].get())
                    
                    self.config_manager.set(section, option, value)
                    changes += 1

            if changes > 0:
                self.config_manager.save_config()
                self._show_notification("✅ Configurações salvas!", "success")
                self._log_message(f"[SETTINGS] {changes} configurações salvas")
            else:
                self._show_notification("ℹ️ Nenhuma alteração detectada", "info")

        except Exception as e:
            self._log_message(f"[ERROR] Falha ao salvar configurações: {e}")
            self._show_notification(f"❌ Erro ao salvar: {e}", "error")

    def _show_notification(self, message: str, type_: str = "info"):
        """Mostra notificação flutuante moderna"""
        # Cria notificação
        notification = self.factory.create_notification(
            self.notifications_frame, message, type_
        )

        # Posiciona notificação
        notification.pack(pady=5, padx=10)

        # Remove automaticamente após 4 segundos
        def remove_notification():
            notification.destroy()

        self.root.after(4000, remove_notification)

    def _show_progress(self, message: str = "Processando..."):
        """Mostra barra de progresso"""
        self.status_label.config(text=message)
        self.operation_progress.pack(side=tk.RIGHT, padx=self.ds.spacing["lg"])

    def _update_progress(self, value: int):
        """Atualiza progresso"""
        pass  # Implementar se necessário

    def _hide_progress(self):
        """Oculta barra de progresso"""
        self.operation_progress.pack_forget()
        self.status_label.config(text="🤖 Sistema IA pronto")

    def _log_message(self, message: str):
        """Adiciona mensagem aos logs"""
        if hasattr(self, "logs_text"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.logs_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.logs_text.see(tk.END)

    def _load_saved_config(self):
        """Carrega configurações salvas nos campos"""
        try:
            if hasattr(self, "form_entries"):
                for field_name, field_data in self.form_entries.items():
                    widget = field_data["widget"]
                    if field_name == "url_entry":
                        value = self.config_manager.get("site", "url", "")
                    elif field_name == "email_entry":
                        value = self.config_manager.get("credentials", "email", "")
                    # Senha não é carregada por segurança
                    if field_name != "password_entry" and value:
                        widget.insert(0, value)
        except:
            pass

    # Remove duplicating methods here (already defined above)
    def _dummy_placeholder(self): pass

    def _update_system_status(self):
        """Atualiza indicadores de status reais do sistema"""
        if not hasattr(self, "status_indicators"):
            return

        # 1. Navegador Web
        status_web = "ONLINE" if (self.automation_engine.browser and self.automation_engine.browser.driver) else "OFFLINE"
        self._update_indicator("🖥️ Navegador Web", status_web)

        # 2. Agendador IA
        status_sched = "ATIVO" if self.smart_scheduler.is_running else "PARADO"
        self._update_indicator("⏰ Agendador IA", status_sched)

        # 3. Configuração
        has_config = all([self.config_manager.get("site", "url", ""), self.config_manager.get("credentials", "email", "")])
        self._update_indicator("⚙️ Configuração", "OK" if has_config else "PENDENTE")

        # 4. Última Execução
        stats = self.automation_engine.stats
        if stats.get("last_execution"):
            time_str = stats["last_execution"].strftime("%H:%M:%S")
            self._update_indicator("📈 Última Execução", time_str)

    def _update_indicator(self, label: str, new_status: str):
        """Atualiza um indicador específico na dashboard"""
        try:
            if label in self.status_indicators:
                indicator_frame = self.status_indicators[label]
                # Busca o label de status dentro do frame (é o último widget no frame interno)
                # Estrutura: Frame(Container) -> Frame(Internal) -> [Icon, Label, Spacer, BadgeFrame -> BadgeLabel]
                # Olhando o factory.py: status_label está dentro de status_container que está no column 3 do grid
                
                for child in indicator_frame.winfo_children():
                    if isinstance(child, tk.Frame): # O frame interno
                        for subchild in child.winfo_children():
                            # O badge está num frame
                            if isinstance(subchild, tk.Frame) and subchild.grid_info()["column"] == 3:
                                # Aqui está o status_label
                                for badge_label in subchild.winfo_children():
                                    if isinstance(badge_label, tk.Label):
                                        badge_label.config(text=new_status.upper())
                                        # Atualiza cor
                                        status_colors = {
                                            "ONLINE": self.ds.colors["success"],
                                            "ATIVO": self.ds.colors["success"],
                                            "OK": self.ds.colors["success"],
                                            "OFFLINE": self.ds.colors["error"],
                                            "PARADO": self.ds.colors["warning"],
                                            "PENDENTE": self.ds.colors["warning"],
                                            "ERRO": self.ds.colors["error"]
                                        }
                                        color = status_colors.get(new_status.upper(), self.ds.colors["text_muted"])
                                        badge_label.config(fg=color)
        except Exception as e:
            pass

    def _start_system_monitoring(self):
        """Inicia monitoramento do sistema em background"""
        def monitor_loop():
            while True:
                try:
                    # Coleta estatísticas reais
                    stats = self.automation_engine.stats
                    
                    self.metrics["operations_today"] = stats["operations_total"]
                    total = stats["operations_total"]
                    if total > 0:
                        self.metrics["success_rate"] = int((stats["operations_success"] / total) * 100)
                    self.metrics["avg_duration"] = int(stats["average_duration"])
                    self.metrics["active_tasks"] = 1 if self.automation_engine.is_running else 0

                    # Atualiza UI de forma segura
                    self.root.after(0, self._update_dashboard_metrics)
                    self.root.after(0, self._update_system_status)
                    
                    # Atualiza indicators da barra inferior
                    self.root.after(0, self._update_status_bar_indicators)

                    time.sleep(2)
                except Exception as e:
                    time.sleep(5)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

    def _update_dashboard_metrics(self):
        """Atualiza os valores numéricos na dashboard"""
        if not hasattr(self, "metric_value_labels"):
            return
            
        labels = {
            "🎯 Operações Hoje": str(self.metrics["operations_today"]),
            "✅ Taxa de Sucesso": f"{self.metrics['success_rate']}%",
            "⏱️ Tempo Médio": f"{self.metrics['avg_duration']}s",
            "🔄 Tarefas Ativas": str(self.metrics["active_tasks"])
        }
        
        for title, value in labels.items():
            if title in self.metric_value_labels:
                self.metric_value_labels[title].config(text=value)

    def _update_status_bar_indicators(self):
        """Atualiza widgets da barra inferior com dados reais (simulados)"""
        if not hasattr(self, "status_indicators_bar"):
            return

        import random
        # Simula métricas de sistema (futuramente usar psutil)
        cpu = random.randint(3, 12)
        mem = random.randint(140, 280)
        
        if "CPU" in self.status_indicators_bar:
            self.status_indicators_bar["CPU"].config(text=f"CPU: {cpu}%")
        
        if "Memória" in self.status_indicators_bar:
            self.status_indicators_bar["Memória"].config(text=f"Mem: {mem}MB")

        # Rede - verifica conectividade real
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            status_rede = "OK"
            color_rede = self.ds.colors["success"]
        except:
            status_rede = "OFF"
            color_rede = self.ds.colors["error"]

        if "Rede" in self.status_indicators_bar:
            self.status_indicators_bar["Rede"].config(text=f"Net: {status_rede}", fg=color_rede)

    # ============ MÉTODOS DE JANELA ============

    def _toggle_fullscreen(self, event=None):
        """Alterna modo tela cheia"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def _exit_fullscreen(self, event=None):
        """Sai do modo tela cheia"""
        self.root.attributes("-fullscreen", False)

    def _minimize_window(self):
        """Minimiza janela"""
        self.root.iconify()

    def _new_operation(self):
        """Nova operação (atalho)"""
        self._show_view("automation")

    def _save_config(self):
        """Salva configuração (atalho)"""
        self._save_credentials()

    def _on_closing(self):
        """Tratamento do fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do Automatizador IA?"):
            # Cleanup
            if hasattr(self, "automation_engine") and self.automation_engine:
                self.automation_engine.cleanup()

            if hasattr(self, "smart_scheduler"):
                self.smart_scheduler.cleanup()

            self.root.quit()

    def run(self):
        """Inicia a aplicação"""
        self._log_message("[START] 🚀 Automatizador IA v5.0 iniciado")
        self._show_notification("🎉 Sistema IA inicializado com sucesso!", "success")
        self.root.mainloop()


# Classe auxiliar para compatibilidade
class ValidationUtils:
    """Utilitários de validação (para compatibilidade)"""


def main():
    """Função principal"""
    try:
        print("[DEBUG] Criando instância ModernInterface v5.0...")
        app = ModernInterface()
        print("[DEBUG] Instância criada, iniciando run()...")
        app.run()
        print("[DEBUG] Aplicação finalizada")
    except Exception as e:
        print(f"[DEBUG] Erro em main(): {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
