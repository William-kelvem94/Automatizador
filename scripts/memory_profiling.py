#!/usr/bin/env python3
"""
MEMORY PROFILING v9.0 - Automator Web IA
Profiling avançado de uso de memória com otimizações enterprise
"""

import os
import sys
import time
import psutil
import tracemalloc
import gc
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import statistics
import threading
import weakref

class EnterpriseMemoryProfiler:
    """Profiler de memória enterprise-grade"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.snapshots = []
        self.memory_timeline = []
        self.leak_candidates = []
        self.optimization_suggestions = []

        # Configurações
        self.sampling_interval = 0.1  # 100ms
        self.profiling_duration = 30  # 30 segundos
        self.memory_threshold_mb = 100  # Alerta acima de 100MB

    def run_comprehensive_memory_profile(self) -> Dict[str, Any]:
        """Executar profiling completo de memória"""

        print("💾 MEMORY PROFILING v9.0 - ENTERPRISE MODE")
        print("=" * 60)

        # 1. Baseline memory measurement
        print("📊 Coletando baseline de memória...")
        baseline = self._collect_memory_baseline()

        # 2. Startup memory profiling
        print("🚀 Profiling de memória durante startup...")
        startup_profile = self._profile_startup_memory()

        # 3. Runtime memory monitoring
        print("📈 Monitorando uso de memória em runtime...")
        runtime_profile = self._monitor_runtime_memory()

        # 4. Memory leak detection
        print("🔍 Detectando memory leaks...")
        leak_analysis = self._detect_memory_leaks()

        # 5. Garbage collection analysis
        print("🗑️  Analisando garbage collection...")
        gc_analysis = self._analyze_garbage_collection()

        # 6. Object allocation profiling
        print("📦 Profiling de alocação de objetos...")
        allocation_profile = self._profile_object_allocation()

        # 7. Optimization recommendations
        print("💡 Gerando recomendações de otimização...")
        recommendations = self._generate_memory_optimizations()

        results = {
            "profile_info": {
                "timestamp": time.time(),
                "sampling_interval": self.sampling_interval,
                "profiling_duration": self.profiling_duration,
                "system_info": self._get_system_memory_info()
            },
            "baseline_memory": baseline,
            "startup_memory_profile": startup_profile,
            "runtime_memory_profile": runtime_profile,
            "memory_leak_analysis": leak_analysis,
            "garbage_collection_analysis": gc_analysis,
            "object_allocation_profile": allocation_profile,
            "optimization_recommendations": recommendations,
            "memory_health_score": self._calculate_memory_health_score(),
            "optimization_potential": self._calculate_memory_optimization_potential()
        }

        return results

    def _collect_memory_baseline(self) -> Dict[str, Any]:
        """Coletar métricas baseline de memória"""

        process = psutil.Process()

        # Múltiplas medições para precisão
        measurements = []
        for _ in range(10):
            measurements.append({
                "rss_mb": process.memory_info().rss / (1024 * 1024),
                "vms_mb": process.memory_info().vms / (1024 * 1024),
                "percent": process.memory_percent()
            })
            time.sleep(0.1)

        return {
            "average_rss_mb": statistics.mean(m["rss_mb"] for m in measurements),
            "average_vms_mb": statistics.mean(m["vms_mb"] for m in measurements),
            "average_percent": statistics.mean(m["percent"] for m in measurements),
            "peak_rss_mb": max(m["rss_mb"] for m in measurements),
            "measurements": measurements
        }

    def _profile_startup_memory(self) -> Dict[str, Any]:
        """Profile de memória durante startup"""

        tracemalloc.start()
        snapshots = []

        # Baseline
        snapshots.append({
            "phase": "baseline",
            "timestamp": time.time(),
            "current_mb": tracemalloc.get_traced_memory()[0] / (1024 * 1024),
            "peak_mb": tracemalloc.get_traced_memory()[1] / (1024 * 1024)
        })

        # Simular startup
        self._simulate_application_startup()

        # Pós-startup
        snapshots.append({
            "phase": "post_startup",
            "timestamp": time.time(),
            "current_mb": tracemalloc.get_traced_memory()[0] / (1024 * 1024),
            "peak_mb": tracemalloc.get_traced_memory()[1] / (1024 * 1024)
        })

        tracemalloc.stop()

        return {
            "snapshots": snapshots,
            "startup_memory_growth_mb": snapshots[-1]["current_mb"] - snapshots[0]["current_mb"],
            "startup_peak_memory_mb": snapshots[-1]["peak_mb"],
            "memory_efficiency": self._evaluate_startup_efficiency(snapshots)
        }

    def _simulate_application_startup(self):
        """Simular startup da aplicação para profiling"""

        # Adicionar src ao path
        src_path = str(self.project_root / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Importar módulos principais simulando startup
        import importlib

        startup_modules = [
            "src.shared.utils.logger",
            "src.shared.config.settings",
            "src.domain.entities.automation_task"
        ]

        for module in startup_modules:
            try:
                importlib.import_module(module.replace("src.", "").replace(".", "_"))
                time.sleep(0.05)  # Simular overhead
            except ImportError:
                pass

    def _monitor_runtime_memory(self) -> Dict[str, Any]:
        """Monitorar uso de memória em runtime"""

        process = psutil.Process()
        timeline = []

        def collect_samples():
            start_time = time.time()
            while time.time() - start_time < self.profiling_duration:
                sample = {
                    "timestamp": time.time(),
                    "rss_mb": process.memory_info().rss / (1024 * 1024),
                    "vms_mb": process.memory_info().vms / (1024 * 1024),
                    "percent": process.memory_percent(),
                    "threads": process.num_threads()
                }
                timeline.append(sample)
                time.sleep(self.sampling_interval)

        # Iniciar coleta
        collect_thread = threading.Thread(target=collect_samples)
        collect_thread.start()
        collect_thread.join()

        # Análise da timeline
        rss_values = [s["rss_mb"] for s in timeline]
        vms_values = [s["vms_mb"] for s in timeline]

        return {
            "timeline": timeline,
            "duration_seconds": self.profiling_duration,
            "samples_count": len(timeline),
            "rss_stats": {
                "min_mb": min(rss_values),
                "max_mb": max(rss_values),
                "avg_mb": statistics.mean(rss_values),
                "stdev_mb": statistics.stdev(rss_values) if len(rss_values) > 1 else 0
            },
            "vms_stats": {
                "min_mb": min(vms_values),
                "max_mb": max(vms_values),
                "avg_mb": statistics.mean(vms_values),
                "stdev_mb": statistics.stdev(vms_values) if len(vms_values) > 1 else 0
            },
            "memory_stability": self._analyze_memory_stability(timeline)
        }

    def _detect_memory_leaks(self) -> Dict[str, Any]:
        """Detectar possíveis memory leaks"""

        # Simulação de detecção de leaks (em implementação real usaria tools mais avançados)
        leak_candidates = []

        # Análise baseada em padrões de crescimento
        if hasattr(self, 'memory_timeline') and self.memory_timeline:
            rss_values = [s.get("rss_mb", 0) for s in self.memory_timeline[-20:]]  # Últimas 20 amostras

            if len(rss_values) >= 10:
                # Verificar crescimento consistente
                growth_trend = []
                for i in range(1, len(rss_values)):
                    growth = rss_values[i] - rss_values[i-1]
                    growth_trend.append(growth)

                avg_growth = statistics.mean(growth_trend)
                if avg_growth > 1:  # Crescimento > 1MB por amostra
                    leak_candidates.append({
                        "type": "continuous_growth",
                        "severity": "high",
                        "avg_growth_mb_per_sample": avg_growth,
                        "description": "Crescimento contínuo de memória detectado"
                    })

        return {
            "leak_candidates": leak_candidates,
            "leak_probability": len(leak_candidates) * 25,  # Score simples
            "recommendations": self._generate_leak_recommendations(leak_candidates)
        }

    def _analyze_garbage_collection(self) -> Dict[str, Any]:
        """Analisar eficiência do garbage collection"""

        # Forçar GC e medir
        gc_start = time.time()
        collected_objects = gc.collect()
        gc_duration = time.time() - gc_start

        # Estatísticas do GC
        gc_stats = {
            "collected_objects": collected_objects,
            "gc_duration_seconds": gc_duration,
            "gc_thresholds": gc.get_threshold(),
            "gc_stats": gc.get_stats()
        }

        # Avaliação de eficiência
        efficiency_score = 100
        if gc_duration > 0.1:  # GC lento
            efficiency_score -= 20
        if collected_objects < 100:  # Poucos objetos coletados
            efficiency_score -= 10

        gc_stats["efficiency_score"] = max(0, efficiency_score)

        return gc_stats

    def _profile_object_allocation(self) -> Dict[str, Any]:
        """Profile de alocação de objetos"""

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        # Simular operações que alocam objetos
        self._simulate_object_allocation_workload()

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Comparar snapshots
        stats = snapshot2.compare_to(snapshot1, 'lineno')

        # Top alocadores
        top_allocators = []
        for stat in stats[:10]:  # Top 10
            top_allocators.append({
                "file": stat.traceback[0].filename if stat.traceback else "unknown",
                "line": stat.traceback[0].lineno if stat.traceback else 0,
                "size_mb": stat.size_diff / (1024 * 1024),
                "count_diff": stat.count_diff
            })

        return {
            "allocation_stats": top_allocators,
            "total_allocated_mb": sum(s["size_mb"] for s in top_allocators),
            "allocation_efficiency": self._evaluate_allocation_efficiency(top_allocators)
        }

    def _simulate_object_allocation_workload(self):
        """Simular workload que aloca objetos"""

        # Criar alguns objetos para profiling
        test_objects = []

        for i in range(1000):
            test_objects.append({
                "id": i,
                "data": "x" * 100,  # 100 bytes por objeto
                "metadata": {"timestamp": time.time(), "type": "test"}
            })

        # Simular processamento
        processed = [obj for obj in test_objects if obj["id"] % 2 == 0]

        # Cleanup
        del test_objects
        del processed
        gc.collect()

    def _generate_memory_optimizations(self) -> Dict[str, List[str]]:
        """Gerar recomendações de otimização de memória"""

        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }

        # Análise baseada nos resultados coletados
        if hasattr(self, 'memory_timeline') and self.memory_timeline:
            avg_memory = statistics.mean(s.get("rss_mb", 0) for s in self.memory_timeline)

            if avg_memory > 200:
                recommendations["immediate"].append("Implementar lazy loading para reduzir uso base de memória")
            if avg_memory > 400:
                recommendations["immediate"].append("Otimizar algoritmos de processamento para reduzir alocações")

        # Recomendações gerais
        recommendations["short_term"].extend([
            "Implementar object pooling para objetos frequentes",
            "Configurar GC thresholds otimizados",
            "Implementar weak references para caches grandes",
            "Usar __slots__ em classes com muitos objetos"
        ])

        recommendations["long_term"].extend([
            "Implementar memory-mapped files para dados grandes",
            "Configurar NUMA-aware memory allocation",
            "Implementar custom allocators para tipos específicos",
            "Otimizar estrutura de dados baseada em perfis de uso"
        ])

        return recommendations

    def _calculate_memory_health_score(self) -> Dict[str, Any]:
        """Calcular score de saúde da memória"""

        score = 100
        issues = []

        # Análise baseada em métricas coletadas
        if hasattr(self, 'memory_timeline') and self.memory_timeline:
            avg_memory = statistics.mean(s.get("rss_mb", 0) for s in self.memory_timeline)
            max_memory = max(s.get("rss_mb", 0) for s in self.memory_timeline)

            if avg_memory > 300:
                score -= 30
                issues.append("Uso médio de memória muito alto")
            elif avg_memory > 150:
                score -= 15
                issues.append("Uso médio de memória elevado")

            if max_memory > 500:
                score -= 25
                issues.append("Picos de memória muito altos")
            elif max_memory > 300:
                score -= 10
                issues.append("Picos de memória elevados")

        # Leak detection impact
        if self.leak_candidates:
            score -= len(self.leak_candidates) * 10
            issues.append("Possíveis memory leaks detectados")

        # GC efficiency
        gc_stats = self._analyze_garbage_collection()
        if gc_stats.get("efficiency_score", 100) < 80:
            score -= 10
            issues.append("Garbage collection ineficiente")

        return {
            "score": max(0, score),
            "rating": self._score_to_rating(score),
            "issues": issues,
            "recommendations": len(issues) > 0
        }

    def _calculate_memory_optimization_potential(self) -> Dict[str, Any]:
        """Calcular potencial de otimização de memória"""

        current_avg = 0
        if hasattr(self, 'memory_timeline') and self.memory_timeline:
            current_avg = statistics.mean(s.get("rss_mb", 0) for s in self.memory_timeline)

        target_memory = 150  # Meta: 150MB

        if current_avg <= target_memory:
            potential = 0
        else:
            potential = ((current_avg - target_memory) / current_avg) * 100

        return {
            "current_avg_mb": current_avg,
            "target_mb": target_memory,
            "optimization_potential_percent": potential,
            "estimated_savings_mb": current_avg - target_memory,
            "feasibility": "high" if potential < 30 else "medium" if potential < 60 else "low"
        }

    def _analyze_memory_stability(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Analisar estabilidade da memória"""

        if len(timeline) < 10:
            return {"stability_score": 50, "classification": "insufficient_data"}

        rss_values = [s.get("rss_mb", 0) for s in timeline]
        stability_score = 100 - (statistics.stdev(rss_values) / statistics.mean(rss_values)) * 100
        stability_score = max(0, min(100, stability_score))

        if stability_score > 80:
            classification = "excellent"
        elif stability_score > 60:
            classification = "good"
        elif stability_score > 40:
            classification = "fair"
        else:
            classification = "poor"

        return {
            "stability_score": stability_score,
            "classification": classification,
            "variability_percent": (statistics.stdev(rss_values) / statistics.mean(rss_values)) * 100
        }

    def _evaluate_startup_efficiency(self, snapshots: List[Dict]) -> Dict[str, Any]:
        """Avaliar eficiência de startup"""

        if len(snapshots) < 2:
            return {"efficiency": "unknown"}

        growth = snapshots[-1]["current_mb"] - snapshots[0]["current_mb"]

        if growth < 50:
            efficiency = "excellent"
            score = 100
        elif growth < 100:
            efficiency = "good"
            score = 80
        elif growth < 200:
            efficiency = "fair"
            score = 60
        else:
            efficiency = "poor"
            score = 40

        return {
            "efficiency": efficiency,
            "score": score,
            "growth_mb": growth
        }

    def _evaluate_allocation_efficiency(self, allocators: List[Dict]) -> Dict[str, Any]:
        """Avaliar eficiência de alocação"""

        if not allocators:
            return {"efficiency": "unknown"}

        total_allocated = sum(a["size_mb"] for a in allocators)

        if total_allocated < 10:
            efficiency = "excellent"
        elif total_allocated < 50:
            efficiency = "good"
        elif total_allocated < 100:
            efficiency = "fair"
        else:
            efficiency = "poor"

        return {
            "efficiency": efficiency,
            "total_allocated_mb": total_allocated,
            "top_allocator": allocators[0] if allocators else None
        }

    def _generate_leak_recommendations(self, leaks: List[Dict]) -> List[str]:
        """Gerar recomendações para leaks detectados"""

        recommendations = []

        for leak in leaks:
            if leak["type"] == "continuous_growth":
                recommendations.extend([
                    "Implementar cleanup periódico de caches",
                    "Usar weak references para objetos grandes",
                    "Revisar algoritmos de processamento para reduzir state accumulation"
                ])

        if not recommendations:
            recommendations.append("Monitorar continuamente para detectar leaks futuros")

        return recommendations

    def _score_to_rating(self, score: float) -> str:
        """Converter score numérico para rating"""

        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        else:
            return "C"

    def _get_system_memory_info(self) -> Dict[str, Any]:
        """Obter informações de memória do sistema"""

        vm = psutil.virtual_memory()

        return {
            "total_gb": vm.total / (1024**3),
            "available_gb": vm.available / (1024**3),
            "used_percent": vm.percent,
            "swap_total_gb": psutil.swap_memory().total / (1024**3),
            "swap_used_percent": psutil.swap_memory().percent
        }

    def save_report(self, results: Dict[str, Any], output_path: Optional[Path] = None):
        """Salvar relatório de profiling"""

        if output_path is None:
            output_path = self.project_root / "reports" / "memory_profiling.json"

        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Relatório salvo em: {output_path}")

        return output_path

    def print_report(self, results: Dict[str, Any]):
        """Imprimir relatório formatado"""

        print("\n" + "="*80)
        print("💾 RELATÓRIO DE MEMORY PROFILING v9.0")
        print("="*80)

        health = results.get("memory_health_score", {})
        opt_potential = results.get("optimization_potential", {})

        print(f"🎯 Memory Health Score: {health.get('rating', 'N/A')} ({health.get('score', 0)}/100)")

        if health.get("issues"):
            print("
🚨 Issues Detectados:"            for issue in health["issues"]:
                print(f"  • {issue}")

        baseline = results.get("baseline_memory", {})
        if baseline:
            print("
📊 Baseline Memory:"            print(".1f"            print(".1f"            print(".1f"
        startup = results.get("startup_memory_profile", {})
        if startup:
            print("
🚀 Startup Memory Profile:"            print(".1f"            print(f"  Pico de memória: {startup.get('startup_peak_memory_mb', 0):.1f}MB")
            print(f"  Eficiência: {startup.get('memory_efficiency', {}).get('efficiency', 'unknown').title()}")

        runtime = results.get("runtime_memory_profile", {})
        if runtime:
            rss_stats = runtime.get("rss_stats", {})
            stability = runtime.get("memory_stability", {})

            print("
📈 Runtime Memory Profile:"            print(".1f"            print(".1f"            print(f"  Estabilidade: {stability.get('classification', 'unknown').title()}")
            print(".1f"
        leak_analysis = results.get("memory_leak_analysis", {})
        if leak_analysis.get("leak_candidates"):
            print("
🔍 Memory Leaks Detected:"            for leak in leak_analysis["leak_candidates"]:
                print(f"  • {leak['description']} (Severity: {leak['severity']})")

        recommendations = results.get("optimization_recommendations", {})
        if recommendations.get("immediate"):
            print("
💡 RECOMENDAÇÕES IMEDIATAS:"            for rec in recommendations["immediate"]:
                print(f"  • {rec}")

        print("\n" + "="*80)

# Instância global
memory_profiler = EnterpriseMemoryProfiler()

def run_memory_profiling():
    """Executar profiling completo de memória"""
    results = memory_profiler.run_comprehensive_memory_profile()
    memory_profiler.print_report(results)
    memory_profiler.save_report(results)
    return results

if __name__ == "__main__":
    print("🚀 MEMORY PROFILING v9.0 - ENTERPRISE MODE")
    print("=" * 60)

    try:
        results = run_memory_profiling()

        print("
✅ MEMORY PROFILING CONCLUÍDO!"        print("🎯 Próximos passos:")
        print("1. Implementar otimizações de memória identificadas")
        print("2. Configurar monitoring de leaks em produção")
        print("3. Otimizar garbage collection")
        print("4. Executar novamente para validar melhorias")

    except Exception as e:
        print(f"❌ Erro durante profiling: {e}")
        import traceback
        traceback.print_exc()
