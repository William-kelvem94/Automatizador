#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONFIGURAÇÕES COMPARTILHADAS
Sistema de configurações centralizado
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import get_logger


class Settings:
    """Gerenciador centralizado de configurações"""

    def __init__(self, config_file: Optional[str] = None):
        self.logger = get_logger(__name__)

        # Arquivo de configuração
        if config_file is None:
            config_dir = Path.home() / ".automator_ia_v7"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "settings.json"

        self.config_file = Path(config_file)
        self._settings = {}
        self._load_settings()

    def _load_settings(self):
        """Carrega configurações do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                self.logger.debug("Configuracoes carregadas do arquivo")
            else:
                self._settings = self._get_default_settings()
                self._save_settings()
                self.logger.debug("Configuracoes padrao criadas")

        except Exception as e:
            self.logger.warning(f"Erro ao carregar configuracoes: {e}")
            self._settings = self._get_default_settings()

    def _save_settings(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            self.logger.debug("Configuracoes salvas")

        except Exception as e:
            self.logger.error(f"Erro ao salvar configuracoes: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            # Interface
            'theme': 'dark',
            'language': 'pt-BR',
            'window_width': 1400,
            'window_height': 900,

            # Automação
            'default_browser': 'chrome',
            'default_timeout': 30,
            'default_max_retries': 3,
            'headless_default': False,

            # Logging
            'log_level': 'INFO',
            'log_max_size': '10 MB',
            'log_retention': '7 days',

            # Backup
            'auto_backup': True,
            'backup_interval': 'daily',
            'max_backups': 10,

            # Seletores padrão
            'default_selectors': {
                'username': 'input[type="email"], input[name*="user"]',
                'password': 'input[type="password"]',
                'submit': 'button[type="submit"], input[type="submit"]'
            },

            # Plugins
            'enabled_plugins': [],
            'plugin_search_paths': [],

            # Segurança
            'encrypt_sensitive_data': True,
            'auto_clear_temp_files': True,

            # Performance
            'max_concurrent_tasks': 3,
            'task_queue_size': 100,

            # Notificações
            'desktop_notifications': True,
            'sound_notifications': False,

            # Rede
            'request_timeout': 30,
            'max_redirects': 5,
            'verify_ssl': True
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém configuração por chave"""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Define configuração"""
        self._settings[key] = value
        self._save_settings()

    def update_settings(self, settings: Dict[str, Any]):
        """Atualiza múltiplas configurações"""
        self._settings.update(settings)
        self._save_settings()

    def get_all_settings(self) -> Dict[str, Any]:
        """Retorna todas as configurações"""
        return self._settings.copy()

    def reset_to_defaults(self):
        """Restaura configurações padrão"""
        self._settings = self._get_default_settings()
        self._save_settings()
        self.logger.info("Configuracoes restauradas para padrao")

    # Métodos específicos para configurações comuns
    def get_theme(self) -> str:
        """Retorna tema atual"""
        return self.get('theme', 'dark')

    def get_language(self) -> str:
        """Retorna idioma atual"""
        return self.get('language', 'pt-BR')

    def get_window_size(self) -> tuple:
        """Retorna tamanho da janela"""
        width = self.get('window_width', 1400)
        height = self.get('window_height', 900)
        return (width, height)

    def set_window_size(self, width: int, height: int):
        """Define tamanho da janela"""
        self.set('window_width', width)
        self.set('window_height', height)

    def get_log_level(self) -> str:
        """Retorna nível de log"""
        return self.get('log_level', 'INFO')

    def is_auto_backup_enabled(self) -> bool:
        """Verifica se backup automático está habilitado"""
        return self.get('auto_backup', True)

    def get_default_browser(self) -> str:
        """Retorna navegador padrão"""
        return self.get('default_browser', 'chrome')

    def get_default_timeout(self) -> int:
        """Retorna timeout padrão"""
        return self.get('default_timeout', 30)

    def get_max_concurrent_tasks(self) -> int:
        """Retorna máximo de tarefas concorrentes"""
        return self.get('max_concurrent_tasks', 3)

    def are_desktop_notifications_enabled(self) -> bool:
        """Verifica se notificações desktop estão habilitadas"""
        return self.get('desktop_notifications', True)

    def get_default_selectors(self) -> Dict[str, str]:
        """Retorna seletores padrão"""
        return self.get('default_selectors', {
            'username': 'input[type="email"]',
            'password': 'input[type="password"]',
            'submit': 'button[type="submit"]'
        })

    # Métodos de validação
    def validate_setting(self, key: str, value: Any) -> bool:
        """Valida se um valor é válido para uma configuração"""
        validators = {
            'theme': lambda v: v in ['light', 'dark', 'system'],
            'language': lambda v: v in ['pt-BR', 'en-US', 'es-ES'],
            'log_level': lambda v: v in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            'default_browser': lambda v: v in ['chrome', 'firefox', 'edge', 'safari'],
            'window_width': lambda v: isinstance(v, int) and 800 <= v <= 2560,
            'window_height': lambda v: isinstance(v, int) and 600 <= v <= 1440,
            'default_timeout': lambda v: isinstance(v, int) and 5 <= v <= 300,
            'max_concurrent_tasks': lambda v: isinstance(v, int) and 1 <= v <= 10
        }

        validator = validators.get(key)
        if validator:
            return validator(value)

        # Para configurações sem validação específica, aceita qualquer valor
        return True

    def get_valid_options(self, key: str) -> Optional[list]:
        """Retorna opções válidas para uma configuração"""
        options = {
            'theme': ['light', 'dark', 'system'],
            'language': ['pt-BR', 'en-US', 'es-ES'],
            'log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            'default_browser': ['chrome', 'firefox', 'edge', 'safari'],
            'backup_interval': ['hourly', 'daily', 'weekly', 'monthly']
        }

        return options.get(key)

    # Métodos de perfil
    def create_profile(self, profile_name: str) -> Dict[str, Any]:
        """Cria um perfil de configurações"""
        profile = {
            'name': profile_name,
            'created_at': str(__import__('datetime').datetime.now()),
            'settings': self._settings.copy()
        }

        profiles = self.get('profiles', [])
        profiles.append(profile)
        self.set('profiles', profiles)

        return profile

    def load_profile(self, profile_name: str) -> bool:
        """Carrega um perfil de configurações"""
        profiles = self.get('profiles', [])

        for profile in profiles:
            if profile['name'] == profile_name:
                self._settings.update(profile['settings'])
                self._save_settings()
                return True

        return False

    def get_profiles(self) -> list:
        """Retorna lista de perfis salvos"""
        return [p['name'] for p in self.get('profiles', [])]

    def delete_profile(self, profile_name: str) -> bool:
        """Exclui um perfil"""
        profiles = self.get('profiles', [])
        profiles = [p for p in profiles if p['name'] != profile_name]
        self.set('profiles', profiles)
        return True
