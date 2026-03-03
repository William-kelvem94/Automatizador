import tkinter as tk


def _create_dashboard_view(self):
    """Cria dashboard inteligente com métricas em tempo real"""
    view = tk.Frame(self.content_area, bg=self.ds.colors["bg_primary"])

    # Título com gradiente visual
    title_frame = tk.Frame(view, bg=self.ds.colors["bg_primary"], height=100)
    title_frame.pack(fill=tk.X)
    title_frame.pack_propagate(False)

    title_container = tk.Frame(title_frame, bg=self.ds.colors["bg_primary"])
    title_container.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=self.ds.spacing["xl"],
    )

    tk.Label(
        title_container,
        text="🎯 Dashboard Inteligente",
        font=(
            self.ds.typography["display"]["family"],
            self.ds.typography["display"]["sizes"]["lg"],
            "bold",
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["primary"],
    ).pack(anchor=tk.W)

    tk.Label(
        title_container,
        text="Visão geral em tempo real do sistema automatizado",
        font=(
            self.ds.typography["body"]["family"],
            self.ds.typography["body"]["sizes"]["lg"],
        ),
        bg=self.ds.colors["bg_primary"],
        fg=self.ds.colors["text_secondary"],
    ).pack(anchor=tk.W, pady=(self.ds.spacing["xs"], 0))

    # Grid de métricas
    metrics_frame = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    metrics_frame.pack(
        fill=tk.X, padx=self.ds.spacing["xl"], pady=(0, self.ds.spacing["xl"])
    )

    # Configurar grid responsivo
    metrics_frame.grid_columnconfigure(0, weight=1)
    metrics_frame.grid_columnconfigure(1, weight=1)
    metrics_frame.grid_columnconfigure(2, weight=1)
    metrics_frame.grid_columnconfigure(3, weight=1)

    # Cards de métricas
    self.metric_value_labels = {}

    _, lab1 = self._create_metric_card(
        metrics_frame,
        "🎯 Operações Hoje",
        str(self.metrics["operations_today"]),
        "",  # Ícone vazio ou passe um ícone se desejar
        0,
    )
    self.metric_value_labels["🎯 Operações Hoje"] = lab1

    _, lab2 = self._create_metric_card(
        metrics_frame,
        "✅ Taxa de Sucesso",
        f"{self.metrics['success_rate']}%",
        "",
        1,
    )
    self.metric_value_labels["✅ Taxa de Sucesso"] = lab2

    _, lab3 = self._create_metric_card(
        metrics_frame,
        "⏱️ Tempo Médio",
        f"{self.metrics['avg_duration']}s",
        "",
        2,
    )
    self.metric_value_labels["⏱️ Tempo Médio"] = lab3

    _, lab4 = self._create_metric_card(
        metrics_frame,
        "🔄 Tarefas Ativas",
        str(self.metrics["active_tasks"]),
        "",
        3,
    )
    self.metric_value_labels["🔄 Tarefas Ativas"] = lab4

    # Status do sistema
    status_frame = tk.Frame(view, bg=self.ds.colors["bg_primary"])
    status_frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=self.ds.spacing["xl"],
        pady=(0, self.ds.spacing["xl"]),
    )

    status_card = self.factory.create_card(
        status_frame, "📊 Status do Sistema IA", "🔧"
    )
    status_card.pack(fill=tk.BOTH, expand=True, pady=self.ds.spacing["lg"])

    # Indicadores de status
    self.status_indicators = {}
    status_items = [
        ("🖥️ Navegador Web", "offline", "🌐"),
        ("⏰ Agendador IA", "parado", "⏰"),
        ("⚙️ Configuração", "ok", "⚙️"),
        ("📈 Última Execução", "nunca", "🕒"),
        ("🔗 Conectividade", "ok", "📡"),
        ("💾 Armazenamento", "ok", "💽"),
    ]

    for label, status, icon in status_items:
        indicator = self.factory.create_status_indicator(
            status_card, label, status, icon
        )
        indicator.pack(fill=tk.X, pady=self.ds.spacing["xs"])
        self.status_indicators[label] = indicator

    self.views["dashboard"] = view
