import tkinter as tk


def _create_settings_view(self):
    """Cria view de configurações avançadas"""
    view = tk.Frame(self.content_area, bg=self.ds.colors["bg_primary"])

    # Header
    header_frame = tk.Frame(view, bg=self.ds.colors["bg_primary"], height=100)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)

    header_container = tk.Frame(header_frame, bg=self.ds.colors["bg_primary"])
    header_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=self.ds.spacing["xl"],
    )

    tk.Label(
        header_container,
        text="⚙️ Configurações Avançadas IA",
        font=(
            self.ds.typography["display"]["family"],
            self.ds.typography["display"]["sizes"]["lg"],
            "bold",
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["primary"],
    ).pack(anchor=tk.W)

    tk.Label(
        header_container,
        text="Personalização inteligente do sistema automatizado",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["lg"],
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["text_secondary"],
    ).pack(anchor=tk.W, pady=(self.ds.spacing["xs"], 0))

    # Container de configurações
    settings_container = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    settings_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=(0, self.ds.spacing["xl"]),
    )

    # Configurações organizadas em cards
    settings_cards = [
        ("🌐 Navegador IA", self._get_browser_settings()),
        ("🤖 Automação", self._get_automation_settings()),
        ("💻 Sistema", self._get_system_settings()),
        ("🔒 Segurança", self._get_security_settings()),
    ]

    for title, settings in settings_cards:
        card = self._create_settings_card(settings_container, title, settings)
        card.pack(fill=tk.X, pady=self.ds.spacing["md"])

    # Footer com botão de salvar
    footer_frame = tk.Frame(view, bg=self.ds.colors["bg_primary"], height=80)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
    footer_frame.pack_propagate(False)

    save_btn = self.factory.create_button(
        footer_frame,
        "💾 Salvar Todas as Configurações",
        self._save_all_settings,
        variant="primary",
        size="lg",
    )
    save_btn.pack(pady=self.ds.spacing["lg"])

    self.views["settings"] = view
