from typing import Any, Dict


class DesignSystem:
    """Sistema de Design Avançado com Tema Dark Professional"""

    def __init__(self):
        self.colors = self._define_color_palette()
        self.typography = self._define_typography()
        self.spacing = self._define_spacing()
        self.shadows = self._define_shadows()

    def _define_color_palette(self) -> Dict[str, str]:
        """Paleta de cores profissional e moderna"""
        return {
            # ===== BACKGROUND GRADIENTS =====
            "bg_primary": "#0a0a0a",  # Preto profundo
            "bg_secondary": "#111111",  # Preto ligeiramente mais claro
            "bg_surface": "#1a1a1a",  # Surface principal
            "bg_surface_light": "#212121",  # Surface clara
            "bg_surface_hover": "#262626",  # Hover state
            "bg_card": "#2a2a2a",  # Cards
            "bg_card_hover": "#333333",  # Cards hover
            "bg_input": "#1f1f1f",  # Inputs
            "bg_sidebar": "#0f0f0f",  # Sidebar
            "bg_header": "#1a1a1a",  # Header
            # ===== PRIMARY COLORS =====
            "primary": "#6366f1",  # Indigo moderno
            "primary_hover": "#4f46e5",  # Indigo escuro
            "primary_light": "#818cf8",  # Indigo claro
            "primary_bg": "#1e1b4b",  # Fundo primary
            # ===== SECONDARY COLORS =====
            "secondary": "#06b6d4",  # Cyan profissional
            "secondary_hover": "#0891b2",  # Cyan escuro
            "secondary_light": "#22d3ee",  # Cyan claro
            "secondary_bg": "#0c4a6e",  # Fundo secondary
            # ===== ACCENT COLORS =====
            "accent": "#ec4899",  # Pink sofisticado
            "accent_hover": "#db2777",  # Pink intenso
            "accent_light": "#f472b6",  # Pink suave
            "accent_bg": "#831843",  # Fundo accent
            # ===== SEMANTIC COLORS =====
            "success": "#10b981",  # Verde esmeralda
            "success_bg": "#064e3b",  # Fundo success
            "error": "#ef4444",  # Vermelho vibrante
            "error_bg": "#7f1d1d",  # Fundo error
            "warning": "#f59e0b",  # Âmbar dourado
            "warning_bg": "#78350f",  # Fundo warning
            "info": "#3b82f6",  # Azul informação
            "info_bg": "#1e3a8a",  # Fundo info
            # ===== TEXT COLORS =====
            "text_primary": "#fafafa",  # Branco quase puro
            "text_secondary": "#d1d5db",  # Cinza muito claro
            "text_tertiary": "#9ca3af",  # Cinza médio
            "text_muted": "#6b7280",  # Cinza mais escuro
            "text_inverse": "#0a0a0a",  # Texto sobre primary
            # ===== BORDER COLORS =====
            "border": "#374151",  # Bordas principais
            "border_light": "#4b5563",  # Bordas claras
            "border_focus": "#6366f1",  # Bordas de foco
            "border_success": "#10b981",  # Bordas success
            "border_error": "#ef4444",  # Bordas error
            # ===== GRADIENTS =====
            "gradient_primary": ["#6366f1", "#4f46e5"],
            "gradient_secondary": ["#06b6d4", "#0891b2"],
            "gradient_accent": ["#ec4899", "#db2777"],
            "gradient_dark": ["#1a1a1a", "#0a0a0a"],
            "gradient_surface": ["#2a2a2a", "#1a1a1a"],
        }

    def _define_typography(self) -> Dict[str, Dict[str, Any]]:
        """Sistema tipográfico consistente"""
        return {
            "display": {
                "family": "Segoe UI",
                "sizes": {"lg": 32, "md": 28, "sm": 24},
                "weights": {"bold": "bold", "semibold": "bold", "regular": "normal"},
            },
            "heading": {
                "family": "Segoe UI",
                "sizes": {"lg": 24, "md": 20, "sm": 18, "xs": 16},
                "weights": {"bold": "bold", "semibold": "bold", "regular": "normal"},
            },
            "body": {
                "family": "Segoe UI",
                "sizes": {"lg": 16, "md": 14, "sm": 13, "xs": 12},
                "weights": {"bold": "bold", "semibold": "bold", "regular": "normal"},
            },
            "label": {
                "family": "Segoe UI",
                "sizes": {"lg": 14, "md": 13, "sm": 12, "xs": 11},
                "weights": {"bold": "bold", "medium": "normal", "regular": "normal"},
            },
            "caption": {
                "family": "Segoe UI",
                "sizes": {"lg": 12, "md": 11, "sm": 10, "xs": 9},
                "weights": {"bold": "bold", "medium": "normal", "regular": "normal"},
            },
        }

    def _define_spacing(self) -> Dict[str, int]:
        """Sistema de espaçamento consistente"""
        return {
            "xs": 4,
            "sm": 8,
            "md": 12,
            "lg": 16,
            "xl": 20,
            "2xl": 24,
            "3xl": 32,
            "4xl": 40,
            "5xl": 48,
            "6xl": 64,
        }

    def _define_shadows(self) -> Dict[str, str]:
        """Sistema de sombras para profundidade visual"""
        return {
            "xs": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
            "none": "none",
        }
