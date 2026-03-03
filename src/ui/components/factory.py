import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple

from ..styles.design_system import DesignSystem


class ComponentFactory:
    """Fábrica de Componentes Reutilizáveis"""

    def __init__(self, root: tk.Tk, design_system: DesignSystem):
        self.root = root
        self.ds = design_system
        self._setup_styles()

    def _setup_styles(self):
        """Configura estilos ttk modernos"""
        style = ttk.Style()

        # ===== CONFIGURAÇÃO BASE =====
        style.configure(
            ".",
            background=self.ds.colors["bg_primary"],
            foreground=self.ds.colors["text_primary"],
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
        )

        # ===== BOTÕES MODERNOS =====
        # Botão Primário
        style.configure(
            "Primary.TButton",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            padding=(self.ds.spacing["xl"], self.ds.spacing["md"]),
            relief="flat",
            borderwidth=0,
            background=self.ds.colors["primary"],
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", self.ds.colors["primary_hover"]),
                ("pressed", self.ds.colors["primary_light"]),
            ],
            foreground=[
                ("active", self.ds.colors["text_primary"]),
                ("pressed", self.ds.colors["text_primary"]),
            ],
        )

        # Botão Secundário
        style.configure(
            "Secondary.TButton",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            padding=(self.ds.spacing["xl"], self.ds.spacing["md"]),
            relief="flat",
            borderwidth=0,
            background=self.ds.colors["bg_surface"],
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", self.ds.colors["bg_surface_hover"]),
                ("pressed", self.ds.colors["bg_surface_light"]),
            ],
            foreground=[("active", self.ds.colors["text_primary"])],
        )

        # Botão Danger
        style.configure(
            "Danger.TButton",
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"]["md"],
                "bold",
            ),
            padding=(self.ds.spacing["xl"], self.ds.spacing["md"]),
            relief="flat",
            borderwidth=0,
            background=self.ds.colors["error"],
        )

        # ===== CARDS E FRAMES =====
        style.configure(
            "Card.TFrame",
            background=self.ds.colors["bg_card"],
            relief="flat",
            borderwidth=0,
        )

        # ===== ENTRADAS =====
        style.configure(
            "TEntry",
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            fieldbackground=self.ds.colors["bg_input"],
            bordercolor=self.ds.colors["border"],
            lightcolor=self.ds.colors["border"],
            darkcolor=self.ds.colors["border"],
            insertcolor=self.ds.colors["text_primary"],
            padding=(self.ds.spacing["md"], self.ds.spacing["sm"]),
        )

        style.map(
            "TEntry",
            fieldbackground=[("focus", self.ds.colors["bg_input"])],
            bordercolor=[("focus", self.ds.colors["border_focus"])],
        )

        # ===== COMBOBOX =====
        style.configure(
            "TCombobox",
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            fieldbackground=self.ds.colors["bg_input"],
            background=self.ds.colors["bg_input"],
            bordercolor=self.ds.colors["border"],
            arrowcolor=self.ds.colors["text_secondary"],
            padding=(self.ds.spacing["md"], self.ds.spacing["sm"]),
        )

        style.map(
            "TCombobox",
            fieldbackground=[("focus", self.ds.colors["bg_input"])],
            background=[("focus", self.ds.colors["bg_input"])],
            bordercolor=[("focus", self.ds.colors["border_focus"])],
        )

        # ===== PROGRESSBAR =====
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=self.ds.colors["primary"],
            troughcolor=self.ds.colors["bg_surface"],
            borderwidth=0,
            lightcolor=self.ds.colors["primary"],
            darkcolor=self.ds.colors["secondary"],
        )

    def create_button(
        self,
        parent,
        text: str,
        command: Callable,
        variant: str = "primary",
        size: str = "md",
        **kwargs,
    ) -> tk.Button:
        """Cria botão padronizado com variantes"""
        variants = {
            "primary": {
                "bg": self.ds.colors["primary"],
                "fg": self.ds.colors["text_primary"],
                "hover_bg": self.ds.colors["primary_hover"],
                "active_bg": self.ds.colors["primary_light"],
            },
            "secondary": {
                "bg": self.ds.colors["bg_surface"],
                "fg": self.ds.colors["text_primary"],
                "hover_bg": self.ds.colors["bg_surface_hover"],
                "active_bg": self.ds.colors["bg_surface_light"],
            },
            "danger": {
                "bg": self.ds.colors["error"],
                "fg": self.ds.colors["text_primary"],
                "hover_bg": self.ds.colors["error_bg"],
                "active_bg": "#dc2626",
            },
            "success": {
                "bg": self.ds.colors["success"],
                "fg": self.ds.colors["text_primary"],
                "hover_bg": "#059669",
                "active_bg": "#047857",
            },
        }

        sizes = {
            "sm": (self.ds.spacing["lg"], self.ds.spacing["xs"]),
            "md": (self.ds.spacing["xl"], self.ds.spacing["md"]),
            "lg": (self.ds.spacing["2xl"], self.ds.spacing["lg"]),
        }

        variant_config = variants.get(variant, variants["primary"])
        width, height = sizes.get(size, sizes["md"])

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=(
                self.ds.typography["label"]["family"],
                self.ds.typography["label"]["sizes"][size],
                "bold",
            ),
            bg=variant_config["bg"],
            fg=variant_config["fg"],
            relief="flat",
            padx=width,
            pady=height,
            cursor="hand2",
            **kwargs,
        )

        # Hover effects
        def on_enter(e):
            button.configure(bg=variant_config["hover_bg"])

        def on_leave(e):
            button.configure(bg=variant_config["bg"])

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def create_card(
        self, parent, title: str = "", icon: str = "", padding: int = None
    ) -> tk.Frame:
        """Cria card moderno com sombra e bordas arredondadas simuladas"""
        if padding is None:
            padding = self.ds.spacing["lg"]

        # Container externo para sombra
        shadow_container = tk.Frame(parent, bg=self.ds.colors["bg_primary"])

        # Card principal
        card = tk.Frame(
            shadow_container,
            bg=self.ds.colors["bg_card"],
            relief="solid",
            bd=1,
            highlightbackground=self.ds.colors["border"],
            highlightcolor=self.ds.colors["border_focus"],
            highlightthickness=1,
        )

        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Header do card (se fornecido)
        if title or icon:
            header = tk.Frame(card, bg=self.ds.colors["bg_card"])
            header.pack(fill=tk.X, padx=padding, pady=(padding, self.ds.spacing["md"]))

            if icon:
                icon_label = tk.Label(
                    header,
                    text=icon,
                    font=(
                        self.ds.typography["heading"]["family"],
                        self.ds.typography["heading"]["sizes"]["sm"],
                    ),
                    bg=self.ds.colors["bg_card"],
                    fg=self.ds.colors["primary"],
                )
                icon_label.pack(side=tk.LEFT, padx=(0, self.ds.spacing["sm"]))

            if title:
                title_label = tk.Label(
                    header,
                    text=title,
                    font=(
                        self.ds.typography["heading"]["family"],
                        self.ds.typography["heading"]["sizes"]["sm"],
                        "bold",
                    ),
                    bg=self.ds.colors["bg_card"],
                    fg=self.ds.colors["text_primary"],
                    anchor="w",
                )
                title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        return shadow_container

    def create_input_field(
        self,
        parent,
        label_text: str = "",
        placeholder: str = "",
        input_type: str = "text",
        **kwargs,
    ) -> Tuple[tk.Frame, tk.Entry]:
        """Cria campo de entrada moderno"""
        container = tk.Frame(parent, bg=self.ds.colors["bg_card"])

        # Label
        if label_text:
            label = tk.Label(
                container,
                text=label_text,
                font=(
                    self.ds.typography["label"]["family"],
                    self.ds.typography["label"]["sizes"]["md"],
                ),
                bg=self.ds.colors["bg_card"],
                fg=self.ds.colors["text_secondary"],
                anchor="w",
            )
            label.pack(fill=tk.X, pady=(0, self.ds.spacing["xs"]))

        # Input container
        input_container = tk.Frame(
            container,
            bg=self.ds.colors["bg_input"],
            relief="solid",
            bd=1,
            highlightbackground=self.ds.colors["border"],
            highlightcolor=self.ds.colors["border_focus"],
            highlightthickness=1,
        )
        input_container.pack(fill=tk.X)

        # Entry
        show_char = "*" if input_type == "password" else ""
        entry = tk.Entry(
            input_container,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_input"],
            fg=self.ds.colors["text_primary"],
            insertbackground=self.ds.colors["text_primary"],
            relief="flat",
            bd=0,
            show=show_char,
            **kwargs,
        )
        entry.pack(fill=tk.X, padx=self.ds.spacing["md"], pady=self.ds.spacing["sm"])

        # Placeholder effect
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.ds.colors["text_muted"])

            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=self.ds.colors["text_primary"])

            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=self.ds.colors["text_muted"])

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        return container, entry

    def create_metric_card(
        self, parent, title: str, value: str, icon: str, trend: str = ""
    ) -> tk.Frame:
        """Cria card de métrica com ícone e valor destacado"""
        card = self.create_card(parent, title, icon)

        # Valor principal
        value_label = tk.Label(
            card,
            text=value,
            font=(
                self.ds.typography["display"]["family"],
                self.ds.typography["display"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["primary"],
        )
        value_label.pack(pady=(self.ds.spacing["md"], self.ds.spacing["sm"]))

        # Trend indicator (se fornecido)
        if trend:
            trend_color = (
                self.ds.colors["success"] if "↑" in trend else self.ds.colors["error"]
            )
            trend_label = tk.Label(
                card,
                text=trend,
                font=(
                    self.ds.typography["caption"]["family"],
                    self.ds.typography["caption"]["sizes"]["md"],
                ),
                bg=self.ds.colors["bg_card"],
                fg=trend_color,
            )
            trend_label.pack()

        return card, value_label

    def create_status_indicator(
        self, parent, label: str, status: str, icon: str
    ) -> tk.Frame:
        """Cria indicador de status moderno"""
        container = tk.Frame(parent, bg=self.ds.colors["bg_card"])

        # Frame interno
        frame = tk.Frame(
            container, bg=self.ds.colors["bg_surface"], relief="flat", bd=0
        )
        frame.pack(fill=tk.X, padx=1, pady=1)

        frame.grid_columnconfigure(2, weight=1)

        # Ícone
        icon_label = tk.Label(
            frame,
            text=icon,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["lg"],
            ),
            bg=self.ds.colors["bg_surface"],
            fg=self.ds.colors["secondary"],
        )
        icon_label.grid(
            row=0,
            column=0,
            padx=(self.ds.spacing["lg"], self.ds.spacing["md"]),
            pady=self.ds.spacing["lg"],
            sticky="w",
        )

        # Label
        label_widget = tk.Label(
            frame,
            text=label,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
                "bold",
            ),
            bg=self.ds.colors["bg_surface"],
            fg=self.ds.colors["text_primary"],
            anchor="w",
        )
        label_widget.grid(row=0, column=1, sticky="w")

        # Spacer
        spacer = tk.Frame(frame, bg=self.ds.colors["bg_surface"])
        spacer.grid(row=0, column=2, sticky="ew")

        # Status badge
        status_container = tk.Frame(frame, bg=self.ds.colors["bg_surface"])
        status_container.grid(row=0, column=3, padx=(0, self.ds.spacing["lg"]))

        status_colors = {
            "online": self.ds.colors["success"],
            "ativo": self.ds.colors["success"],
            "ok": self.ds.colors["success"],
            "offline": self.ds.colors["error"],
            "parado": self.ds.colors["warning"],
            "erro": self.ds.colors["error"],
            "nunca": self.ds.colors["text_muted"],
        }

        status_color = status_colors.get(status.lower(), self.ds.colors["text_primary"])
        status_label = tk.Label(
            status_container,
            text=status.upper(),
            font=(
                self.ds.typography["caption"]["family"],
                self.ds.typography["caption"]["sizes"]["sm"],
                "bold",
            ),
            bg=self.ds.colors["bg_surface"],
            fg=status_color,
            padx=self.ds.spacing["sm"],
            pady=self.ds.spacing["xs"],
            relief="flat",
        )
        status_label.pack()

        return container

    def create_notification(
        self, parent, message: str, type_: str = "info"
    ) -> tk.Frame:
        """Cria notificação flutuante moderna"""
        # Container da notificação
        notification = tk.Frame(
            parent,
            bg=self.ds.colors["bg_card"],
            relief="solid",
            bd=1,
            highlightbackground=self.ds.colors["border"],
        )

        # Configurar cores baseadas no tipo
        type_colors = {
            "success": self.ds.colors["success"],
            "error": self.ds.colors["error"],
            "warning": self.ds.colors["warning"],
            "info": self.ds.colors["info"],
        }

        accent_color = type_colors.get(type_, self.ds.colors["info"])

        # Barra lateral colorida
        accent_bar = tk.Frame(notification, bg=accent_color, width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Conteúdo
        content = tk.Frame(notification, bg=self.ds.colors["bg_card"])
        content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.ds.spacing["md"],
            pady=self.ds.spacing["md"],
        )

        # Ícone
        icons = {"success": "✓", "error": "✕", "warning": "⚠", "info": "ℹ"}

        icon_label = tk.Label(
            content,
            text=icons.get(type_, "ℹ"),
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["lg"],
            ),
            bg=self.ds.colors["bg_card"],
            fg=accent_color,
        )
        icon_label.pack(anchor="w")

        # Mensagem
        message_label = tk.Label(
            content,
            text=message,
            font=(
                self.ds.typography["body"]["family"],
                self.ds.typography["body"]["sizes"]["md"],
            ),
            bg=self.ds.colors["bg_card"],
            fg=self.ds.colors["text_primary"],
            wraplength=300,
            justify="left",
        )
        message_label.pack(anchor="w", pady=(self.ds.spacing["xs"], 0))

        return notification
