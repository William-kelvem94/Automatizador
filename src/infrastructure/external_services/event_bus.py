#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EVENT BUS - SISTEMA DE EVENTOS
Implementação de event-driven architecture
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from ...domain.interfaces.automation_repository import IEventBus
from ...shared.utils.logger import get_logger


class EventBus(IEventBus):
    """Implementação do Event Bus usando asyncio"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

        self.logger.info("EventBus inicializado")

    async def start(self):
        """Inicia o processamento de eventos"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._process_events())
        self.logger.info("EventBus iniciado - processamento de eventos ativo")

    async def stop(self):
        """Para o processamento de eventos"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.logger.info("EventBus parado")

    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publica um evento"""
        if not self._running:
            self.logger.warning(f"EventBus não está rodando. Evento {event_type} ignorado.")
            return

        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'event_id': f"evt_{datetime.now().timestamp()}"
        }

        await self._event_queue.put(event)
        self.logger.debug(f"Evento publicado: {event_type}")

    async def subscribe(self, event_type: str, handler: Callable) -> None:
        """Inscreve um handler para um tipo de evento"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            self.logger.debug(f"Handler inscrito para evento: {event_type}")

    async def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove inscrição de um handler"""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                self.logger.debug(f"Handler removido para evento: {event_type}")

    async def _process_events(self):
        """Processa eventos da fila"""
        while self._running:
            try:
                # Aguarda próximo evento com timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                event_type = event['type']
                event_data = event['data']

                # Executa handlers para este tipo de evento
                if event_type in self._handlers:
                    handlers = self._handlers[event_type].copy()  # Cópia para evitar modificações durante execução

                    for handler in handlers:
                        try:
                            # Executa handler de forma assíncrona
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event_data)
                            else:
                                # Executa handler síncrono em thread pool
                                await asyncio.get_event_loop().run_in_executor(None, handler, event_data)

                        except Exception as e:
                            self.logger.error(f"Erro ao executar handler para evento {event_type}: {e}")
                            # Continua processando outros handlers mesmo se um falhar

                self._event_queue.task_done()

            except asyncio.TimeoutError:
                # Timeout normal - continua o loop
                continue
            except asyncio.CancelledError:
                # Task cancelada - sai do loop
                break
            except Exception as e:
                self.logger.error(f"Erro no processamento de eventos: {e}")
                await asyncio.sleep(1)  # Pequena pausa antes de continuar

    def get_subscribed_events(self) -> List[str]:
        """Retorna lista de tipos de evento com inscrições"""
        return list(self._handlers.keys())

    def get_handler_count(self, event_type: str) -> int:
        """Retorna número de handlers para um tipo de evento"""
        return len(self._handlers.get(event_type, []))

    def is_running(self) -> bool:
        """Verifica se o EventBus está rodando"""
        return self._running

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do EventBus"""
        return {
            'service': 'EventBus',
            'status': 'healthy' if self._running else 'stopped',
            'subscribed_events': self.get_subscribed_events(),
            'queue_size': self._event_queue.qsize(),
            'timestamp': datetime.now().isoformat()
        }


class EventStore:
    """Armazenamento persistente de eventos para audit e replay"""

    def __init__(self, storage_path: str = None):
        self.logger = get_logger(__name__)
        self.storage_path = storage_path or "./event_store"
        self._ensure_storage_path()
        self.logger.info(f"EventStore inicializado em: {self.storage_path}")

    def _ensure_storage_path(self):
        """Garante que o diretório de armazenamento existe"""
        import os
        os.makedirs(self.storage_path, exist_ok=True)

    async def store_event(self, event: Dict[str, Any]) -> bool:
        """Armazena evento no storage"""
        try:
            import json

            event_id = event.get('event_id', f"evt_{datetime.now().timestamp()}")
            filename = f"{event_id}.json"
            filepath = os.path.join(self.storage_path, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(event, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Evento armazenado: {event_id}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao armazenar evento: {e}")
            return False

    async def get_events(self, event_type: Optional[str] = None,
                        since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recupera eventos do storage"""
        try:
            import json
            import os

            events = []

            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_path, filename)

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            event = json.load(f)

                        # Filtros
                        if event_type and event.get('type') != event_type:
                            continue

                        if since:
                            event_time = event.get('timestamp', '')
                            if event_time < since:
                                continue

                        events.append(event)

                    except Exception as e:
                        self.logger.warning(f"Erro ao ler evento {filename}: {e}")

            # Ordena por timestamp
            events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return events

        except Exception as e:
            self.logger.error(f"Erro ao recuperar eventos: {e}")
            return []

    async def replay_events(self, event_bus: EventBus, event_type: Optional[str] = None,
                           since: Optional[str] = None) -> int:
        """Replay de eventos para o event bus"""
        events = await self.get_events(event_type, since)

        replayed_count = 0
        for event in events:
            try:
                await event_bus.publish(event['type'], event['data'])
                replayed_count += 1
            except Exception as e:
                self.logger.error(f"Erro no replay do evento {event.get('event_id')}: {e}")

        self.logger.info(f"Replay concluído: {replayed_count} eventos reproduzidos")
        return replayed_count

    async def cleanup_old_events(self, days_to_keep: int = 30) -> int:
        """Remove eventos antigos"""
        try:
            import os
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()

            removed_count = 0

            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_path, filename)

                    try:
                        # Lê timestamp do evento
                        with open(filepath, 'r', encoding='utf-8') as f:
                            event = json.load(f)

                        event_time = event.get('timestamp', '')
                        if event_time and event_time < cutoff_str:
                            os.remove(filepath)
                            removed_count += 1

                    except Exception as e:
                        self.logger.warning(f"Erro ao processar {filename}: {e}")

            self.logger.info(f"Limpeza concluída: {removed_count} eventos antigos removidos")
            return removed_count

        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")
            return 0
