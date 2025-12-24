"""
Sistema de Agendamento Inteligente
Gerencia execuções programadas com inteligência artificial
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor


class SmartScheduler:
    """Agendador inteligente com aprendizado e otimização"""

    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Configurações inteligentes
        self.smart_config = {
            'auto_adjust': True,      # Ajusta horários baseado em sucesso/falha
            'avoid_failures': True,   # Evita horários com alta taxa de falha
            'optimize_timing': True,  # Otimiza timing baseado em análise
            'retry_failed': True,     # Tenta novamente operações falhadas
        }

        # Estatísticas por horário
        self.schedule_stats = {}

        # Callbacks
        self.on_job_executed = None
        self.on_job_failed = None

    def initialize(self) -> bool:
        """Inicializa o agendador"""
        try:
            self.logger.info("Inicializando agendador inteligente...")

            # Configura jobstore e executor
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': AsyncIOExecutor()
            }

            # Configurações do scheduler
            job_defaults = {
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }

            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='America/Sao_Paulo'  # Ajuste para timezone brasileiro
            )

            self.logger.info("Agendador inteligente inicializado")
            return True

        except Exception as e:
            self.logger.error(f"Falha na inicialização do agendador: {e}")
            return False

    def schedule_login_operations(self, schedule_config: Dict[str, Any],
                                login_callback: Callable) -> bool:
        """
        Agenda operações de login com configuração inteligente

        Args:
            schedule_config: Configuração do agendamento
            login_callback: Função a ser executada
        """
        if not self.scheduler:
            self.logger.error("Agendador não inicializado")
            return False

        try:
            self.logger.info("Configurando agendamento inteligente...")

            # Extrai configuração
            times = schedule_config.get('times', [])
            days = schedule_config.get('days', ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom'])
            timezone = schedule_config.get('timezone', 'America/Sao_Paulo')

            if not times:
                self.logger.error("Nenhum horário especificado para agendamento")
                return False

            # Mapeia dias da semana
            day_mapping = {
                'dom': 0, 'seg': 1, 'ter': 2, 'qua': 3,
                'qui': 4, 'sex': 5, 'sab': 6
            }

            days_numbers = [day_mapping[day.lower()[:3]] for day in days
                          if day.lower()[:3] in day_mapping]

            if not days_numbers:
                days_numbers = [1, 2, 3, 4, 5]  # Segunda a sexta por padrão

            # Agenda cada horário
            jobs_scheduled = 0
            for time_str in times:
                try:
                    hour, minute = map(int, time_str.split(':'))

                    # Cria trigger inteligente
                    trigger = CronTrigger(
                        hour=hour,
                        minute=minute,
                        day_of_week=','.join(map(str, days_numbers)),
                        timezone=timezone
                    )

                    # Adiciona job com callback inteligente
                    job = self.scheduler.add_job(
                        func=self._smart_login_wrapper,
                        trigger=trigger,
                        args=[login_callback, time_str],
                        id=f"login_{time_str.replace(':', '')}",
                        name=f"Login Automático {time_str}",
                        replace_existing=True
                    )

                    # Inicializa estatísticas para este horário
                    self.schedule_stats[time_str] = {
                        'total_executions': 0,
                        'successful_executions': 0,
                        'failed_executions': 0,
                        'last_execution': None,
                        'last_success': None,
                        'average_duration': 0,
                        'consecutive_failures': 0
                    }

                    jobs_scheduled += 1
                    self.logger.info(f"Agendado login para {time_str} nos dias: {days}")

                except Exception as e:
                    self.logger.error(f"Erro ao agendar {time_str}: {e}")

            if jobs_scheduled > 0:
                self.logger.info(f"Total de {jobs_scheduled} operações agendadas")
                return True
            else:
                self.logger.error("Nenhuma operação foi agendada")
                return False

        except Exception as e:
            self.logger.error(f"Erro na configuração do agendamento: {e}")
            return False

    def _smart_login_wrapper(self, login_callback: Callable, schedule_time: str):
        """Wrapper inteligente para execuções de login"""
        start_time = time.time()

        try:
            self.logger.info(f"Iniciando execução agendada: {schedule_time}")

            # Verifica se deve executar baseado em inteligência
            if not self._should_execute(schedule_time):
                self.logger.info(f"Execução pulada por decisão inteligente: {schedule_time}")
                return

            # Executa callback
            result = login_callback()

            # Registra resultado
            self._record_execution_result(schedule_time, True, time.time() - start_time, result)

            # Callback de sucesso
            if self.on_job_executed:
                self.on_job_executed(schedule_time, result)

        except Exception as e:
            duration = time.time() - start_time
            self._record_execution_result(schedule_time, False, duration, str(e))

            self.logger.error(f"Falha na execução agendada {schedule_time}: {e}")

            # Callback de falha
            if self.on_job_failed:
                self.on_job_failed(schedule_time, str(e))

    def _should_execute(self, schedule_time: str) -> bool:
        """Decide se deve executar baseado em inteligência"""
        if not self.smart_config['auto_adjust']:
            return True

        stats = self.schedule_stats.get(schedule_time, {})

        # Se teve muitas falhas consecutivas, pula
        if self.smart_config['avoid_failures']:
            consecutive_failures = stats.get('consecutive_failures', 0)
            if consecutive_failures >= 3:
                self.logger.warning(f"Pulando execução devido a {consecutive_failures} falhas consecutivas")
                return False

        # Verifica se já executou recentemente com sucesso
        last_success = stats.get('last_success')
        if last_success:
            hours_since_success = (datetime.now() - last_success).total_seconds() / 3600
            if hours_since_success < 1:  # Não executa se teve sucesso há menos de 1 hora
                self.logger.info("Pulando execução - sucesso recente detectado")
                return False

        return True

    def _record_execution_result(self, schedule_time: str, success: bool,
                               duration: float, details: Any):
        """Registra resultado da execução para análise inteligente"""
        if schedule_time not in self.schedule_stats:
            self.schedule_stats[schedule_time] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'last_execution': None,
                'last_success': None,
                'average_duration': 0,
                'consecutive_failures': 0
            }

        stats = self.schedule_stats[schedule_time]

        # Atualiza contadores
        stats['total_executions'] += 1
        stats['last_execution'] = datetime.now()

        if success:
            stats['successful_executions'] += 1
            stats['last_success'] = datetime.now()
            stats['consecutive_failures'] = 0
        else:
            stats['failed_executions'] += 1
            stats['consecutive_failures'] += 1

        # Atualiza duração média
        current_avg = stats['average_duration']
        total_execs = stats['total_executions']
        stats['average_duration'] = (current_avg * (total_execs - 1) + duration) / total_execs

        # Log do resultado
        success_rate = (stats['successful_executions'] / stats['total_executions']) * 100
        self.logger.info(
            f"Resultado {schedule_time}: {'SUCESSO' if success else 'FALHA'} "
            f"({success_rate:.1f}% sucesso, {duration:.1f}s, {stats['consecutive_failures']} falhas seguidas)"
        )

    def start(self) -> bool:
        """Inicia o agendador"""
        if not self.scheduler:
            self.logger.error("Agendador não inicializado")
            return False

        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                self.logger.info("Agendador inteligente iniciado")

                # Thread para manter vivo
                scheduler_thread = threading.Thread(target=self._keep_alive, daemon=True)
                scheduler_thread.start()

            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar agendador: {e}")
            return False

    def stop(self):
        """Para o agendador"""
        if self.scheduler and self.is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                self.logger.info("Agendador inteligente parado")
            except Exception as e:
                self.logger.error(f"Erro ao parar agendador: {e}")

    def _keep_alive(self):
        """Mantém o agendador vivo"""
        while self.is_running:
            time.sleep(1)

    def get_schedule_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do agendamento"""
        if not self.scheduler:
            return {'status': 'not_initialized'}

        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            jobs.append(job_info)

        return {
            'status': 'running' if self.is_running else 'stopped',
            'jobs_count': len(jobs),
            'jobs': jobs,
            'stats': self.schedule_stats.copy(),
            'smart_config': self.smart_config.copy()
        }

    def optimize_schedule(self) -> Dict[str, Any]:
        """Otimiza agendamento baseado em análise inteligente"""
        if not self.smart_config['optimize_timing']:
            return {'optimized': False, 'reason': 'optimization_disabled'}

        optimizations = []

        for schedule_time, stats in self.schedule_stats.items():
            total_execs = stats['total_executions']
            if total_execs < 5:  # Precisa de dados suficientes
                continue

            success_rate = stats['successful_executions'] / total_execs

            # Se taxa de sucesso baixa, sugere ajustes
            if success_rate < 0.5:
                optimizations.append({
                    'time': schedule_time,
                    'issue': 'low_success_rate',
                    'success_rate': success_rate,
                    'suggestion': 'Consider adjusting time or checking system stability'
                })

            # Se muitas falhas consecutivas
            if stats['consecutive_failures'] >= 2:
                optimizations.append({
                    'time': schedule_time,
                    'issue': 'consecutive_failures',
                    'failures': stats['consecutive_failures'],
                    'suggestion': 'Temporary suspension recommended'
                })

        return {
            'optimized': len(optimizations) > 0,
            'optimizations': optimizations,
            'total_analyzed': len(self.schedule_stats)
        }

    def cleanup(self):
        """Limpa recursos do agendador"""
        self.stop()
        self.schedule_stats.clear()
