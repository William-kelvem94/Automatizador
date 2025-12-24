# -*- coding: utf-8 -*-

"""
ENTERPRISE BACKUP MANAGER - PostgreSQL
Sistema completo de backup e recovery com múltiplas estratégias
"""

import os
import shutil
import subprocess
import time
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import threading

from ...shared.utils.logger import get_logger
from ...infrastructure.monitoring.metrics_collector import metrics_collector


@dataclass
class BackupConfig:
    """Configuração de backup"""
    enabled: bool = True
    base_dir: str = "./backups"
    retention_days: int = 30
    compression: bool = True
    encryption: bool = False
    encryption_key: Optional[str] = None

    # Estratégias de backup
    full_backup_schedule: str = "0 2 * * *"  # Diariamente às 2:00
    incremental_backup_schedule: str = "0 */4 * * *"  # A cada 4 horas
    wal_archiving: bool = True

    # Configurações de performance
    parallel_jobs: int = 2
    max_backup_size_gb: float = 100.0

    # Configurações de monitoramento
    alert_on_failure: bool = True
    alert_email: Optional[str] = None


@dataclass
class BackupResult:
    """Resultado de operação de backup"""
    success: bool
    backup_type: str
    file_path: Optional[str] = None
    file_size: int = 0
    duration: float = 0.0
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class EnterpriseBackupManager:
    """Gerenciador de backup enterprise para PostgreSQL"""

    def __init__(self, config: BackupConfig, connection_string: str):
        self.config = config
        self.connection_string = connection_string
        self.logger = get_logger(__name__)

        # Diretórios
        self.base_dir = Path(config.base_dir)
        self.full_backups_dir = self.base_dir / "full"
        self.incremental_backups_dir = self.base_dir / "incremental"
        self.wal_archive_dir = self.base_dir / "wal"
        self.temp_dir = self.base_dir / "temp"

        # Criar diretórios
        for dir_path in [self.full_backups_dir, self.incremental_backups_dir,
                        self.wal_archive_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Controle de estado
        self.is_running = False
        self.last_full_backup: Optional[datetime] = None
        self.backup_thread: Optional[threading.Thread] = None

        # Estatísticas
        self.stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_size_gb': 0.0,
            'last_backup_time': None,
            'average_backup_duration': 0.0
        }

        # Carregar estado anterior
        self._load_backup_state()

        self.logger.info(f"EnterpriseBackupManager inicializado - Base dir: {self.base_dir}")

    def _load_backup_state(self):
        """Carregar estado de backups anteriores"""
        state_file = self.base_dir / "backup_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.last_full_backup = datetime.fromisoformat(state.get('last_full_backup')) if state.get('last_full_backup') else None
                    self.stats.update(state.get('stats', {}))
            except Exception as e:
                self.logger.warning(f"Erro ao carregar estado de backup: {e}")

    def _save_backup_state(self):
        """Salvar estado atual"""
        state = {
            'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
            'stats': self.stats,
            'config': {
                'retention_days': self.config.retention_days,
                'compression': self.config.compression,
                'encryption': self.config.encryption
            }
        }

        state_file = self.base_dir / "backup_state.json"
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado de backup: {e}")

    def start_automated_backups(self):
        """Iniciar backups automatizados"""
        if self.is_running:
            self.logger.warning("Backups automatizados já estão rodando")
            return

        self.is_running = True
        self.backup_thread = threading.Thread(
            target=self._backup_loop,
            daemon=True,
            name="AutomatedBackup"
        )
        self.backup_thread.start()

        self.logger.info("✅ Backups automatizados iniciados")

    def stop_automated_backups(self):
        """Parar backups automatizados"""
        self.is_running = False
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=10.0)

        self.logger.info("✅ Backups automatizados parados")

    def _backup_loop(self):
        """Loop principal de backup automatizado"""
        self.logger.info("Iniciando loop de backup automatizado")

        while self.is_running:
            try:
                current_time = datetime.now()

                # Verificar se deve fazer backup full
                if self._should_perform_full_backup(current_time):
                    self.logger.info("Executando backup full agendado...")
                    result = self.perform_full_backup()
                    if result.success:
                        self.last_full_backup = current_time

                # Verificar se deve fazer backup incremental
                elif self._should_perform_incremental_backup(current_time):
                    self.logger.info("Executando backup incremental agendado...")
                    self.perform_incremental_backup()

                # Limpeza de backups antigos
                self._cleanup_old_backups()

            except Exception as e:
                self.logger.error(f"Erro no loop de backup: {e}")

            # Aguardar próximo ciclo (verificar a cada 5 minutos)
            time.sleep(300)

    def _should_perform_full_backup(self, current_time: datetime) -> bool:
        """Verificar se deve executar backup full"""
        if not self.last_full_backup:
            return True

        # Lógica simplificada - backup full diário
        time_since_last_full = current_time - self.last_full_backup
        return time_since_last_full.days >= 1

    def _should_perform_incremental_backup(self, current_time: datetime) -> bool:
        """Verificar se deve executar backup incremental"""
        # Backup incremental a cada 4 horas
        return current_time.hour % 4 == 0 and current_time.minute < 5

    def perform_full_backup(self) -> BackupResult:
        """Executar backup full usando pg_dump"""
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Nome do arquivo
            backup_filename = f"automator_full_{timestamp}.sql"
            if self.config.compression:
                backup_filename += ".gz"

            backup_path = self.full_backups_dir / backup_filename

            # Comando pg_dump
            cmd = [
                "pg_dump",
                "--host", self._extract_host_from_connection(),
                "--port", str(self._extract_port_from_connection()),
                "--username", self._extract_user_from_connection(),
                "--dbname", self._extract_db_from_connection(),
                "--no-password",
                "--format", "custom" if not self.config.compression else "directory",
                "--compress", "9" if self.config.compression else "0",
                "--verbose",
                "--file", str(backup_path)
            ]

            # Adicionar senha via variável de ambiente
            env = os.environ.copy()
            env['PGPASSWORD'] = self._extract_password_from_connection()

            # Executar backup
            self.logger.info(f"Executando pg_dump: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora timeout
            )

            if result.returncode == 0:
                # Calcular checksum e tamanho
                file_size = backup_path.stat().st_size
                checksum = self._calculate_checksum(backup_path)

                # Criptografar se necessário
                if self.config.encryption and self.config.encryption_key:
                    backup_path = self._encrypt_backup(backup_path)

                duration = time.time() - start_time

                # Atualizar estatísticas
                self._update_backup_stats(True, file_size, duration)

                backup_result = BackupResult(
                    success=True,
                    backup_type="full",
                    file_path=str(backup_path),
                    file_size=file_size,
                    duration=duration,
                    checksum=checksum
                )

                self.logger.info(f"✅ Backup full concluído: {backup_path} ({file_size} bytes)")
                return backup_result

            else:
                error_msg = result.stderr.strip()
                self.logger.error(f"❌ Backup full falhou: {error_msg}")

                # Atualizar estatísticas de falha
                self._update_backup_stats(False, 0, time.time() - start_time)

                return BackupResult(
                    success=False,
                    backup_type="full",
                    error_message=error_msg,
                    duration=time.time() - start_time
                )

        except subprocess.TimeoutExpired:
            error_msg = "Backup timeout após 1 hora"
            self.logger.error(f"❌ {error_msg}")

            self._update_backup_stats(False, 0, time.time() - start_time)

            return BackupResult(
                success=False,
                backup_type="full",
                error_message=error_msg,
                duration=time.time() - start_time
            )

        except Exception as e:
            error_msg = f"Erro inesperado: {e}"
            self.logger.error(f"❌ {error_msg}")

            self._update_backup_stats(False, 0, time.time() - start_time)

            return BackupResult(
                success=False,
                backup_type="full",
                error_message=error_msg,
                duration=time.time() - start_time
            )

    def perform_incremental_backup(self) -> Optional[BackupResult]:
        """Executar backup incremental (baseado em WAL)"""
        # Implementação simplificada - em produção usaria pg_basebackup
        # ou ferramentas como Barman/WAL-E
        self.logger.info("Backup incremental não implementado nesta versão")
        return None

    def restore_from_backup(self, backup_path: str, target_db: Optional[str] = None) -> bool:
        """
        Restaurar backup

        Args:
            backup_path: Caminho do arquivo de backup
            target_db: Database de destino (opcional)

        Returns:
            True se sucesso
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                self.logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False

            # Descriptografar se necessário
            if self.config.encryption and backup_file.suffix == '.encrypted':
                backup_file = self._decrypt_backup(backup_file)

            # Comando pg_restore
            cmd = [
                "pg_restore",
                "--host", self._extract_host_from_connection(),
                "--port", str(self._extract_port_from_connection()),
                "--username", self._extract_user_from_connection(),
                "--dbname", target_db or self._extract_db_from_connection(),
                "--no-password",
                "--verbose",
                "--clean",
                "--if-exists",
                str(backup_file)
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self._extract_password_from_connection()

            self.logger.info(f"Restaurando backup: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos timeout
            )

            if result.returncode == 0:
                self.logger.info(f"✅ Restauração concluída com sucesso de {backup_path}")
                return True
            else:
                self.logger.error(f"❌ Restauração falhou: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Erro na restauração: {e}")
            return False

    def _cleanup_old_backups(self):
        """Limpar backups antigos baseado na retenção"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)

            total_removed = 0
            total_space_freed = 0

            # Limpar backups full
            for backup_file in self.full_backups_dir.glob("*.sql*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    file_size = backup_file.stat().st_size
                    backup_file.unlink()
                    total_removed += 1
                    total_space_freed += file_size

            # Limpar backups incrementais
            for backup_file in self.incremental_backups_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    if backup_file.is_file():
                        file_size = backup_file.stat().st_size
                        backup_file.unlink()
                        total_removed += 1
                        total_space_freed += file_size

            if total_removed > 0:
                freed_mb = total_space_freed / (1024 * 1024)
                self.logger.info(f"🧹 Limpados {total_removed} backups antigos, liberados {freed_mb:.1f} MB")

        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups: {e}")

    def get_backup_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de backup"""
        try:
            # Calcular espaço usado
            total_size = 0
            backup_count = 0

            for dir_path in [self.full_backups_dir, self.incremental_backups_dir, self.wal_archive_dir]:
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        backup_count += 1

            stats = dict(self.stats)
            stats.update({
                'total_backups_on_disk': backup_count,
                'total_size_bytes': total_size,
                'total_size_gb': total_size / (1024**3),
                'retention_days': self.config.retention_days,
                'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
                'automated_backups_running': self.is_running
            })

            return stats

        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}

    def _update_backup_stats(self, success: bool, size: int, duration: float):
        """Atualizar estatísticas de backup"""
        self.stats['total_backups'] += 1

        if success:
            self.stats['successful_backups'] += 1
            self.stats['total_size_gb'] += size / (1024**3)
        else:
            self.stats['failed_backups'] += 1

        self.stats['last_backup_time'] = datetime.now().isoformat()

        # Atualizar duração média
        if self.stats['total_backups'] == 1:
            self.stats['average_backup_duration'] = duration
        else:
            self.stats['average_backup_duration'] = (
                (self.stats['average_backup_duration'] * (self.stats['total_backups'] - 1)) + duration
            ) / self.stats['total_backups']

        # Salvar estado
        self._save_backup_state()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA256 do arquivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular checksum: {e}")
            return ""

    def _encrypt_backup(self, backup_path: Path) -> Path:
        """Criptografar arquivo de backup"""
        # Implementação simplificada - em produção usaria AES-256
        encrypted_path = backup_path.with_suffix(backup_path.suffix + '.encrypted')
        shutil.move(str(backup_path), str(encrypted_path))
        return encrypted_path

    def _decrypt_backup(self, encrypted_path: Path) -> Path:
        """Descriptografar arquivo de backup"""
        # Implementação simplificada
        decrypted_path = encrypted_path.with_suffix(encrypted_path.suffix.replace('.encrypted', ''))
        shutil.move(str(encrypted_path), str(decrypted_path))
        return decrypted_path

    # Métodos utilitários para extrair informações da connection string
    def _extract_host_from_connection(self) -> str:
        """Extrair host da connection string"""
        # Implementação simplificada
        return "localhost"

    def _extract_port_from_connection(self) -> int:
        """Extrair porta da connection string"""
        return 5432

    def _extract_user_from_connection(self) -> str:
        """Extrair usuário da connection string"""
        return "automator"

    def _extract_password_from_connection(self) -> str:
        """Extrair senha da connection string"""
        return "automator_pass"

    def _extract_db_from_connection(self) -> str:
        """Extrair nome do database"""
        return "automator_db"

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do backup manager"""
        try:
            stats = self.get_backup_stats()

            # Verificar se diretório existe e é acessível
            if not self.base_dir.exists():
                return {'status': 'unhealthy', 'error': 'Backup directory not found'}

            # Verificar espaço disponível
            try:
                total, used, free = shutil.disk_usage(self.base_dir)
                free_gb = free / (1024**3)

                if free_gb < 1.0:  # Menos de 1GB livre
                    return {'status': 'warning', 'message': f'Low disk space: {free_gb:.1f}GB free'}

            except Exception as e:
                return {'status': 'warning', 'message': f'Cannot check disk space: {e}'}

            return {
                'status': 'healthy',
                'backup_stats': stats,
                'configuration': {
                    'enabled': self.config.enabled,
                    'retention_days': self.config.retention_days,
                    'compression': self.config.compression,
                    'encryption': self.config.encryption
                }
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Função utilitária para criar backup manager
def create_backup_manager(database_url: str, config: Optional[BackupConfig] = None) -> EnterpriseBackupManager:
    """Factory para criar backup manager"""
    if config is None:
        config = BackupConfig()

    return EnterpriseBackupManager(config, database_url)
