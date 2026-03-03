import tkinter as tk


def _create_automation_view(self):
    """Cria view de automação com interface intuitiva"""
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
        text="🚀 Centro de Automação IA",
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
        text="Automatização inteligente de processos com IA avançada",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["lg"],
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["text_secondary"],
    ).pack(anchor=tk.W, pady=(self.ds.spacing["xs"], 0))

    # Container principal
    main_container = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    main_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=(0, self.ds.spacing["xl"]),
    )

    # Painel de configuração
    config_panel = tk.Frame(main_container, bg=self.ds.colors["bg_primary"])
    config_panel.pack(fill=tk.X, pady=(0, self.ds.spacing["xl"]))

    config_card = self._create_config_card(config_panel)
    config_card.pack(fill=tk.X)

    # Painel de operações
    operations_panel = tk.Frame(main_container, bg=self.ds.colors["bg_primary"])
    operations_panel.pack(fill=tk.BOTH, expand=True)

    operations_card = self._create_operations_card(operations_panel)
    operations_card.pack(fill=tk.BOTH, expand=True)

    self.views["automation"] = view
