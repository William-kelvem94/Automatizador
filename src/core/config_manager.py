"""
Gerenciador de Configuração Inteligente
Sistema avançado para gerenciar configurações com validação e backup
"""

import os
import json
import logging
import configparser
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class ConfigManager:
    """Gerenciador inteligente de configurações"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.ini"
        self.backup_dir = self.config_dir / "backups"
        self.logger = logging.getLogger(__name__)

        # Cria diretórios se não existirem
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        # Configurações padrão
        self.default_config = {
            'site': {
                'url': '',
                'email_selector': 'input[type="email"]',
                'password_selector': 'input[type="password"]',
                'submit_selector': 'button[type="submit"]'
            },
            'credentials': {
                'email': '',
                'password': ''
            },
            'schedule': {
                'enabled': 'false',
                'times': '08:00,12:00,18:00,22:00',
                'days': 'seg,ter,qua,qui,sex',
                'timezone': 'America/Sao_Paulo'
            },
            'settings': {
                'headless': 'false',
                'wait_timeout': '10',
                'max_retries': '3',
                'screenshot_on_error': 'true',
                'log_level': 'INFO'
            },
            'advanced': {
                'user_agent_rotation': 'true',
                'proxy_enabled': 'false',
                'proxy_list': '',
                'captcha_solver': 'none',
                'two_factor_auth': 'none'
            }
        }

        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self) -> bool:
        """Carrega configuração com fallbacks inteligentes"""
        try:
            # Cria arquivo se não existir
            if not self.config_file.exists():
                self.logger.info("Arquivo de configuração não encontrado, criando novo")
                self.create_default_config()

            # Carrega configuração
            self.config.read(self.config_file, encoding='utf-8')

            # Aplica configurações padrão para seções faltantes
            self._apply_defaults()

            # Valida configuração
            if self.validate_config():
                self.logger.info("Configuração carregada e validada com sucesso")
                return True
            else:
                self.logger.warning("Configuração carregada mas com avisos de validação")
                return True

        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            # Tenta criar configuração de emergência
            self.create_emergency_config()
            return False

    def create_default_config(self):
        """Cria arquivo de configuração com valores padrão"""
        try:
            # Aplica valores padrão
            for section, options in self.default_config.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for option, value in options.items():
                    self.config.set(section, option, value)

            # Salva arquivo
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            self.logger.info(f"Arquivo de configuração padrão criado: {self.config_file}")

        except Exception as e:
            self.logger.error(f"Erro ao criar configuração padrão: {e}")

    def create_emergency_config(self):
        """Cria configuração mínima de emergência"""
        try:
            # Configuração mínima
            emergency_config = configparser.ConfigParser()
            emergency_config.add_section('site')
            emergency_config.set('site', 'url', '')
            emergency_config.add_section('credentials')
            emergency_config.set('credentials', 'email', '')
            emergency_config.set('credentials', 'password', '')
            emergency_config.add_section('settings')
            emergency_config.set('settings', 'headless', 'false')

            self.config = emergency_config
            self.logger.warning("Configuração de emergência criada")

        except Exception as e:
            self.logger.critical("Falha crítica na configuração de emergência")

    def _apply_defaults(self):
        """Aplica valores padrão para opções faltantes"""
        for section, options in self.default_config.items():
            if not self.config.has_section(section):
                self.config.add_section(section)

            for option, default_value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, default_value)
                    self.logger.debug(f"Valor padrão aplicado: [{section}]{option} = {default_value}")

    def validate_config(self) -> bool:
        """Valida configuração carregada"""
        warnings = []
        errors = []

        try:
            # Valida URL
            url = self.get('site', 'url', '')
            if url and not self._is_valid_url(url):
                warnings.append("URL pode não ser válida")

            # Valida email
            email = self.get('credentials', 'email', '')
            if email and not self._is_valid_email(email):
                warnings.append("Formato de email pode ser inválido")

            # Valida horários
            times_str = self.get('schedule', 'times', '')
            if times_str:
                invalid_times = []
                for time_str in times_str.split(','):
                    time_str = time_str.strip()
                    if time_str and not self._is_valid_time(time_str):
                        invalid_times.append(time_str)

                if invalid_times:
                    warnings.append(f"Horários inválidos: {', '.join(invalid_times)}")

            # Valida timeout
            timeout = self.getint('settings', 'wait_timeout', 10)
            if timeout < 1 or timeout > 60:
                warnings.append("Timeout deve estar entre 1 e 60 segundos")

            # Log dos resultados
            if errors:
                for error in errors:
                    self.logger.error(f"Erro de configuração: {error}")

            if warnings:
                for warning in warnings:
                    self.logger.warning(f"Aviso de configuração: {warning}")

            return len(errors) == 0

        except Exception as e:
            self.logger.error(f"Erro na validação da configuração: {e}")
            return False

    def _is_valid_url(self, url: str) -> bool:
        """Valida formato básico de URL"""
        return url.startswith(('http://', 'https://')) and len(url) > 10

    def _is_valid_email(self, email: str) -> bool:
        """Valida formato básico de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _is_valid_time(self, time_str: str) -> bool:
        """Valida formato de horário HH:MM"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except ValueError:
            return False

    def save_config(self) -> bool:
        """Salva configuração com backup automático"""
        try:
            # Cria backup antes de salvar
            self._create_backup()

            # Salva nova configuração
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            self.logger.info("Configuração salva com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            return False

    def _create_backup(self):
        """Cria backup da configuração atual"""
        try:
            if self.config_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"config_{timestamp}.ini"

                # Copia arquivo atual
                import shutil
                shutil.copy2(self.config_file, backup_file)

                # Mantém apenas os 10 backups mais recentes
                self._cleanup_old_backups()

                self.logger.debug(f"Backup criado: {backup_file}")

        except Exception as e:
            self.logger.warning(f"Erro ao criar backup: {e}")

    def _cleanup_old_backups(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        try:
            backups = sorted(self.backup_dir.glob("config_*.ini"), reverse=True)
            if len(backups) > 10:
                for old_backup in backups[10:]:
                    old_backup.unlink()
                    self.logger.debug(f"Backup antigo removido: {old_backup}")
        except Exception as e:
            self.logger.warning(f"Erro ao limpar backups antigos: {e}")

    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """Obtém valor da configuração com fallback"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except:
            return fallback

    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """Obtém valor inteiro da configuração"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except:
            return fallback

    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Obtém valor booleano da configuração"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except:
            return fallback

    def set(self, section: str, option: str, value: Any):
        """Define valor na configuração"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))

    def get_all_config(self) -> Dict[str, Dict[str, str]]:
        """Retorna toda a configuração como dicionário"""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = {}
            for option in self.config.options(section):
                config_dict[section][option] = self.config.get(section, option)
        return config_dict

    def export_config(self, filepath: str) -> bool:
        """Exporta configuração para arquivo JSON"""
        try:
            config_data = {
                'exported_at': datetime.now().isoformat(),
                'config': self.get_all_config(),
                'metadata': {
                    'version': '4.0.0',
                    'type': 'automation_config'
                }
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Configuração exportada para: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao exportar configuração: {e}")
            return False

    def import_config(self, filepath: str) -> bool:
        """Importa configuração de arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'config' not in data:
                raise ValueError("Arquivo de importação inválido")

            # Cria backup antes de importar
            self._create_backup()

            # Aplica configuração importada
            for section, options in data['config'].items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for option, value in options.items():
                    self.config.set(section, option, value)

            # Salva configuração
            self.save_config()

            self.logger.info(f"Configuração importada de: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao importar configuração: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reseta configuração para valores padrão"""
        try:
            # Cria backup
            self._create_backup()

            # Recria configuração padrão
            self.config = configparser.ConfigParser()
            self.create_default_config()

            self.logger.info("Configuração resetada para valores padrão")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao resetar configuração: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """Retorna resumo da configuração atual"""
        return {
            'config_file': str(self.config_file),
            'backup_dir': str(self.backup_dir),
            'sections_count': len(self.config.sections()),
            'sections': list(self.config.sections()),
            'has_credentials': bool(self.get('credentials', 'email') and self.get('credentials', 'password')),
            'has_schedule': self.getboolean('schedule', 'enabled', False),
            'headless_mode': self.getboolean('settings', 'headless', False),
            'last_backup': self._get_last_backup_time()
        }

    def _get_last_backup_time(self) -> Optional[str]:
        """Obtém timestamp do último backup"""
        try:
            backups = list(self.backup_dir.glob("config_*.ini"))
            if backups:
                latest = max(backups, key=lambda x: x.stat().st_mtime)
                return datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
        except:
            pass
        return None
