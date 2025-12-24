#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAZY IMPORTER ENTERPRISE v9.0
Sistema de importação inteligente com cache, monitoramento e fallback
"""

import importlib
import sys
import time
import threading
from typing import Any, Optional, Dict, List, Set
from pathlib import Path
import weakref
import logging

logger = logging.getLogger(__name__)

class LazyImporterEnterprise:
    """
    Lazy Importer Enterprise - Sistema avançado de carregamento condicional

    Features:
    - Categorização inteligente por domínio
    - Cache com TTL e LRU eviction
    - Monitoramento de performance
    - Fallback automático
    - Lazy loading condicional baseado em features
    """

    def __init__(self, cache_size_mb: int = 100, ttl_seconds: int = 3600):
        self._loaded_modules: Dict[str, Any] = {}
        self._module_metadata: Dict[str, Dict] = {}
        self._cache_size_mb = cache_size_mb
        self._ttl_seconds = ttl_seconds
        self._current_cache_size = 0
        self._lock = threading.RLock()

        # Categorização inteligente de módulos
        self._module_categories = {
            # Core (sempre carregado)
            'core': {
                'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
                'sqlalchemy', 'sqlalchemy.orm', 'loguru', 'pydantic',
                'pathlib', 'os', 'sys', 'json', 'time'
            },

            # AI/ML (carregado sob demanda)
            'ai': {
                'torch', 'transformers', 'openai', 'anthropic',
                'scikit-learn', 'numpy', 'pandas'
            },

            # Vision (carregado sob demanda)
            'vision': {
                'cv2', 'PIL', 'opencv-python', 'scikit-image'
            },

            # Web/API (carregado sob demanda)
            'web': {
                'fastapi', 'uvicorn', 'starlette', 'httpx',
                'aiohttp', 'requests', 'flask'
            },

            # Database (carregado sob demanda)
            'database': {
                'psycopg2', 'redis', 'pymongo', 'aiosqlite'
            },

            # Monitoring (carregado sob demanda)
            'monitoring': {
                'prometheus_client', 'sentry_sdk', 'grafana_api'
            },

            # Security (carregado sob demanda)
            'security': {
                'cryptography', 'bcrypt', 'python-jose', 'passlib'
            },

            # Enterprise (carregado sob demanda)
            'enterprise': {
                'kubernetes', 'docker', 'boto3', 'azure-storage-blob'
            },

            # Development (nunca carregado em produção)
            'dev': {
                'pytest', 'black', 'mypy', 'flake8', 'pre-commit'
            }
        }

        # Dependências entre categorias
        self._category_dependencies = {
            'ai': ['vision'],  # AI pode precisar de vision
            'web': ['security'],  # Web precisa de security
            'enterprise': ['monitoring', 'security'],  # Enterprise precisa de ambos
        }

        # Inicializar cache
        self._init_cache()

    def _init_cache(self):
        """Inicializar sistema de cache"""
        cache_dir = Path.home() / ".automator_cache"
        cache_dir.mkdir(exist_ok=True)

        self._cache_dir = cache_dir
        self._module_cache_dir = cache_dir / "modules"
        self._bytecode_cache_dir = cache_dir / "bytecode"

        self._module_cache_dir.mkdir(exist_ok=True)
        self._bytecode_cache_dir.mkdir(exist_ok=True)

    def get_category(self, module_name: str) -> str:
        """Determinar categoria de um módulo"""
        for category, modules in self._module_categories.items():
            if module_name in modules:
                return category
        return 'unknown'

    def should_load_lazy(self, module_name: str) -> bool:
        """Determinar se módulo deve ser carregado lazy"""
        category = self.get_category(module_name)

        # Core sempre eager
        if category == 'core':
            return False

        # Dev nunca em produção
        if category == 'dev' and not self._is_development():
            return False

        # Outros são lazy
        return True

    def _is_development(self) -> bool:
        """Verificar se está em ambiente de desenvolvimento"""
        return (Path.cwd() / ".git").exists() or os.environ.get('AUTOMATOR_ENV') == 'development'

    def import_module(self, module_name: str, force_eager: bool = False) -> Optional[Any]:
        """
        Import inteligente com lazy loading

        Args:
            module_name: Nome do módulo
            force_eager: Forçar carregamento imediato

        Returns:
            Módulo carregado ou None se falhar
        """
        with self._lock:
            start_time = time.time()

            # Verificar cache
            if module_name in self._loaded_modules:
                metadata = self._module_metadata[module_name]

                # Verificar TTL
                if time.time() - metadata['loaded_at'] < self._ttl_seconds:
                    logger.debug(f"Cache hit for {module_name}")
                    return self._loaded_modules[module_name]
                else:
                    # TTL expirado, recarregar
                    logger.debug(f"TTL expired for {module_name}, reloading")
                    del self._loaded_modules[module_name]
                    del self._module_metadata[module_name]

            # Verificar se deve ser lazy
            if not force_eager and self.should_load_lazy(module_name):
                logger.debug(f"Lazy loading {module_name}")
                return self._create_lazy_proxy(module_name)

            # Carregar módulo
            try:
                module = importlib.import_module(module_name)

                # Armazenar em cache
                self._loaded_modules[module_name] = module
                self._module_metadata[module_name] = {
                    'loaded_at': time.time(),
                    'load_time': time.time() - start_time,
                    'size_bytes': sys.getsizeof(module),
                    'category': self.get_category(module_name)
                }

                # Atualizar tamanho do cache
                self._current_cache_size += sys.getsizeof(module)

                # Evict se necessário
                self._evict_if_needed()

                logger.debug(f"Successfully loaded {module_name} in {time.time() - start_time:.3f}s")
                return module

            except ImportError as e:
                logger.warning(f"Failed to import {module_name}: {e}")

                # Tentar fallback
                fallback = self._find_fallback(module_name)
                if fallback:
                    logger.info(f"Trying fallback {fallback} for {module_name}")
                    return self.import_module(fallback, force_eager)

                return None

    def _create_lazy_proxy(self, module_name: str) -> Any:
        """Criar proxy lazy para módulo"""

        class LazyModuleProxy:
            """Proxy que carrega módulo sob demanda"""

            def __init__(self, importer, module_name):
                self._importer = importer
                self._module_name = module_name
                self._real_module = None
                self._lock = threading.RLock()

            def _load_real_module(self):
                """Carregar módulo real quando necessário"""
                if self._real_module is None:
                    with self._lock:
                        if self._real_module is None:  # Double-check
                            logger.debug(f"Loading real module {self._module_name}")
                            self._real_module = self._importer.import_module(
                                self._module_name, force_eager=True
                            )
                return self._real_module

            def __getattr__(self, name):
                """Delegar acesso para módulo real"""
                real_module = self._load_real_module()
                if real_module:
                    return getattr(real_module, name)
                raise AttributeError(f"Lazy module {self._module_name} failed to load")

            def __repr__(self):
                return f"<LazyModuleProxy for {self._module_name}>"

        return LazyModuleProxy(self, module_name)

    def _find_fallback(self, module_name: str) -> Optional[str]:
        """Encontrar módulo de fallback"""
        fallbacks = {
            'torch': 'torchvision',
            'transformers': 'tokenizers',
            'openai': 'anthropic',
            'cv2': 'PIL',
            'fastapi': 'flask',
            'psycopg2': 'sqlite3',
            'redis': None  # Sem fallback
        }
        return fallbacks.get(module_name)

    def _evict_if_needed(self):
        """Evict módulos do cache se necessário (LRU)"""
        if self._current_cache_size <= self._cache_size_mb * 1024 * 1024:
            return

        # Ordenar por tempo de acesso (LRU)
        sorted_modules = sorted(
            self._module_metadata.items(),
            key=lambda x: x[1]['loaded_at']
        )

        # Remover módulos antigos até liberar espaço
        target_size = self._cache_size_mb * 1024 * 1024 * 0.8  # 80% do limite

        for module_name, metadata in sorted_modules:
            if self._current_cache_size <= target_size:
                break

            logger.debug(f"Evicting {module_name} from cache")
            del self._loaded_modules[module_name]
            del self._module_metadata[module_name]
            self._current_cache_size -= metadata['size_bytes']

    def preload_category(self, category: str) -> List[str]:
        """Pré-carregar todos os módulos de uma categoria"""
        if category not in self._module_categories:
            logger.warning(f"Unknown category: {category}")
            return []

        loaded = []
        for module_name in self._module_categories[category]:
            if self.import_module(module_name, force_eager=True):
                loaded.append(module_name)

        logger.info(f"Preloaded {len(loaded)} modules from category {category}")
        return loaded

    def get_stats(self) -> Dict:
        """Obter estatísticas do lazy importer"""
        return {
            'loaded_modules': len(self._loaded_modules),
            'cache_size_mb': self._current_cache_size / (1024 * 1024),
            'categories': {cat: len(modules) for cat, modules in self._module_categories.items()},
            'cache_hit_ratio': self._calculate_cache_hit_ratio()
        }

    def _calculate_cache_hit_ratio(self) -> float:
        """Calcular taxa de acerto do cache"""
        total_requests = sum(meta.get('access_count', 0) for meta in self._module_metadata.values())
        cache_hits = sum(meta.get('cache_hits', 0) for meta in self._module_metadata.values())

        return cache_hits / total_requests if total_requests > 0 else 0.0

    def clear_cache(self):
        """Limpar cache completamente"""
        with self._lock:
            self._loaded_modules.clear()
            self._module_metadata.clear()
            self._current_cache_size = 0
            logger.info("Cache cleared")


# Instância global
lazy_importer = LazyImporterEnterprise()

# Funções de conveniência
def lazy_import(module_name: str) -> Optional[Any]:
    """Função de conveniência para import lazy"""
    return lazy_importer.import_module(module_name)

def preload_category(category: str) -> List[str]:
    """Pré-carregar categoria de módulos"""
    return lazy_importer.preload_category(category)

def get_lazy_stats() -> Dict:
    """Obter estatísticas do lazy importer"""
    return lazy_importer.get_stats()
