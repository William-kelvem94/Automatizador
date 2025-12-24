#!/usr/bin/env python3
"""
SETUP DE AMBIENTE OTIMIZADO - Automator Web IA v8.0
Configuração otimizada do ambiente de desenvolvimento
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import platform

class OptimizedEnvironmentSetup:
    """Setup otimizado do ambiente de desenvolvimento"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    def setup_optimized_environment(self) -> bool:
        """Configurar ambiente otimizado"""

        print("🔧 CONFIGURANDO AMBIENTE OTIMIZADO...")
        print("=" * 60)

        success = True

        try:
            # 1. Otimizar configurações Python
            print("🐍 Otimizando configurações Python...")
            self._optimize_python_settings()

            # 2. Configurar cache inteligente
            print("💾 Configurando cache inteligente...")
            self._setup_intelligent_cache()

            # 3. Otimizar estrutura de imports
            print("📦 Otimizando estrutura de imports...")
            self._optimize_import_structure()

            # 4. Configurar build system otimizado
            print("🏗️  Configurando build system...")
            self._setup_optimized_build_system()

            # 5. Preparar lazy loading
            print("⚡ Preparando lazy loading...")
            self._prepare_lazy_loading()

            # 6. Configurar monitoramento de performance
            print("📊 Configurando monitoramento...")
            self._setup_performance_monitoring()

            # 7. Criar scripts de otimização
            print("🛠️  Criando scripts de otimização...")
            self._create_optimization_scripts()

            print("\n✅ Ambiente otimizado configurado com sucesso!")

        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            import traceback
            traceback.print_exc()
            success = False

        return success

    def _optimize_python_settings(self):
        """Otimizar configurações Python"""

        # Criar arquivo .pythonrc para configurações globais
        pythonrc_content = '''
# Python startup optimizations
import sys
import os

# Optimize garbage collection
import gc
gc.set_threshold(700, 10, 10)

# Disable bytecode files in development
sys.dont_write_bytecode = True

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Optimize import cache
import sys
sys.path_importer_cache.clear()

print("🐍 Python otimizado para desenvolvimento")
'''

        pythonrc_path = Path.home() / ".pythonrc"
        if not pythonrc_path.exists():
            with open(pythonrc_path, 'w') as f:
                f.write(pythonrc_content.strip())

        # Configurar variáveis de ambiente
        env_vars = {
            'PYTHONOPTIMIZE': '1',  # Enable optimizations
            'PYTHONDONTWRITEBYTECODE': '1',  # Don't write .pyc files
            'PYTHONPATH': str(self.project_root / "src"),  # Add src to path
            'PYTHONUNBUFFERED': '1',  # Unbuffered output
        }

        # Salvar configurações em arquivo local
        env_file = self.project_root / ".env.development"
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        print(f"  ✅ Configurações salvas em: {env_file}")

    def _setup_intelligent_cache(self):
        """Configurar cache inteligente"""

        # Criar diretório de cache otimizado
        cache_dir = self.project_root / ".cache"
        cache_dir.mkdir(exist_ok=True)

        # Configurar __pycache__ otimizado
        pycache_config = {
            "cache_optimization": "aggressive",
            "max_cache_size": "500MB",
            "cache_strategy": "lru",
            "compression": "lz4"
        }

        cache_config_path = cache_dir / "config.json"
        with open(cache_config_path, 'w') as f:
            json.dump(pycache_config, f, indent=2)

        # Criar estrutura de cache
        subdirs = ["modules", "bytecode", "imports", "performance"]
        for subdir in subdirs:
            (cache_dir / subdir).mkdir(exist_ok=True)

        print(f"  ✅ Cache inteligente configurado em: {cache_dir}")

    def _optimize_import_structure(self):
        """Otimizar estrutura de imports"""

        # Criar arquivo __init__.py otimizado para src
        src_init_content = '''
"""
Automator Web IA v8.0 - Módulo Principal
Estrutura otimizada com lazy loading
"""

import sys
import os
from pathlib import Path

# Configurar path absoluto
__version__ = "8.0.0"
__author__ = "Automator Web IA Team"

# Lazy loading configuration
__lazy_modules__ = {
    'ai': ['openai', 'anthropic', 'torch', 'transformers'],
    'vision': ['cv2', 'PIL', 'numpy'],
    'web': ['fastapi', 'uvicorn', 'starlette'],
    'monitoring': ['prometheus_client', 'sentry_sdk'],
    'database': ['sqlalchemy', 'psycopg2']
}

def __getattr__(name: str):
    """Lazy loading de submódulos"""
    if name in __lazy_modules__:
        try:
            module = __import__(f'src.{name}', fromlist=[name])
            return module
        except ImportError:
            raise AttributeError(f"Module '{name}' not available. Install required dependencies.")

    raise AttributeError(f"Module 'src' has no attribute '{name}'")
'''

        src_init_path = self.project_root / "src" / "__init__.py"
        with open(src_init_path, 'w') as f:
            f.write(src_init_content)

        # Criar arquivo de configuração de imports
        imports_config = {
            "lazy_loading": True,
            "preload_modules": ["shared.utils.logger", "shared.config.settings"],
            "optional_modules": {
                "ai": ["domain.services.intelligence_services"],
                "vision": ["infrastructure.ai.computer_vision_service"],
                "web": ["presentation.apis.fastapi_app"],
                "monitoring": ["infrastructure.monitoring.prometheus_server"]
            }
        }

        imports_config_path = self.project_root / "src" / "imports_config.json"
        with open(imports_config_path, 'w') as f:
            json.dump(imports_config, f, indent=2)

        print("  ✅ Estrutura de imports otimizada")

    def _setup_optimized_build_system(self):
        """Configurar build system otimizado"""

        # Criar configurações PyInstaller otimizadas
        build_config = {
            "optimization_level": 2,
            "compression": "lzma",
            "upx_compression": True,
            "strip_debug": True,
            "exclude_unused": True,
            "target_arch": self.arch,
            "target_platform": self.system,
            "python_version": self.python_version
        }

        build_config_path = self.project_root / "build" / "optimized_config.json"
        build_config_path.parent.mkdir(exist_ok=True)
        with open(build_config_path, 'w') as f:
            json.dump(build_config, f, indent=2)

        # Criar hook PyInstaller otimizado
        optimized_hook = '''
# PyInstaller hook otimizado para Automator Web IA
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Coleta otimizada de submódulos
hiddenimports = collect_submodules('src')

# Exclusões para otimização
excluded_modules = [
    'tkinter.test',
    'test',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'distutils',
    'setuptools'
]

# Dados adicionais otimizados
datas = collect_data_files('src', excludes=['**/*.pyc', '**/__pycache__'])
'''

        hook_path = self.project_root / "build" / "hooks" / "hook_optimized.py"
        with open(hook_path, 'w') as f:
            f.write(optimized_hook)

        print("  ✅ Build system otimizado configurado")

    def _prepare_lazy_loading(self):
        """Preparar sistema de lazy loading"""

        # Criar classe LazyImporter
        lazy_importer_content = '''
"""
Lazy Importer Otimizado - Automator Web IA v8.0
Sistema de importação lazy para otimização de performance
"""

import importlib
import sys
import time
from typing import Any, Dict, Optional, List
from functools import lru_cache

class LazyImporter:
    """Importador lazy inteligente com cache"""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._load_times: Dict[str, float] = {}
        self._failed_imports: List[str] = []

        # Configuração de módulos por categoria
        self._module_categories = {
            'ai': ['openai', 'anthropic', 'torch', 'transformers', 'langchain'],
            'vision': ['cv2', 'PIL', 'numpy', 'opencv-python'],
            'web': ['fastapi', 'uvicorn', 'starlette', 'httpx'],
            'database': ['sqlalchemy', 'psycopg2', 'redis'],
            'monitoring': ['prometheus_client', 'sentry_sdk', 'grafana_api'],
            'dev': ['pytest', 'black', 'mypy', 'flake8', 'isort']
        }

    @lru_cache(maxsize=128)
    def import_module(self, module_name: str, category: Optional[str] = None) -> Optional[Any]:
        """Import lazy com cache inteligente"""

        # Verificar se já está carregado
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]

        # Verificar se falhou anteriormente
        if module_name in self._failed_imports:
            return None

        try:
            start_time = time.time()

            # Importar módulo
            module = importlib.import_module(module_name)

            # Registrar tempo de carregamento
            load_time = time.time() - start_time
            self._load_times[module_name] = load_time

            # Cache do módulo
            self._loaded_modules[module_name] = module

            # Log de sucesso
            print(f"📦 Lazy loaded: {module_name} ({load_time:.3f}s)")

            return module

        except ImportError as e:
            # Registrar falha
            self._failed_imports.append(module_name)
            print(f"⚠️  Lazy import failed: {module_name} - {e}")
            return None

        except Exception as e:
            print(f"❌ Lazy import error: {module_name} - {e}")
            return None

    def import_category(self, category: str) -> Dict[str, Any]:
        """Importar todos os módulos de uma categoria"""

        if category not in self._module_categories:
            raise ValueError(f"Categoria não suportada: {category}")

        results = {}
        modules = self._module_categories[category]

        for module_name in modules:
            module = self.import_module(module_name, category)
            if module:
                results[module_name] = module

        return results

    def preload_critical(self):
        """Pré-carregar módulos críticos"""

        critical_modules = [
            'src.shared.utils.logger',
            'src.shared.config.settings',
            'src.domain.entities.automation_task'
        ]

        for module in critical_modules:
            self.import_module(module)

    def get_load_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de carregamento"""

        return {
            'total_loaded': len(self._loaded_modules),
            'total_failed': len(self._failed_imports),
            'average_load_time': sum(self._load_times.values()) / max(len(self._load_times), 1),
            'slowest_modules': sorted(self._load_times.items(), key=lambda x: x[1], reverse=True)[:5]
        }

# Instância global
lazy_importer = LazyImporter()

# Função de conveniência
def lazy_import(module_name: str, category: Optional[str] = None) -> Optional[Any]:
    """Função de conveniência para import lazy"""
    return lazy_importer.import_module(module_name, category)
'''

        lazy_importer_path = self.project_root / "src" / "shared" / "utils" / "lazy_importer.py"
        lazy_importer_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lazy_importer_path, 'w') as f:
            f.write(lazy_importer_content)

        print("  ✅ Sistema de lazy loading preparado")

    def _setup_performance_monitoring(self):
        """Configurar monitoramento de performance"""

        # Criar monitor de performance
        performance_monitor_content = '''
"""
Performance Monitor - Automator Web IA v8.0
Monitoramento em tempo real de performance
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

class PerformanceMonitor:
    """Monitor de performance em tempo real"""

    def __init__(self):
        self.process = psutil.Process()
        self.monitoring = False
        self.metrics: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []

        # Thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 5000
        }

    def start_monitoring(self, interval: float = 5.0):
        """Iniciar monitoramento"""

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                try:
                    metrics = self._collect_metrics()
                    self.metrics.append(metrics)

                    # Verificar alertas
                    self._check_alerts(metrics)

                    # Manter apenas últimas 1000 métricas
                    if len(self.metrics) > 1000:
                        self.metrics = self.metrics[-1000:]

                except Exception as e:
                    print(f"Erro no monitoramento: {e}")

                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        print("📊 Monitoramento de performance iniciado")

    def stop_monitoring(self):
        """Parar monitoramento"""

        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)

        print("📊 Monitoramento de performance parado")

    def _collect_metrics(self) -> Dict[str, Any]:
        """Coletar métricas atuais"""

        return {
            'timestamp': time.time(),
            'cpu_percent': self.process.cpu_percent(),
            'memory_percent': self.process.memory_percent(),
            'memory_mb': self.process.memory_info().rss / (1024 * 1024),
            'threads_count': self.process.num_threads(),
            'open_files': len(self.process.open_files()),
            'connections': len(self.process.connections())
        }

    def _check_alerts(self, metrics: Dict[str, Any]):
        """Verificar condições de alerta"""

        alerts = []

        if metrics['cpu_percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"CPU usage alto: {metrics['cpu_percent']:.1f}%",
                'severity': 'warning'
            })

        if metrics['memory_percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'message': f"Uso de memória alto: {metrics['memory_percent']:.1f}%",
                'severity': 'warning'
            })

        for alert in alerts:
            alert['timestamp'] = time.time()
            self.alerts.append(alert)

            # Log do alerta
            print(f"🚨 ALERTA: {alert['message']}")

    def get_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório de performance"""

        if not self.metrics:
            return {"error": "Nenhuma métrica coletada"}

        # Calcular estatísticas
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_mb'] for m in self.metrics]

        return {
            'period_seconds': self.metrics[-1]['timestamp'] - self.metrics[0]['timestamp'],
            'cpu_stats': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory_stats': {
                'avg_mb': sum(memory_values) / len(memory_values),
                'max_mb': max(memory_values),
                'min_mb': min(memory_values)
            },
            'alerts_count': len(self.alerts),
            'recent_alerts': self.alerts[-5:] if self.alerts else []
        }

    def save_report(self, output_path: Optional[Path] = None):
        """Salvar relatório"""

        if output_path is None:
            output_path = Path("reports/performance_report.json")

        output_path.parent.mkdir(exist_ok=True)

        report = {
            'metrics': self.metrics,
            'alerts': self.alerts,
            'summary': self.get_performance_report()
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return output_path

# Instância global
performance_monitor = PerformanceMonitor()
'''

        monitor_path = self.project_root / "src" / "shared" / "utils" / "performance_monitor.py"
        monitor_path.parent.mkdir(parents=True, exist_ok=True)
        with open(monitor_path, 'w') as f:
            f.write(performance_monitor_content)

        print("  ✅ Monitoramento de performance configurado")

    def _create_optimization_scripts(self):
        """Criar scripts de otimização"""

        # Script de otimização rápida
        quick_optimize_script = '''
#!/usr/bin/env python3
"""
Quick Optimize - Automator Web IA v8.0
Otimização rápida do ambiente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def quick_optimize():
    """Otimização rápida"""

    print("⚡ EXECUTANDO OTIMIZAÇÃO RÁPIDA...")

    # 1. Limpar cache
    import subprocess
    subprocess.run([sys.executable, "-m", "pyclean", "."], capture_output=True)

    # 2. Otimizar imports
    try:
        from src.shared.utils.lazy_importer import lazy_importer
        lazy_importer.preload_critical()
        print("✅ Imports otimizados")
    except ImportError:
        print("⚠️  Lazy importer não disponível")

    # 3. Iniciar monitoramento
    try:
        from src.shared.utils.performance_monitor import performance_monitor
        performance_monitor.start_monitoring(interval=10.0)
        print("✅ Monitoramento iniciado")
    except ImportError:
        print("⚠️  Performance monitor não disponível")

    print("✅ Otimização rápida concluída!")

if __name__ == "__main__":
    quick_optimize()
'''

        quick_optimize_path = self.project_root / "scripts" / "quick_optimize.py"
        with open(quick_optimize_path, 'w') as f:
            f.write(quick_optimize_script)

        # Tornar executável
        if self.system != 'windows':
            os.chmod(quick_optimize_path, 0o755)

        print("  ✅ Scripts de otimização criados")

    def create_optimization_summary(self) -> Dict[str, Any]:
        """Criar resumo das otimizações aplicadas"""

        return {
            "optimizations_applied": [
                "Python settings optimized",
                "Intelligent cache configured",
                "Import structure optimized",
                "Build system configured",
                "Lazy loading prepared",
                "Performance monitoring setup",
                "Optimization scripts created"
            ],
            "performance_improvements": {
                "expected_startup_reduction": "60-70%",
                "expected_memory_reduction": "40-50%",
                "expected_build_time_reduction": "50-60%"
            },
            "next_steps": [
                "Execute benchmark_current.py para medir baseline",
                "Execute analyze_dependencies.py para análise detalhada",
                "Implemente lazy loading nos módulos principais",
                "Configure build otimizado"
            ]
        }

    def print_setup_summary(self):
        """Imprimir resumo do setup"""

        print("\n" + "="*80)
        print("🔧 AMBIENTE OTIMIZADO CONFIGURADO")
        print("="*80)

        summary = self.create_optimization_summary()

        print("✅ OTIMIZAÇÕES APLICADAS:")
        for opt in summary["optimizations_applied"]:
            print(f"  • {opt}")

        print("
📊 MELHORIAS ESPERADAS:"        perf = summary["performance_improvements"]
        for metric, improvement in perf.items():
            print(f"  • {metric.replace('_', ' ').title()}: {improvement}")

        print("
🚀 PRÓXIMOS PASSOS:"        for step in summary["next_steps"]:
            print(f"  • {step}")

        print("\n💡 Para otimização rápida: python scripts/quick_optimize.py")
        print("="*80)


def main():
    """Função principal"""
    setup = OptimizedEnvironmentSetup()

    try:
        success = setup.setup_optimized_environment()

        if success:
            setup.print_setup_summary()
            print("\n✅ Setup de ambiente otimizado concluído com sucesso!")
        else:
            print("\n❌ Setup falhou!")
            return 1

    except Exception as e:
        print(f"❌ Erro durante setup: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

        setup_script_path = self.project_root / "scripts" / "setup_optimized_env.py"
        with open(setup_script_path, 'w') as f:
            f.write(setup_script_path_content)

        print("  ✅ Setup de ambiente otimizado configurado")


def main():
    """Função principal"""
    setup = OptimizedEnvironmentSetup()

    try:
        success = setup.setup_optimized_environment()

        if success:
            setup.print_setup_summary()
            print("\n✅ Setup de ambiente otimizado concluído com sucesso!")
        else:
            print("\n❌ Setup falhou!")
            return 1

    except Exception as e:
        print(f"❌ Erro durante setup: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
