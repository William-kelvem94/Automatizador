# -*- coding: utf-8 -*-

"""
SECURITY AUDIT MODULE - Auditoria de Segurança Enterprise
Sistema completo de auditoria e compliance
"""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from ...shared.utils.logger import get_logger


class AuditEventType(Enum):
    """Tipos de eventos de auditoria"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    SECURITY_INCIDENT = "security_incident"
    CONFIGURATION_CHANGE = "configuration_change"
    USER_ACTIVITY = "user_activity"
    SYSTEM_ERROR = "system_error"


class AuditSeverity(Enum):
    """Severidade dos eventos de auditoria"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Evento de auditoria"""
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    resource: str
    action: str
    result: str  # success/failure
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: f"audit_{int(time.time() * 1000000)}")

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'hash': self._generate_hash()
        }

    def _generate_hash(self) -> str:
        """Gerar hash de integridade do evento"""
        data = f"{self.event_id}{self.event_type.value}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class SecurityAuditor:
    """Auditor de segurança principal"""

    def __init__(self, log_path: str = "./logs/audit.log"):
        self.logger = get_logger(__name__)
        self.log_path = log_path
        self._ensure_log_directory()

        # Estatísticas
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'failed_auth_attempts': 0,
            'suspicious_activities': 0
        }

    def _ensure_log_directory(self):
        """Garantir que o diretório de logs existe"""
        import os
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(self, event: AuditEvent) -> None:
        """Registrar evento de auditoria"""
        try:
            # Atualizar estatísticas
            self._update_stats(event)

            # Escrever no log
            with open(self.log_path, 'a', encoding='utf-8') as f:
                json.dump(event.to_dict(), f, ensure_ascii=False)
                f.write('\n')

            # Log adicional para eventos críticos
            if event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                self.logger.warning(f"Security Event: {event.event_type.value} - {event.action}")

            # Verificar padrões suspeitos
            self._check_suspicious_patterns(event)

        except Exception as e:
            self.logger.error(f"Erro ao registrar evento de auditoria: {e}")

    def _update_stats(self, event: AuditEvent):
        """Atualizar estatísticas"""
        self.stats['total_events'] += 1

        # Por tipo
        event_type = event.event_type.value
        self.stats['events_by_type'][event_type] = self.stats['events_by_type'].get(event_type, 0) + 1

        # Por severidade
        severity = event.severity.value
        self.stats['events_by_severity'][severity] = self.stats['events_by_severity'].get(severity, 0) + 1

        # Contadores específicos
        if event.event_type == AuditEventType.AUTHENTICATION and event.result == 'failure':
            self.stats['failed_auth_attempts'] += 1

        if event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            self.stats['suspicious_activities'] += 1

    def _check_suspicious_patterns(self, event: AuditEvent):
        """Verificar padrões suspeitos"""
        # Tentativas de autenticação falhadas múltiplas
        if (event.event_type == AuditEventType.AUTHENTICATION and
            event.result == 'failure' and
            event.details.get('consecutive_failures', 0) > 3):
            self.log_event(AuditEvent(
                event_type=AuditEventType.SECURITY_INCIDENT,
                severity=AuditSeverity.HIGH,
                user_id=event.user_id,
                session_id=event.session_id,
                resource="authentication",
                action="multiple_failed_attempts",
                result="detected",
                details={
                    'incident_type': 'brute_force_attempt',
                    'user_id': event.user_id,
                    'ip_address': event.ip_address
                },
                ip_address=event.ip_address,
                user_agent=event.user_agent
            ))

        # Acesso a recursos sensíveis
        sensitive_resources = ['admin', 'security', 'encryption_keys']
        if (any(resource in event.resource.lower() for resource in sensitive_resources) and
            event.result == 'success'):
            self.log_event(AuditEvent(
                event_type=AuditEventType.SECURITY_INCIDENT,
                severity=AuditSeverity.MEDIUM,
                user_id=event.user_id,
                session_id=event.session_id,
                resource=event.resource,
                action="sensitive_resource_access",
                result="logged",
                details={
                    'resource_type': 'sensitive',
                    'access_granted': True
                },
                ip_address=event.ip_address,
                user_agent=event.user_agent
            ))

    def get_audit_trail(self,
                        user_id: Optional[str] = None,
                        event_type: Optional[AuditEventType] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Obter trilha de auditoria com filtros"""
        try:
            events = []

            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        event_data = json.loads(line.strip())
                        event_datetime = datetime.fromisoformat(event_data['timestamp'])

                        # Aplicar filtros
                        if user_id and event_data.get('user_id') != user_id:
                            continue

                        if event_type and event_data.get('event_type') != event_type.value:
                            continue

                        if start_date and event_datetime < start_date:
                            continue

                        if end_date and event_datetime > end_date:
                            continue

                        events.append(event_data)

                        if len(events) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

            return events

        except Exception as e:
            self.logger.error(f"Erro ao obter trilha de auditoria: {e}")
            return []

    def get_security_report(self,
                           days: int = 7,
                           include_details: bool = False) -> Dict[str, Any]:
        """Gerar relatório de segurança"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Obter eventos do período
            events = self.get_audit_trail(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Limite alto para relatório
            )

            # Análise dos eventos
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_events': len(events),
                    'events_by_type': {},
                    'events_by_severity': {},
                    'failed_authentications': 0,
                    'security_incidents': 0,
                    'unique_users': set(),
                    'unique_ips': set()
                },
                'critical_events': [],
                'recommendations': []
            }

            for event in events:
                # Contadores
                event_type = event.get('event_type', 'unknown')
                severity = event.get('event_type', 'unknown')

                report['summary']['events_by_type'][event_type] = \
                    report['summary']['events_by_type'].get(event_type, 0) + 1

                report['summary']['events_by_severity'][severity] = \
                    report['summary']['events_by_severity'].get(severity, 0) + 1

                # Eventos específicos
                if event_type == 'authentication' and event.get('result') == 'failure':
                    report['summary']['failed_authentications'] += 1

                if event_type == 'security_incident':
                    report['summary']['security_incidents'] += 1

                # Usuários e IPs únicos
                if event.get('user_id'):
                    report['summary']['unique_users'].add(event.get('user_id'))

                if event.get('ip_address'):
                    report['summary']['unique_ips'].add(event.get('ip_address'))

                # Eventos críticos
                if severity in ['high', 'critical']:
                    report['critical_events'].append(event)

            # Converter sets para listas
            report['summary']['unique_users'] = list(report['summary']['unique_users'])
            report['summary']['unique_ips'] = list(report['summary']['unique_ips'])

            # Gerar recomendações
            report['recommendations'] = self._generate_security_recommendations(report)

            # Limitar eventos críticos se não solicitado detalhes completos
            if not include_details and len(report['critical_events']) > 10:
                report['critical_events'] = report['critical_events'][:10]
                report['note'] = "Apenas os 10 eventos mais recentes são mostrados"

            return report

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de segurança: {e}")
            return {'error': str(e)}

    def _generate_security_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Gerar recomendações de segurança baseadas no relatório"""
        recommendations = []

        summary = report.get('summary', {})

        # Recomendações baseadas em falhas de autenticação
        failed_auth = summary.get('failed_authentications', 0)
        if failed_auth > 10:
            recommendations.append(f"Alto número de falhas de autenticação ({failed_auth}). Considere implementar bloqueio temporário.")

        # Recomendações baseadas em incidentes de segurança
        incidents = summary.get('security_incidents', 0)
        if incidents > 0:
            recommendations.append(f"{incidents} incidente(s) de segurança detectado(s). Revisar logs detalhadamente.")

        # Recomendações baseadas em acessos únicos
        unique_users = len(summary.get('unique_users', []))
        if unique_users > 50:
            recommendations.append(f"Muitos usuários únicos ({unique_users}). Considere implementar rate limiting.")

        # Recomendações gerais
        if summary.get('total_events', 0) < 100:
            recommendations.append("Baixo volume de eventos de auditoria. Verificar se auditoria está funcionando corretamente.")

        return recommendations

    def archive_old_logs(self, days_to_keep: int = 90) -> int:
        """Arquivar logs antigos"""
        try:
            import shutil
            from pathlib import Path

            archive_dir = Path(self.log_path).parent / "archive"
            archive_dir.mkdir(exist_ok=True)

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            archived_count = 0

            # Criar arquivo de archive
            archive_file = archive_dir / f"audit_archive_{cutoff_date.strftime('%Y%m%d')}.log"

            with open(self.log_path, 'r', encoding='utf-8') as current_file, \
                 open(archive_file, 'w', encoding='utf-8') as archive:

                lines_to_keep = []

                for line in current_file:
                    try:
                        event_data = json.loads(line.strip())
                        event_date = datetime.fromisoformat(event_data['timestamp'])

                        if event_date < cutoff_date:
                            # Arquivar evento antigo
                            archive.write(line)
                            archived_count += 1
                        else:
                            # Manter evento recente
                            lines_to_keep.append(line)
                    except (json.JSONDecodeError, KeyError):
                        # Linha inválida - manter
                        lines_to_keep.append(line)

            # Reescrever arquivo atual com eventos recentes
            with open(self.log_path, 'w', encoding='utf-8') as current_file:
                current_file.writelines(lines_to_keep)

            if archived_count > 0:
                self.logger.info(f"Arquivados {archived_count} eventos antigos")

            return archived_count

        except Exception as e:
            self.logger.error(f"Erro ao arquivar logs antigos: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas atuais"""
        return self.stats.copy()

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do auditor"""
        try:
            # Verificar se arquivo de log é acessível
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write("")  # Teste de escrita

            # Verificar estatísticas
            stats = self.get_stats()

            return {
                'status': 'healthy',
                'log_file': self.log_path,
                'total_events_logged': stats.get('total_events', 0),
                'last_check': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'log_file': self.log_path
            }


# Funções utilitárias para auditoria rápida
def audit_authentication(user_id: str, success: bool, ip_address: Optional[str] = None,
                        details: Optional[Dict[str, Any]] = None) -> None:
    """Auditoria rápida de autenticação"""
    auditor = SecurityAuditor()
    auditor.log_event(AuditEvent(
        event_type=AuditEventType.AUTHENTICATION,
        severity=AuditSeverity.MEDIUM if not success else AuditSeverity.LOW,
        user_id=user_id,
        resource="authentication",
        action="login_attempt",
        result="success" if success else "failure",
        details=details or {},
        ip_address=ip_address
    ))


def audit_data_access(user_id: str, resource: str, action: str,
                     success: bool, details: Optional[Dict[str, Any]] = None) -> None:
    """Auditoria rápida de acesso a dados"""
    auditor = SecurityAuditor()
    auditor.log_event(AuditEvent(
        event_type=AuditEventType.DATA_ACCESS,
        severity=AuditSeverity.MEDIUM,
        user_id=user_id,
        resource=resource,
        action=action,
        result="success" if success else "failure",
        details=details or {}
    ))


def audit_security_incident(incident_type: str, severity: AuditSeverity,
                           details: Dict[str, Any]) -> None:
    """Auditoria rápida de incidente de segurança"""
    auditor = SecurityAuditor()
    auditor.log_event(AuditEvent(
        event_type=AuditEventType.SECURITY_INCIDENT,
        severity=severity,
        resource="security_system",
        action=incident_type,
        result="detected",
        details=details
    ))
