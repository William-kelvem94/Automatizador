#!/usr/bin/env python3
"""
LAZY LOADING OPTIMIZATION v9.0 - Automator Web IA
Implementação completa de lazy loading enterprise-grade
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import importlib
import time
import threading
import weakref

class EnterpriseLazyLoader:
    """Lazy loader enterprise-grade com cache inteligente e monitoramento"""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._load_times: Dict[str, float] = {}
        self._failed_imports: List[str] = []
        self._module_dependencies: Dict[str, List[str]] = {}
        self._category_cache: Dict[str, Dict[str, Any]] = {}
        self._preload_cache: Dict[str, Any] = {}
        self._memory_monitor = MemoryMonitor()
        self._performance_monitor = PerformanceMonitor()

        # Configurações enterprise
        self._cache_size_limit = 100 * 1024 * 1024  # 100MB
        self._current_cache_size = 0
        self._preload_enabled = True
        self._monitoring_enabled = True

        # Categorias de módulos por domínio
        self._module_categories = {
            'ai': [
                'openai', 'anthropic', 'torch', 'transformers',
                'langchain', 'sentence_transformers', 'diffusers'
            ],
            'vision': [
                'cv2', 'PIL', 'numpy', 'scipy', 'scikit-image',
                'pytesseract', 'easyocr', 'opencv-contrib-python'
            ],
            'web': [
                'fastapi', 'uvicorn', 'starlette', 'httpx',
                'aiohttp', 'requests', 'selenium', 'playwright'
            ],
            'database': [
                'sqlalchemy', 'psycopg2', 'redis', 'pymongo',
                'alembic', 'sqlalchemy-utils'
            ],
            'monitoring': [
                'prometheus_client', 'sentry_sdk', 'loguru',
                'structlog', 'datadog', 'newrelic'
            ],
            'security': [
                'cryptography', 'bcrypt', 'python-jose',
                'oauthlib', 'authlib', 'pyjwt'
            ],
            'enterprise': [
                'kubernetes', 'docker', 'boto3', 'azure-storage-blob',
                'google-cloud-storage', 'stripe', 'sendgrid'
            ],
            'dev': [
                'pytest', 'black', 'mypy', 'flake8', 'isort',
                'coverage', 'tox', 'pre-commit'
            ]
        }

        # Dependências entre categorias
        self._category_dependencies = {
            'ai': ['vision'],  # AI pode precisar de vision
            'web': ['security'],  # Web precisa de security
            'enterprise': ['monitoring', 'security'],  # Enterprise precisa de ambos
        }

        # Inicializar monitoramento
        if self._monitoring_enabled:
            self._start_performance_monitoring()

    def import_module(self, module_name: str, category: Optional[str] = None,
                     force_reload: bool = False) -> Optional[Any]:
        """Import lazy com cache inteligente e métricas"""

        # Verificar cache primeiro
        if not force_reload and module_name in self._loaded_modules:
            return self._loaded_modules[module_name]

        # Verificar se já falhou
        if module_name in self._failed_imports:
            return None

        start_time = time.time()

        try:
            # Importar módulo
            module = importlib.import_module(module_name)

            # Registrar tempo de carregamento
            load_time = time.time() - start_time
            self._load_times[module_name] = load_time

            # Estimar tamanho do módulo
            module_size = self._estimate_module_size(module)

            # Verificar limites de cache
            if self._current_cache_size + module_size > self._cache_size_limit:
                self._evict_cache_entries(module_size)

            # Cache do módulo
            self._loaded_modules[module_name] = module
            self._current_cache_size += module_size

            # Log de sucesso com métricas
            print(f"📦 Lazy loaded: {module_name} ({load_time:.3f}s, {module_size/1024:.1f}KB)")

            # Atualizar métricas de performance
            if self._monitoring_enabled:
                self._performance_monitor.record_import(module_name, load_time, module_size)

            return module

        except ImportError as e:
            # Registrar falha
            self._failed_imports.append(module_name)

            # Log de falha
            print(f"⚠️  Lazy import failed: {module_name} - {e}")

            # Atualizar métricas de falha
            if self._monitoring_enabled:
                self._performance_monitor.record_failed_import(module_name, str(e))

            return None

        except Exception as e:
            print(f"❌ Lazy import error: {module_name} - {e}")
            return None

    def import_category(self, category: str, preload_dependencies: bool = True) -> Dict[str, Any]:
        """Importar todos os módulos de uma categoria"""

        if category not in self._module_categories:
            raise ValueError(f"Categoria não suportada: {category}")

        # Verificar cache de categoria
        if category in self._category_cache:
            return self._category_cache[category]

        results = {}

        # Importar dependências primeiro se solicitado
        if preload_dependencies and category in self._category_dependencies:
            for dep_category in self._category_dependencies[category]:
                print(f"🔗 Preloading dependency category: {dep_category}")
                self.import_category(dep_category, preload_dependencies=False)

        # Importar módulos da categoria
        modules = self._module_categories[category]

        for module_name in modules:
            module = self.import_module(module_name, category)
            if module:
                results[module_name] = module

        # Cache da categoria
        self._category_cache[category] = results

        print(f"📂 Category '{category}' loaded: {len(results)}/{len(modules)} modules")

        return results

    def preload_critical_modules(self):
        """Pré-carregar módulos críticos para performance"""

        critical_modules = [
            'src.shared.utils.logger',
            'src.shared.config.settings',
            'src.domain.entities.automation_task',
            'src.infrastructure.database.connection'
        ]

        print("🚀 Preloading critical modules...")

        for module in critical_modules:
            self.import_module(module)

        print("✅ Critical modules preloaded")

    def preload_category_async(self, category: str):
        """Pré-carregar categoria de forma assíncrona"""

        def preload_worker():
            try:
                self.import_category(category)
                print(f"✅ Async preload completed: {category}")
            except Exception as e:
                print(f"❌ Async preload failed: {category} - {e}")

        thread = threading.Thread(target=preload_worker, daemon=True)
        thread.start()

        return thread

    def get_performance_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de performance"""

        return {
            'total_loaded_modules': len(self._loaded_modules),
            'total_failed_imports': len(self._failed_imports),
            'cache_size_mb': self._current_cache_size / (1024 * 1024),
            'average_load_time': sum(self._load_times.values()) / max(len(self._load_times), 1),
            'slowest_modules': sorted(self._load_times.items(), key=lambda x: x[1], reverse=True)[:5],
            'memory_stats': self._memory_monitor.get_stats(),
            'performance_metrics': self._performance_monitor.get_stats() if self._monitoring_enabled else {}
        }

    def optimize_for_environment(self, environment: str):
        """Otimizar baseado no ambiente"""

        if environment == 'development':
            self._cache_size_limit = 200 * 1024 * 1024  # 200MB
            self._preload_enabled = False  # Menos preload em dev

        elif environment == 'production':
            self._cache_size_limit = 50 * 1024 * 1024   # 50MB
            self._preload_enabled = True   # Máximo preload em prod

        elif environment == 'enterprise':
            self._cache_size_limit = 100 * 1024 * 1024  # 100MB
            self._preload_enabled = True   # Enterprise features

        print(f"🔧 Optimized for environment: {environment}")

    def _estimate_module_size(self, module) -> int:
        """Estimar tamanho do módulo em bytes"""

        try:
            # Estimativa simples baseada em __dict__
            size = sys.getsizeof(module.__dict__)
            if hasattr(module, '__file__') and module.__file__:
                # Adicionar tamanho do arquivo se existir
                file_path = Path(module.__file__)
                if file_path.exists():
                    size += file_path.stat().st_size
            return size
        except:
            return 10240  # 10KB default

    def _evict_cache_entries(self, required_size: int):
        """Evicter entradas do cache para liberar espaço"""

        # Estratégia LRU baseada em tempo de carregamento
        sorted_modules = sorted(
            [(name, self._load_times.get(name, 0)) for name in self._loaded_modules.keys()],
            key=lambda x: x[1]  # Ordenar por tempo (mais recentes primeiro)
        )

        freed_space = 0
        modules_to_evict = []

        for module_name, _ in sorted_modules:
            if freed_space >= required_size:
                break

            module_size = self._estimate_module_size(self._loaded_modules[module_name])
            freed_space += module_size
            modules_to_evict.append(module_name)

        # Remover módulos
        for module_name in modules_to_evict:
            if module_name in self._loaded_modules:
                del self._loaded_modules[module_name]
                print(f"🗑️  Cache evicted: {module_name}")

        self._current_cache_size -= freed_space

    def _start_performance_monitoring(self):
        """Iniciar monitoramento de performance"""

        def monitor_worker():
            while True:
                try:
                    # Coletar métricas periodicamente
                    self._performance_monitor.collect_system_metrics()
                    time.sleep(30)  # A cada 30 segundos
                except Exception as e:
                    print(f"Performance monitoring error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=monitor_worker, daemon=True)
        thread.start()

        print("📊 Performance monitoring started")

class MemoryMonitor:
    """Monitor de uso de memória"""

    def __init__(self):
        self.samples = []

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de memória"""

        try:
            import psutil
            process = psutil.Process()

            current_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_percent = process.memory_percent()

            return {
                'current_mb': current_memory,
                'percent': memory_percent,
                'samples_count': len(self.samples)
            }
        except ImportError:
            return {'error': 'psutil not available'}

class PerformanceMonitor:
    """Monitor de performance detalhado"""

    def __init__(self):
        self.import_metrics = []
        self.system_metrics = []
        self.failed_imports = []

    def record_import(self, module_name: str, load_time: float, size: int):
        """Registrar métrica de import"""

        self.import_metrics.append({
            'module': module_name,
            'load_time': load_time,
            'size': size,
            'timestamp': time.time()
        })

    def record_failed_import(self, module_name: str, error: str):
        """Registrar import falhado"""

        self.failed_imports.append({
            'module': module_name,
            'error': error,
            'timestamp': time.time()
        })

    def collect_system_metrics(self):
        """Coletar métricas do sistema"""

        try:
            import psutil
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            self.system_metrics.append(metrics)
        except ImportError:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de performance"""

        if not self.import_metrics:
            return {}

        load_times = [m['load_time'] for m in self.import_metrics]

        return {
            'total_imports': len(self.import_metrics),
            'avg_load_time': sum(load_times) / len(load_times),
            'slowest_import': max(self.import_metrics, key=lambda x: x['load_time']),
            'fastest_import': min(self.import_metrics, key=lambda x: x['load_time']),
            'failed_imports': len(self.failed_imports),
            'total_size_loaded': sum(m['size'] for m in self.import_metrics)
        }

# Instância global enterprise
enterprise_lazy_loader = EnterpriseLazyLoader()

# Funções de conveniência
def lazy_import(module_name: str, category: Optional[str] = None) -> Optional[Any]:
    """Função de conveniência para import lazy enterprise"""
    return enterprise_lazy_loader.import_module(module_name, category)

def import_ai_modules():
    """Importar módulos de IA"""
    return enterprise_lazy_loader.import_category('ai')

def import_vision_modules():
    """Importar módulos de visão"""
    return enterprise_lazy_loader.import_category('vision')

def preload_critical():
    """Pré-carregar módulos críticos"""
    enterprise_lazy_loader.preload_critical_modules()

def get_performance_stats():
    """Obter estatísticas de performance"""
    return enterprise_lazy_loader.get_performance_stats()

def optimize_for_environment(env: str):
    """Otimizar para ambiente específico"""
    enterprise_lazy_loader.optimize_for_environment(env)

if __name__ == "__main__":
    # Demonstração do lazy loader enterprise
    print("🚀 DEMONSTRAÇÃO - ENTERPRISE LAZY LOADER v9.0")
    print("=" * 60)

    # Otimizar para desenvolvimento
    optimize_for_environment('development')

    # Pré-carregar módulos críticos
    preload_critical()

    # Testar import de categoria
    print("\n🔍 Testando import de categoria AI...")
    ai_modules = import_ai_modules()

    print(f"📊 Módulos AI carregados: {len(ai_modules)}")

    # Testar import individual
    print("\n🔍 Testando import individual...")
    torch_module = lazy_import('torch', 'ai')
    if torch_module:
        print("✅ PyTorch carregado com sucesso")
    else:
        print("⚠️  PyTorch não disponível (opcional)")

    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS:")
    stats = get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Enterprise Lazy Loader demonstrado com sucesso!")
    print("🎯 Pronto para otimização de performance v9.0!")
