#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONTROLADOR PRINCIPAL
Controla a interação entre interface e lógica de negócio
"""

import asyncio
from typing import Dict, Any, List, Optional
from ...application.services.automation_orchestrator import AutomationOrchestrator
from ...infrastructure.external_services.playwright_automation_service import PlaywrightAutomationService
from ...infrastructure.persistence.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ...shared.config.settings import Settings
from ...shared.utils.logger import get_logger


class MainController:
    """Controlador principal da aplicação"""

    def __init__(self):
        self.logger = get_logger(__name__)

        # Configurações
        self.settings = Settings()

        # Infraestrutura
        self.task_repository = SQLAlchemyTaskRepository()

        # Serviços
        self.automation_service = PlaywrightAutomationService()
        self.orchestrator = AutomationOrchestrator(
            task_repository=self.task_repository,
            automation_service=self.automation_service
        )

        # Cache de dados
        self._cached_tasks: Optional[List] = None

        self.logger.info("Controlador principal inicializado")

    async def initialize(self):
        """Inicializa componentes assíncronos"""
        try:
            # Inicializar repositórios
            await self.task_repository._ensure_initialized()
            await self.profile_repository._ensure_initialized()

            # Inicializar serviços
            await self.automation_service._ensure_initialized()

            self.logger.info("Componentes inicializados com sucesso")

        except Exception as e:
            self.logger.error(f"Erro na inicializacao: {e}")
            raise

    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Retorna lista de tarefas"""
        try:
            if self._cached_tasks is None:
                tasks = await self.task_repository.get_all_tasks()
                self._cached_tasks = [task.to_dict() for task in tasks]

            return self._cached_tasks.copy()

        except Exception as e:
            self.logger.error(f"Erro ao buscar tarefas: {e}")
            return []

    async def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Busca tarefa por ID"""
        try:
            task = await self.task_repository.get_task_by_id(task_id)
            return task.to_dict() if task else None

        except Exception as e:
            self.logger.error(f"Erro ao buscar tarefa {task_id}: {e}")
            return None

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova tarefa"""
        try:
            task = await self.orchestrator.create_task(task_data)

            # Invalida cache
            self._cached_tasks = None

            result = {
                'success': True,
                'task': task.to_dict(),
                'message': f"Tarefa '{task.name}' criada com sucesso"
            }

            self.logger.info(f"Tarefa criada: {task.id}")
            return result

        except Exception as e:
            self.logger.error(f"Erro ao criar tarefa: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro ao criar tarefa: {e}"
            }

    async def execute_automation_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa tarefa de automação"""
        try:
            # Cria tarefa temporária ou usa existente
            if 'id' in task_data:
                # Usa tarefa existente
                result = await self.orchestrator.execute_task(task_data['id'])
            else:
                # Cria e executa tarefa temporária
                task = await self.orchestrator.create_task(task_data)
                result = await self.orchestrator.execute_task(task.id)

            # Invalida cache
            self._cached_tasks = None

            return result

        except Exception as e:
            self.logger.error(f"Erro na execucao: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro na execucao: {e}"
            }

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Exclui tarefa"""
        try:
            success = await self.task_repository.delete_task(task_id)

            if success:
                # Invalida cache
                self._cached_tasks = None
                self.logger.info(f"Tarefa excluida: {task_id}")
                return {
                    'success': True,
                    'message': f"Tarefa excluida com sucesso"
                }
            else:
                return {
                    'success': False,
                    'message': "Tarefa nao encontrada"
                }

        except Exception as e:
            self.logger.error(f"Erro ao excluir tarefa {task_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro ao excluir tarefa: {e}"
            }


    async def analyze_webpage(self, url: str) -> Dict[str, Any]:
        """Analisa página web"""
        try:
            analysis = await self.automation_service.analyze_page(url)

            return {
                'success': True,
                'analysis': analysis.to_dict(),
                'message': f"Analise concluida para {url}"
            }

        except Exception as e:
            self.logger.error(f"Erro na analise de {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro na analise: {e}"
            }

    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Testa conexão com site"""
        try:
            result = await self.automation_service.test_connection(url)

            return {
                'success': result.get('success', False),
                'data': result,
                'message': result.get('message', 'Teste concluido')
            }

        except Exception as e:
            self.logger.error(f"Erro no teste de conexao: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro no teste: {e}"
            }

    async def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        try:
            stats = await self.orchestrator.get_statistics()
            return {
                'success': True,
                'statistics': stats
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter estatisticas: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro nas estatisticas: {e}"
            }

    def get_settings(self) -> Dict[str, Any]:
        """Retorna configurações atuais"""
        try:
            return self.settings.get_all_settings()
        except Exception as e:
            self.logger.error(f"Erro ao obter configuracoes: {e}")
            return {}

    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Salva configurações"""
        try:
            self.settings.update_settings(settings)
            return {
                'success': True,
                'message': "Configuracoes salvas com sucesso"
            }
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuracoes: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro ao salvar: {e}"
            }

    def reset_settings(self) -> Dict[str, Any]:
        """Restaura configurações padrão"""
        try:
            self.settings.reset_to_defaults()
            return {
                'success': True,
                'message': "Configuracoes restauradas para padrao"
            }
        except Exception as e:
            self.logger.error(f"Erro ao resetar configuracoes: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro ao resetar: {e}"
            }

    async def cleanup(self):
        """Limpa recursos"""
        try:
            await self.automation_service.cleanup()
            self.logger.info("Controlador finalizado")
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")

    def __del__(self):
        """Destrutor - garante limpeza"""
        try:
            if hasattr(self, 'automation_service'):
                # Executa cleanup síncrono se possível
                pass
        except:
            pass
