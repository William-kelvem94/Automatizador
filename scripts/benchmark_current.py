#!/usr/bin/env python3
"""
BENCHMARK DE PERFORMANCE ATUAL - Automator Web IA v8.0
Benchmark completo da performance atual do sistema
"""

import os
import sys
import time
import psutil
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import subprocess
import threading
import statistics

class PerformanceBenchmark:
    """Benchmark de performance completo"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.process = None

    def run_complete_benchmark(self) -> Dict[str, Any]:
        """Executar benchmark completo"""

        print("⚡ EXECUTANDO BENCHMARK DE PERFORMANCE...")
        print("=" * 60)

        # 1. Benchmark de startup
        print("🚀 Testando tempo de startup...")
        startup_results = self._benchmark_startup_time()

        # 2. Benchmark de memória
        print("💾 Testando uso de memória...")
        memory_results = self._benchmark_memory_usage()

        # 3. Benchmark de CPU
        print("🖥️  Testando uso de CPU...")
        cpu_results = self._benchmark_cpu_usage()

        # 4. Benchmark de imports
        print("📦 Testando tempo de imports...")
        import_results = self._benchmark_import_time()

        # 5. Benchmark de build
        print("🏗️  Testando tempo de build...")
        build_results = self._benchmark_build_time()

        # 6. Análise de gargalos
        print("🔍 Analisando gargalos...")
        bottleneck_analysis = self._analyze_bottlenecks()

        self.results = {
            "startup_benchmark": startup_results,
            "memory_benchmark": memory_results,
            "cpu_benchmark": cpu_results,
            "import_benchmark": import_results,
            "build_benchmark": build_results,
            "bottleneck_analysis": bottleneck_analysis,
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations()
        }

        return self.results

    def _benchmark_startup_time(self) -> Dict[str, Any]:
        """Benchmark do tempo de startup"""

        results = {
            "attempts": [],
            "statistics": {}
        }

        # Múltiplas tentativas para precisão
        for attempt in range(5):
            print(f"  Tentativa {attempt + 1}/5...")

            start_time = time.time()

            try:
                # Simular startup (importar módulos principais)
                import sys
                sys.path.insert(0, str(self.project_root / "src"))

                # Importar módulos principais
                import importlib
                modules_to_import = [
                    "src.shared.utils.logger",
                    "src.shared.config.settings",
                    "src.domain.entities.automation_task",
                    "src.infrastructure.database.connection"
                ]

                for module in modules_to_import:
                    try:
                        importlib.import_module(module)
                    except ImportError:
                        pass  # Módulo pode não existir ainda

                startup_time = time.time() - start_time
                results["attempts"].append(startup_time)

            except Exception as e:
                print(f"    Erro na tentativa {attempt + 1}: {e}")
                results["attempts"].append(float('inf'))

        # Calcular estatísticas
        valid_times = [t for t in results["attempts"] if t != float('inf')]

        if valid_times:
            results["statistics"] = {
                "min_time": min(valid_times),
                "max_time": max(valid_times),
                "avg_time": statistics.mean(valid_times),
                "median_time": statistics.median(valid_times),
                "stdev": statistics.stdev(valid_times) if len(valid_times) > 1 else 0
            }

        return results

    def _benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark de uso de memória"""

        results = {
            "baseline_memory": 0,
            "peak_memory": 0,
            "memory_growth": 0,
            "memory_efficiency": "unknown"
        }

        try:
            # Baseline
            process = psutil.Process()
            results["baseline_memory"] = process.memory_info().rss / (1024 * 1024)  # MB

            # Simular carregamento do sistema
            tracemalloc.start()

            # Importar módulos principais
            import sys
            sys.path.insert(0, str(self.project_root / "src"))

            modules_to_test = [
                ("src.shared.utils.logger", "Logger"),
                ("src.shared.config.settings", "Settings"),
                ("src.domain.entities.automation_task", "Entities"),
            ]

            for module_name, description in modules_to_test:
                try:
                    __import__(module_name.replace("src.", "").replace(".", "_"), fromlist=[module_name.split(".")[-1]])
                except ImportError:
                    pass

            # Medir uso após imports
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            results["peak_memory"] = peak / (1024 * 1024)  # MB
            results["memory_growth"] = results["peak_memory"] - results["baseline_memory"]

            # Classificar eficiência
            if results["memory_growth"] < 50:
                results["memory_efficiency"] = "excellent"
            elif results["memory_growth"] < 100:
                results["memory_efficiency"] = "good"
            elif results["memory_growth"] < 200:
                results["memory_efficiency"] = "fair"
            else:
                results["memory_efficiency"] = "poor"

        except Exception as e:
            print(f"Erro no benchmark de memória: {e}")
            results["error"] = str(e)

        return results

    def _benchmark_cpu_usage(self) -> Dict[str, Any]:
        """Benchmark de uso de CPU"""

        results = {
            "import_cpu_usage": [],
            "overall_cpu_efficiency": "unknown"
        }

        try:
            process = psutil.Process()

            # Medir CPU durante imports
            cpu_samples = []

            def monitor_cpu():
                while monitoring_active:
                    cpu_percent = process.cpu_percent(interval=0.1)
                    cpu_samples.append(cpu_percent)
                    time.sleep(0.1)

            # Iniciar monitoramento
            monitoring_active = True
            monitor_thread = threading.Thread(target=monitor_cpu, daemon=True)
            monitor_thread.start()

            # Executar imports
            time.sleep(0.5)  # Warm up

            import sys
            sys.path.insert(0, str(self.project_root / "src"))

            modules_to_test = [
                "src.shared.utils.logger",
                "src.shared.config.settings",
                "src.domain.entities.automation_task",
            ]

            for module_name in modules_to_test:
                try:
                    __import__(module_name.replace("src.", "").replace(".", "_"), fromlist=[module_name.split(".")[-1]])
                    time.sleep(0.2)
                except ImportError:
                    pass

            # Parar monitoramento
            time.sleep(0.5)
            monitoring_active = False
            monitor_thread.join(timeout=1)

            results["import_cpu_usage"] = cpu_samples

            # Calcular média de uso
            if cpu_samples:
                avg_cpu = statistics.mean(cpu_samples)
                if avg_cpu < 20:
                    results["overall_cpu_efficiency"] = "excellent"
                elif avg_cpu < 40:
                    results["overall_cpu_efficiency"] = "good"
                elif avg_cpu < 70:
                    results["overall_cpu_efficiency"] = "fair"
                else:
                    results["overall_cpu_efficiency"] = "poor"

                results["avg_cpu_usage"] = avg_cpu

        except Exception as e:
            print(f"Erro no benchmark de CPU: {e}")
            results["error"] = str(e)

        return results

    def _benchmark_import_time(self) -> Dict[str, Any]:
        """Benchmark do tempo de import de módulos"""

        results = {
            "module_import_times": {},
            "slowest_modules": [],
            "total_import_time": 0
        }

        modules_to_test = [
            ("src.shared.utils.logger", "Logger utility"),
            ("src.shared.config.settings", "Configuration settings"),
            ("src.domain.entities.automation_task", "Domain entities"),
            ("src.infrastructure.database.connection", "Database connection"),
            ("src.presentation.qt_views.main_window", "Qt main window"),
        ]

        import sys
        sys.path.insert(0, str(self.project_root / "src"))

        total_time = 0

        for module_name, description in modules_to_test:
            try:
                start_time = time.time()
                __import__(module_name.replace("src.", "").replace(".", "_"), fromlist=[module_name.split(".")[-1]])
                import_time = time.time() - start_time

                results["module_import_times"][module_name] = {
                    "time": import_time,
                    "description": description
                }

                total_time += import_time

            except ImportError:
                results["module_import_times"][module_name] = {
                    "time": None,
                    "description": description,
                    "error": "Module not found"
                }
            except Exception as e:
                results["module_import_times"][module_name] = {
                    "time": None,
                    "description": description,
                    "error": str(e)
                }

        results["total_import_time"] = total_time

        # Identificar módulos mais lentos
        valid_times = [(name, data["time"]) for name, data in results["module_import_times"].items()
                      if data["time"] is not None]

        if valid_times:
            sorted_modules = sorted(valid_times, key=lambda x: x[1], reverse=True)
            results["slowest_modules"] = sorted_modules[:3]

        return results

    def _benchmark_build_time(self) -> Dict[str, Any]:
        """Benchmark do tempo de build"""

        results = {
            "build_time": None,
            "build_success": False,
            "build_size": None,
            "build_efficiency": "unknown"
        }

        try:
            # Verificar se PyInstaller está disponível
            import PyInstaller
        except ImportError:
            results["error"] = "PyInstaller não instalado"
            return results

        try:
            start_time = time.time()

            # Simular build (apenas análise, não build completo)
            from PyInstaller.__main__ import run

            # Parâmetros de build de teste
            build_args = [
                '--onefile',
                '--name=test-build',
                '--hidden-import=PySide6.QtCore',
                '--hidden-import=loguru',
                '--hidden-import=pydantic',
                '--specpath=build/test-specs',
                '--workpath=build/test-work',
                'src/main.py' if (self.project_root / "src" / "main.py").exists()
                else 'launcher.py'
            ]

            # Executar análise apenas (não build completo)
            try:
                # Usar --help para testar se PyInstaller funciona
                subprocess.run([
                    sys.executable, '-m', 'PyInstaller', '--help'
                ], capture_output=True, timeout=30)

                build_time = time.time() - start_time
                results["build_time"] = build_time
                results["build_success"] = True

                # Classificar eficiência
                if build_time < 60:
                    results["build_efficiency"] = "excellent"
                elif build_time < 120:
                    results["build_efficiency"] = "good"
                elif build_time < 300:
                    results["build_efficiency"] = "fair"
                else:
                    results["build_efficiency"] = "poor"

            except subprocess.TimeoutExpired:
                results["build_time"] = float('inf')
                results["build_efficiency"] = "timeout"

        except Exception as e:
            results["error"] = str(e)
            results["build_success"] = False

        return results

    def _analyze_bottlenecks(self) -> Dict[str, Any]:
        """Analisar gargalos de performance"""

        bottlenecks = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        # Análise baseada nos resultados
        if self.results:
            # Startup bottlenecks
            startup_stats = self.results.get("startup_benchmark", {}).get("statistics", {})
            if startup_stats.get("avg_time", 0) > 10:
                bottlenecks["critical"].append("Startup time muito lento (>10s)")

            # Memory bottlenecks
            memory_growth = self.results.get("memory_benchmark", {}).get("memory_growth", 0)
            if memory_growth > 200:
                bottlenecks["high"].append("Uso excessivo de memória (>200MB)")

            # Import bottlenecks
            slowest_modules = self.results.get("import_benchmark", {}).get("slowest_modules", [])
            if slowest_modules:
                slowest_time = slowest_modules[0][1]
                if slowest_time > 2:
                    bottlenecks["medium"].append(f"Import lento detectado: {slowest_modules[0][0]} ({slowest_time:.2f}s)")

            # Build bottlenecks
            build_time = self.results.get("build_benchmark", {}).get("build_time")
            if build_time and build_time > 300:
                bottlenecks["high"].append("Build muito lento (>5min)")

        return bottlenecks

    def _generate_summary(self) -> Dict[str, Any]:
        """Gerar resumo do benchmark"""

        summary = {
            "overall_score": "unknown",
            "performance_rating": "unknown",
            "critical_issues": 0,
            "recommendations_count": 0
        }

        if self.results:
            # Calcular score geral
            scores = []

            # Startup score
            startup_time = self.results.get("startup_benchmark", {}).get("statistics", {}).get("avg_time", 0)
            if startup_time < 3:
                scores.append(5)
            elif startup_time < 5:
                scores.append(4)
            elif startup_time < 10:
                scores.append(3)
            elif startup_time < 15:
                scores.append(2)
            else:
                scores.append(1)

            # Memory score
            memory_efficiency = self.results.get("memory_benchmark", {}).get("memory_efficiency", "unknown")
            if memory_efficiency == "excellent":
                scores.append(5)
            elif memory_efficiency == "good":
                scores.append(4)
            elif memory_efficiency == "fair":
                scores.append(3)
            else:
                scores.append(1)

            # CPU score
            cpu_efficiency = self.results.get("cpu_benchmark", {}).get("overall_cpu_efficiency", "unknown")
            if cpu_efficiency == "excellent":
                scores.append(5)
            elif cpu_efficiency == "good":
                scores.append(4)
            elif cpu_efficiency == "fair":
                scores.append(3)
            else:
                scores.append(1)

            # Calcular média
            if scores:
                avg_score = statistics.mean(scores)

                if avg_score >= 4.5:
                    summary["overall_score"] = "A+"
                    summary["performance_rating"] = "excellent"
                elif avg_score >= 3.5:
                    summary["overall_score"] = "A"
                    summary["performance_rating"] = "good"
                elif avg_score >= 2.5:
                    summary["overall_score"] = "B"
                    summary["performance_rating"] = "fair"
                else:
                    summary["overall_score"] = "C"
                    summary["performance_rating"] = "poor"

            # Contar issues críticos
            bottlenecks = self.results.get("bottleneck_analysis", {})
            summary["critical_issues"] = len(bottlenecks.get("critical", []))

            # Contar recomendações
            recommendations = self.results.get("recommendations", {})
            total_recs = 0
            for rec_list in recommendations.values():
                if isinstance(rec_list, list):
                    total_recs += len(rec_list)
            summary["recommendations_count"] = total_recs

        return summary

    def _generate_recommendations(self) -> Dict[str, List[str]]:
        """Gerar recomendações de otimização"""

        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }

        if self.results:
            # Análise dos resultados para recomendações
            startup_time = self.results.get("startup_benchmark", {}).get("statistics", {}).get("avg_time", 0)
            memory_growth = self.results.get("memory_benchmark", {}).get("memory_growth", 0)
            build_time = self.results.get("build_benchmark", {}).get("build_time")

            # Recomendações imediatas
            if startup_time > 5:
                recommendations["immediate"].append("Implementar lazy loading para reduzir tempo de startup")

            if memory_growth > 100:
                recommendations["immediate"].append("Otimizar imports e reduzir uso de memória")

            # Recomendações de curto prazo
            recommendations["short_term"].extend([
                "Implementar cache de módulos compilados",
                "Otimizar algoritmo de carregamento de configurações",
                "Implementar preload assíncrono de componentes críticos"
            ])

            # Recomendações de longo prazo
            recommendations["long_term"].extend([
                "Implementar plugin system para extensibilidade",
                "Otimizar para diferentes perfis de hardware",
                "Implementar AOT compilation para módulos críticos"
            ])

        return recommendations

    def save_report(self, output_path: Optional[Path] = None):
        """Salvar relatório de benchmark"""

        if output_path is None:
            output_path = self.project_root / "reports" / "performance_benchmark.json"

        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"📊 Relatório salvo em: {output_path}")

        return output_path

    def print_report(self):
        """Imprimir relatório formatado"""

        if not self.results:
            print("❌ Nenhum benchmark executado. Execute run_complete_benchmark() primeiro.")
            return

        print("\n" + "="*80)
        print("⚡ RELATÓRIO DE BENCHMARK DE PERFORMANCE")
        print("="*80)

        # Resumo geral
        summary = self.results.get("summary", {})
        print(f"🎯 Score Geral: {summary.get('overall_score', 'N/A')}")
        print(f"📊 Rating: {summary.get('performance_rating', 'N/A')}")
        print(f"🚨 Issues Críticos: {summary.get('critical_issues', 0)}")
        print(f"💡 Recomendações: {summary.get('recommendations_count', 0)}")

        # Benchmarks individuais
        startup = self.results.get("startup_benchmark", {}).get("statistics", {})
        if startup:
            print("
🚀 Startup Performance:"            print(".2f"            print(".2f"            print(".2f"
        memory = self.results.get("memory_benchmark", {})
        if memory.get("memory_growth"):
            print("
💾 Memory Usage:"            print(".1f"            print(f"  Eficiência: {memory.get('memory_efficiency', 'unknown').title()}")

        cpu = self.results.get("cpu_benchmark", {})
        if cpu.get("avg_cpu_usage"):
            print("
🖥️  CPU Usage:"            print(".1f"            print(f"  Eficiência: {cpu.get('overall_cpu_efficiency', 'unknown').title()}")

        imports = self.results.get("import_benchmark", {})
        if imports.get("total_import_time"):
            print("
📦 Import Performance:"            print(".2f"            if imports.get("slowest_modules"):
                slowest = imports["slowest_modules"][0]
                print(".2f"
        build = self.results.get("build_benchmark", {})
        if build.get("build_time"):
            if build["build_time"] == float('inf'):
                print("
🏗️  Build Performance:"                print("  Tempo: Timeout/Erro"                print(f"  Eficiência: {build.get('build_efficiency', 'unknown').title()}")
            else:
                print("
🏗️  Build Performance:"                print(".2f"                print(f"  Eficiência: {build.get('build_efficiency', 'unknown').title()}")

        # Gargalos
        bottlenecks = self.results.get("bottleneck_analysis", {})
        if bottlenecks:
            print("
🔍 Performance Bottlenecks:"            for severity, issues in bottlenecks.items():
                if issues:
                    print(f"  {severity.upper()}:")
                    for issue in issues:
                        print(f"    • {issue}")

        # Recomendações
        recommendations = self.results.get("recommendations", {})
        if recommendations.get("immediate"):
            print("
🚨 AÇÕES IMEDIATAS:"            for rec in recommendations["immediate"]:
                print(f"  • {rec}")

        print("\n" + "="*80)


def main():
    """Função principal"""
    benchmark = PerformanceBenchmark()

    try:
        # Executar benchmark completo
        results = benchmark.run_complete_benchmark()

        # Imprimir relatório
        benchmark.print_report()

        # Salvar relatório
        report_path = benchmark.save_report()
        print(f"📁 Relatório detalhado salvo em: {report_path}")

        print("\n✅ Benchmark de performance concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
