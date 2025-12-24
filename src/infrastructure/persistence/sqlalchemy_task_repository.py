#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REPOSITÓRIO DE TAREFAS - SQLALCHEMY
Implementação da persistência usando SQLAlchemy + SQLite
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from ...domain.entities.automation_task import AutomationTask, TaskStatus, BrowserType, AutomationResult
from ...domain.interfaces.automation_repository import IAutomationRepository
from ...shared.utils.logger import get_logger

Base = declarative_base()


class TaskModel(Base):
    """Modelo SQLAlchemy para tarefas"""
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    url = Column(String)
    username = Column(String)
    password = Column(String)

    # Configurações
    browser_type = Column(String, default='chrome')
    headless = Column(Boolean, default=False)
    timeout = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)

    # Seletores
    username_selector = Column(String, default='')
    password_selector = Column(String, default='')
    submit_selector = Column(String, default='')

    # Status
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    last_execution = Column(DateTime, nullable=True)

    # Relacionamentos
    execution_results = relationship("ExecutionResultModel", back_populates="task", cascade="all, delete-orphan")


class ExecutionResultModel(Base):
    """Modelo SQLAlchemy para resultados de execução"""
    __tablename__ = 'execution_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)

    success = Column(Boolean, nullable=False)
    message = Column(Text)
    execution_time = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.now)
    error_details = Column(Text)

    # Dados adicionais em JSON
    data = Column(Text, default='{}')

    # Relacionamento
    task = relationship("TaskModel", back_populates="execution_results")


class SQLAlchemyTaskRepository(IAutomationRepository):
    """Implementação do repositório usando SQLAlchemy"""

    def __init__(self, database_url: str = "sqlite:///automation.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.logger = get_logger(__name__)
        self._initialized = False

    async def _ensure_initialized(self):
        """Garante que o banco está inicializado"""
        if not self._initialized:
            await self._initialize()

    async def _initialize(self):
        """Inicializa conexão com banco de dados"""
        try:
            # Cria engine
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
                echo=False  # Desabilita logs SQL
            )

            # Cria tabelas
            Base.metadata.create_all(bind=self.engine)

            # Cria session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            self._initialized = True
            self.logger.info("Banco de dados inicializado com sucesso")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco: {e}")
            raise

    def _get_session(self) -> Session:
        """Obtém sessão do banco"""
        if not self._initialized:
            raise RuntimeError("Repositório não inicializado")
        return self.SessionLocal()

    async def save_task(self, task: AutomationTask) -> bool:
        """Salva tarefa no banco"""
        await self._ensure_initialized()

        session = self._get_session()
        try:
            # Converte entidade para modelo
            task_model = self._task_to_model(task)

            # Salva ou atualiza
            existing = session.query(TaskModel).filter(TaskModel.id == task.id).first()
            if existing:
                # Atualiza campos
                for key, value in task_model.__dict__.items():
                    if not key.startswith('_'):
                        setattr(existing, key, value)
            else:
                session.add(task_model)

            session.commit()
            self.logger.debug(f"Tarefa {task.id} salva com sucesso")
            return True

        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro ao salvar tarefa {task.id}: {e}")
            return False

        finally:
            session.close()

    async def get_task_by_id(self, task_id: str) -> Optional[AutomationTask]:
        """Busca tarefa por ID"""
        await self._ensure_initialized()

        session = self._get_session()
        try:
            task_model = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if task_model:
                return self._model_to_task(task_model)
            return None

        except Exception as e:
            self.logger.error(f"Erro ao buscar tarefa {task_id}: {e}")
            return None

        finally:
            session.close()

    async def get_all_tasks(self) -> List[AutomationTask]:
        """Retorna todas as tarefas"""
        await self._ensure_initialized()

        session = self._get_session()
        try:
            task_models = session.query(TaskModel).all()
            return [self._model_to_task(model) for model in task_models]

        except Exception as e:
            self.logger.error(f"Erro ao buscar tarefas: {e}")
            return []

        finally:
            session.close()

    async def delete_task(self, task_id: str) -> bool:
        """Remove tarefa do banco"""
        await self._ensure_initialized()

        session = self._get_session()
        try:
            result = session.query(TaskModel).filter(TaskModel.id == task_id).delete()
            session.commit()

            success = result > 0
            if success:
                self.logger.debug(f"Tarefa {task_id} removida com sucesso")
            else:
                self.logger.warning(f"Tarefa {task_id} não encontrada para remoção")

            return success

        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro ao remover tarefa {task_id}: {e}")
            return False

        finally:
            session.close()

    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Atualiza status de uma tarefa"""
        await self._ensure_initialized()

        session = self._get_session()
        try:
            result = session.query(TaskModel)\
                          .filter(TaskModel.id == task_id)\
                          .update({"status": status, "updated_at": datetime.now()})

            session.commit()
            success = result > 0

            if success:
                self.logger.debug(f"Status da tarefa {task_id} atualizado para {status}")
            else:
                self.logger.warning(f"Tarefa {task_id} não encontrada para atualização")

            return success

        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro ao atualizar status da tarefa {task_id}: {e}")
            return False

        finally:
            session.close()

    def _task_to_model(self, task: AutomationTask) -> TaskModel:
        """Converte entidade Task para modelo SQLAlchemy"""
        return TaskModel(
            id=task.id,
            name=task.name,
            description=task.description,
            url=task.url,
            username=task.username,
            password=task.password,
            browser_type=task.browser_type.value,
            headless=task.headless,
            timeout=task.timeout,
            max_retries=task.max_retries,
            username_selector=task.username_selector,
            password_selector=task.password_selector,
            submit_selector=task.submit_selector,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            last_execution=task.last_execution
        )

    def _model_to_task(self, model: TaskModel) -> AutomationTask:
        """Converte modelo SQLAlchemy para entidade Task"""
        # Carrega resultados de execução
        execution_history = []
        if hasattr(model, 'execution_results'):
            for result_model in model.execution_results:
                # Converte dados JSON
                data = {}
                try:
                    import json
                    data = json.loads(result_model.data) if result_model.data else {}
                except:
                    pass

                result = AutomationResult(
                    success=result_model.success,
                    message=result_model.message or "",
                    data=data,
                    execution_time=result_model.execution_time,
                    timestamp=result_model.timestamp,
                    error_details=result_model.error_details
                )
                execution_history.append(result)

        return AutomationTask(
            id=model.id,
            name=model.name,
            description=model.description or "",
            url=model.url or "",
            username=model.username or "",
            password=model.password or "",
            browser_type=BrowserType(model.browser_type or 'chrome'),
            headless=model.headless or False,
            timeout=model.timeout or 30,
            max_retries=model.max_retries or 3,
            username_selector=model.username_selector or "",
            password_selector=model.password_selector or "",
            submit_selector=model.submit_selector or "",
            status=TaskStatus(model.status or 'pending'),
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_execution=model.last_execution,
            execution_history=execution_history
        )
