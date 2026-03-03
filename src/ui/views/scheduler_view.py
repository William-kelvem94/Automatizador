import tkinter as tk


def _create_scheduler_view(self):
    """Cria view do agendador inteligente"""
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
        text="⏰ Agendador Inteligente IA",
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
        text="Execuções programadas com inteligência artificial",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["lg"],
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["text_secondary"],
    ).pack(anchor=tk.W, pady=(self.ds.spacing["xs"], 0))

    # Painel de configuração
    config_panel = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    config_panel.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=(0, self.ds.spacing["xl"]),
    )

    scheduler_card = self._create_scheduler_card(config_panel)
    scheduler_card.pack(fill=tk.BOTH, expand=True)

    self.views["scheduler"] = view
