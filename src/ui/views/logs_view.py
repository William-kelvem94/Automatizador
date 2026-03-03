import tkinter as tk
from tkinter import scrolledtext, ttk


def _create_logs_view(self):
    """Cria view de logs com interface moderna"""
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
        text="📋 Centro de Logs IA",
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
        text="Histórico inteligente de operações e diagnósticos",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["lg"],
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["text_secondary"],
    ).pack(anchor=tk.W, pady=(self.ds.spacing["xs"], 0))

    # Container de logs
    logs_container = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    logs_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=(0, self.ds.spacing["xl"]),
    )

    # Barra de ferramentas
    toolbar = tk.Frame(logs_container, bg=self.ds.colors["bg_card"], height=60)
    toolbar.pack(fill=tk.X)
    toolbar.pack_propagate(False)

    toolbar_container = tk.Frame(toolbar, bg=self.ds.colors["bg_card"])
    toolbar_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["lg"],
        pady=self.ds.spacing["md"],
    )

    # Filtros
    filter_frame = tk.Frame(toolbar_container, bg=self.ds.colors["bg_card"])
    filter_frame.pack(side=tk.LEFT)

    tk.Label(
        filter_frame,
        text="🔍 Filtros IA:",
        font=(
            self.ds.typography["label"]["family"],
            self.ds.typography["label"]["sizes"]["md"],
            "bold",
        ),
        bg=self.ds.colors["bg_card"],
        fg=self.ds.colors["text_primary"],
    ).pack(side=tk.LEFT, padx=(0, self.ds.spacing["md"]))

    self.log_filter_var = tk.StringVar(value="todos")
    filter_combo = ttk.Combobox(
        filter_frame,
        textvariable=self.log_filter_var,
        values=["todos", "erros", "avisos", "sucessos", "info"],
        state="readonly",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["md"],
        ),
        width=12,
    )
    filter_combo.pack(side=tk.LEFT, padx=(0, self.ds.spacing["lg"]))
    filter_combo.bind("<<ComboboxSelected>>", self._filter_logs)

    # Botões de ação
    buttons_frame = tk.Frame(toolbar_container, bg=self.ds.colors["bg_card"])
    buttons_frame.pack(side=tk.RIGHT)

    clear_btn = self.factory.create_button(
        buttons_frame, "🧹 Limpar", self._clear_logs, variant="secondary", size="sm"
    )
    clear_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["xs"]))

    save_btn = self.factory.create_button(
        buttons_frame, "💾 Salvar", self._save_logs, variant="secondary", size="sm"
    )
    save_btn.pack(side=tk.LEFT, padx=(0, self.ds.spacing["xs"]))

    refresh_btn = self.factory.create_button(
        buttons_frame,
        "🔄 Atualizar",
        self._refresh_logs,
        variant="primary",
        size="sm",
    )
    refresh_btn.pack(side=tk.LEFT)

    # Área de logs
    logs_frame = tk.Frame(logs_container, bg=self.ds.colors["bg_card"])
    logs_frame.pack(fill=tk.BOTH, expand=True, pady=(self.ds.spacing["md"], 0))

    # Text area com syntax highlighting
    self.logs_text = scrolledtext.ScrolledText(
        logs_frame,
        font=("Consolas", 10),
        bg=self.ds.colors["bg_surface"],
        fg=self.ds.colors["text_primary"],
        insertbackground=self.ds.colors["text_primary"],
        selectbackground=self.ds.colors["primary"],
        relief="flat",
        padx=self.ds.spacing["md"],
        pady=self.ds.spacing["md"],
    )
    self.logs_text.pack(fill=tk.BOTH, expand=True)

    # Tags para colorização
    self.logs_text.tag_configure("error", foreground=self.ds.colors["error"])
    self.logs_text.tag_configure("warning", foreground=self.ds.colors["warning"])
    self.logs_text.tag_configure("success", foreground=self.ds.colors["success"])
    self.logs_text.tag_configure("info", foreground=self.ds.colors["text_secondary"])

    self.views["logs"] = view
