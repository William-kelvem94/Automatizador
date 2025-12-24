#!/usr/bin/env python3
"""
ANALISADOR DE DEPENDÊNCIAS - Automator Web IA v8.0
Análise completa das dependências do projeto para otimização
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import importlib.util
import pkg_resources
import requirements

class DependencyAnalyzer:
    """Analisador avançado de dependências"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_path = self.project_root / "config" / "requirements.txt"
        self.analysis_results = {}

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Executar análise completa das dependências"""

        print("🔍 ANALISANDO DEPENDÊNCIAS DO PROJETO...")
        print("=" * 60)

        # 1. Análise do requirements.txt
        print("📋 Analisando requirements.txt...")
        reqs_analysis = self._analyze_requirements_file()

        # 2. Análise de imports no código
        print("🔍 Analisando imports no código...")
        imports_analysis = self._analyze_code_imports()

        # 3. Análise de dependências transitivas
        print("🔗 Analisando dependências transitivas...")
        transitive_analysis = self._analyze_transitive_deps()

        # 4. Análise de compatibilidade
        print("⚖️  Analisando compatibilidade...")
        compatibility_analysis = self._analyze_compatibility()

        # 5. Análise de performance
        print("⚡ Analisando impacto na performance...")
        performance_analysis = self._analyze_performance_impact()

        # 6. Recomendações de otimização
        print("💡 Gerando recomendações...")
        recommendations = self._generate_optimization_recommendations()

        self.analysis_results = {
            "requirements_analysis": reqs_analysis,
            "imports_analysis": imports_analysis,
            "transitive_analysis": transitive_analysis,
            "compatibility_analysis": compatibility_analysis,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "summary": self._generate_summary()
        }

        return self.analysis_results

    def _analyze_requirements_file(self) -> Dict[str, Any]:
        """Analisar arquivo requirements.txt"""

        if not self.requirements_path.exists():
            return {"error": "requirements.txt não encontrado"}

        with open(self.requirements_path, 'r') as f:
            content = f.read()

        # Parse requirements
        reqs = []
        for req in requirements.parse(content):
            reqs.append({
                "name": req.name,
                "specs": req.specs,
                "extras": req.extras,
                "line": str(req)
            })

        analysis = {
            "total_packages": len(reqs),
            "packages": reqs,
            "categories": self._categorize_packages(reqs),
            "heavy_packages": self._identify_heavy_packages(reqs),
            "optional_packages": self._identify_optional_packages(reqs)
        }

        return analysis

    def _categorize_packages(self, packages: List[Dict]) -> Dict[str, List[str]]:
        """Categorizar pacotes por tipo"""

        core_packages = []
        ai_packages = []
        vision_packages = []
        web_packages = []
        dev_packages = []
        ui_packages = []
        db_packages = []
        utils_packages = []

        # Mapeamento baseado em nomes de pacotes
        categories = {
            "core": ["loguru", "pydantic", "python-dotenv"],
            "ai": ["openai", "anthropic", "torch", "transformers", "langchain"],
            "vision": ["opencv-python", "pillow", "numpy"],
            "web": ["fastapi", "uvicorn", "starlette", "httpx"],
            "dev": ["pytest", "black", "mypy", "flake8", "isort"],
            "ui": ["PySide6", "PyQt6", "customtkinter", "darkdetect", "qt-material"],
            "db": ["sqlalchemy", "psycopg2", "sqlite"],
            "utils": ["apscheduler", "cryptography", "bcrypt", "python-jose"]
        }

        for package in packages:
            name = package["name"].lower()
            categorized = False

            for category, package_list in categories.items():
                if any(pkg in name for pkg in package_list):
                    if category == "core":
                        core_packages.append(package["name"])
                    elif category == "ai":
                        ai_packages.append(package["name"])
                    elif category == "vision":
                        vision_packages.append(package["name"])
                    elif category == "web":
                        web_packages.append(package["name"])
                    elif category == "dev":
                        dev_packages.append(package["name"])
                    elif category == "ui":
                        ui_packages.append(package["name"])
                    elif category == "db":
                        db_packages.append(package["name"])
                    elif category == "utils":
                        utils_packages.append(package["name"])
                    categorized = True
                    break

            if not categorized:
                utils_packages.append(package["name"])

        return {
            "core": core_packages,
            "ai": ai_packages,
            "vision": vision_packages,
            "web": web_packages,
            "dev": dev_packages,
            "ui": ui_packages,
            "database": db_packages,
            "utils": utils_packages
        }

    def _identify_heavy_packages(self, packages: List[Dict]) -> List[Dict]:
        """Identificar pacotes pesados"""

        heavy_packages = [
            "torch", "transformers", "opencv-python", "PySide6",
            "PyQt6", "numpy", "scipy", "pandas", "tensorflow"
        ]

        heavy_found = []
        for package in packages:
            if any(heavy in package["name"].lower() for heavy in heavy_packages):
                heavy_found.append({
                    "name": package["name"],
                    "estimated_size_mb": self._estimate_package_size(package["name"]),
                    "category": "heavy"
                })

        return heavy_found

    def _identify_optional_packages(self, packages: List[Dict]) -> List[Dict]:
        """Identificar pacotes opcionais"""

        optional_patterns = [
            "torch", "transformers", "opencv", "tensorflow", "scikit",
            "pillow", "numpy", "scipy", "pandas", "matplotlib",
            "fastapi", "uvicorn", "starlette", "httpx",
            "pytest", "black", "mypy", "flake8", "isort"
        ]

        optional_found = []
        for package in packages:
            if any(opt in package["name"].lower() for opt in optional_patterns):
                optional_found.append({
                    "name": package["name"],
                    "reason": self._get_optional_reason(package["name"]),
                    "can_be_lazy": True
                })

        return optional_found

    def _estimate_package_size(self, package_name: str) -> float:
        """Estimar tamanho do pacote em MB"""

        size_estimates = {
            "torch": 800.0,
            "transformers": 250.0,
            "opencv-python": 50.0,
            "PySide6": 150.0,
            "PyQt6": 120.0,
            "numpy": 15.0,
            "pandas": 50.0,
            "tensorflow": 400.0,
            "scipy": 80.0,
            "matplotlib": 30.0
        }

        return size_estimates.get(package_name.lower(), 10.0)

    def _get_optional_reason(self, package_name: str) -> str:
        """Obter razão pela qual o pacote é opcional"""

        reasons = {
            "torch": "Apenas para funcionalidades de IA avançada",
            "transformers": "Apenas para processamento de linguagem natural",
            "opencv": "Apenas para processamento de imagens",
            "tensorflow": "Apenas para modelos de ML específicos",
            "fastapi": "Apenas para APIs REST/GraphQL",
            "pytest": "Apenas para desenvolvimento e testes",
            "black": "Apenas para desenvolvimento",
            "mypy": "Apenas para desenvolvimento"
        }

        return reasons.get(package_name.lower(), "Funcionalidade opcional")

    def _analyze_code_imports(self) -> Dict[str, Any]:
        """Analisar imports no código fonte"""

        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return {"error": "Diretório src não encontrado"}

        all_imports = []
        python_files = list(src_dir.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extrair imports
                imports = self._extract_imports_from_file(content)
                all_imports.extend(imports)

            except Exception as e:
                print(f"Erro ao analisar {py_file}: {e}")

        # Analisar imports únicos
        unique_imports = list(set(all_imports))
        unique_imports.sort()

        # Categorizar imports
        categorized_imports = self._categorize_imports(unique_imports)

        return {
            "total_files": len(python_files),
            "total_imports": len(all_imports),
            "unique_imports": len(unique_imports),
            "imports_list": unique_imports,
            "categorized": categorized_imports,
            "unused_dependencies": self._find_unused_dependencies(unique_imports)
        }

    def _extract_imports_from_file(self, content: str) -> List[str]:
        """Extrair imports de um arquivo Python"""

        imports = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # Import direto
            if line.startswith('import '):
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    imports.append(module)

            # From import
            elif line.startswith('from '):
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    imports.append(module)

        return imports

    def _categorize_imports(self, imports: List[str]) -> Dict[str, List[str]]:
        """Categorizar imports por tipo"""

        categories = {
            "standard_library": [],
            "third_party": [],
            "local_modules": []
        }

        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'subprocess',
            'threading', 'multiprocessing', 'asyncio', 'logging', 'typing',
            'collections', 'itertools', 'functools', 're', 'math', 'random',
            'hashlib', 'base64', 'urllib', 'http', 'xml', 'html', 'email'
        }

        for imp in imports:
            if imp in stdlib_modules:
                categories["standard_library"].append(imp)
            elif imp.startswith('.'):
                categories["local_modules"].append(imp)
            else:
                categories["third_party"].append(imp)

        return categories

    def _find_unused_dependencies(self, used_imports: List[str]) -> List[str]:
        """Encontrar dependências não utilizadas"""

        if not self.requirements_path.exists():
            return []

        # Ler requirements
        with open(self.requirements_path, 'r') as f:
            reqs = [req.name for req in requirements.parse(f.read())]

        # Comparar com imports utilizados
        used_deps = []
        for imp in used_imports:
            # Mapeamento de import para nome do pacote
            package_mapping = {
                'PIL': 'Pillow',
                'cv2': 'opencv-python',
                'sklearn': 'scikit-learn',
                'yaml': 'PyYAML'
            }

            package_name = package_mapping.get(imp, imp)
            if package_name in reqs:
                used_deps.append(package_name)

        unused = [req for req in reqs if req not in used_deps]

        return unused

    def _analyze_transitive_deps(self) -> Dict[str, Any]:
        """Analisar dependências transitivas"""

        try:
            # Tentar instalar e analisar dependências
            result = subprocess.run([
                sys.executable, '-c',
                """
import pkg_resources
import json

# Obter dependências instaladas
installed = []
for dist in pkg_resources.working_set:
    deps = [str(dep) for dep in dist.requires()]
    if deps:  # Apenas pacotes com dependências
        installed.append({
            'name': dist.project_name,
            'version': dist.version,
            'dependencies': deps
        })

print(json.dumps(installed))
                """
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                transitive_data = json.loads(result.stdout)
            else:
                transitive_data = []

        except Exception as e:
            print(f"Erro ao analisar dependências transitivas: {e}")
            transitive_data = []

        # Análise básica
        analysis = {
            "packages_with_deps": len(transitive_data),
            "total_transitive_deps": sum(len(pkg['dependencies']) for pkg in transitive_data),
            "most_dependent_packages": sorted(
                transitive_data,
                key=lambda x: len(x['dependencies']),
                reverse=True
            )[:5]
        }

        return analysis

    def _analyze_compatibility(self) -> Dict[str, Any]:
        """Analisar compatibilidade entre pacotes"""

        compatibility_issues = []

        # Verificar conflitos conhecidos
        conflict_patterns = [
            ("PySide6", "PyQt6", "Ambos são frameworks Qt - escolher apenas um"),
            ("torch", "tensorflow", "Frameworks de ML conflitantes"),
            ("opencv-python", "opencv-contrib-python", "Versões conflitantes do OpenCV")
        ]

        if self.requirements_path.exists():
            with open(self.requirements_path, 'r') as f:
                content = f.read()

            packages = [req.name.lower() for req in requirements.parse(content)]

            for pkg1, pkg2, issue in conflict_patterns:
                if pkg1.lower() in packages and pkg2.lower() in packages:
                    compatibility_issues.append({
                        "packages": [pkg1, pkg2],
                        "issue": issue,
                        "severity": "high"
                    })

        return {
            "issues_found": len(compatibility_issues),
            "compatibility_issues": compatibility_issues,
            "status": "good" if not compatibility_issues else "needs_attention"
        }

    def _analyze_performance_impact(self) -> Dict[str, Any]:
        """Analisar impacto na performance"""

        # Estimativas baseadas em conhecimento geral
        performance_impact = {
            "startup_time_impact": {
                "PySide6": 2.0,  # segundos
                "torch": 5.0,
                "transformers": 3.0,
                "opencv_python": 1.5,
                "fastapi": 1.0,
                "sqlalchemy": 0.5
            },
            "memory_impact": {
                "PySide6": 80,  # MB
                "torch": 500,
                "transformers": 300,
                "opencv_python": 50,
                "fastapi": 30,
                "sqlalchemy": 20
            }
        }

        # Calcular totais
        total_startup_impact = 0
        total_memory_impact = 0

        if self.requirements_path.exists():
            with open(self.requirements_path, 'r') as f:
                packages = [req.name.lower() for req in requirements.parse(f.read())]

            for package in packages:
                total_startup_impact += performance_impact["startup_time_impact"].get(package, 0)
                total_memory_impact += performance_impact["memory_impact"].get(package, 0)

        return {
            "estimated_startup_time": total_startup_impact,
            "estimated_memory_usage": total_memory_impact,
            "performance_score": self._calculate_performance_score(total_startup_impact, total_memory_impact),
            "bottlenecks": self._identify_performance_bottlenecks(packages if 'packages' in locals() else [])
        }

    def _calculate_performance_score(self, startup_time: float, memory_mb: float) -> str:
        """Calcular score de performance"""

        # Lógica simples de pontuação
        if startup_time < 5 and memory_mb < 200:
            return "A+"
        elif startup_time < 10 and memory_mb < 400:
            return "A"
        elif startup_time < 15 and memory_mb < 600:
            return "B+"
        elif startup_time < 20 and memory_mb < 800:
            return "B"
        else:
            return "C"

    def _identify_performance_bottlenecks(self, packages: List[str]) -> List[str]:
        """Identificar gargalos de performance"""

        bottlenecks = []

        heavy_packages = ["torch", "transformers", "opencv-python", "PySide6", "tensorflow"]
        for package in packages:
            if package.lower() in heavy_packages:
                bottlenecks.append(f"{package}: Pacote pesado que impacta startup")

        if len(packages) > 50:
            bottlenecks.append("Muitas dependências: Considere lazy loading")

        return bottlenecks

    def _generate_optimization_recommendations(self) -> Dict[str, Any]:
        """Gerar recomendações de otimização"""

        recommendations = {
            "immediate_actions": [],
            "short_term": [],
            "long_term": []
        }

        # Análises básicas para recomendações
        if hasattr(self, 'analysis_results'):
            reqs = self.analysis_results.get("requirements_analysis", {})
            perf = self.analysis_results.get("performance_analysis", {})

            # Ações imediatas
            if reqs.get("total_packages", 0) > 30:
                recommendations["immediate_actions"].append(
                    "Reduzir número de dependências - considere lazy loading"
                )

            if perf.get("performance_score") in ["C", "B"]:
                recommendations["immediate_actions"].append(
                    "Otimizar performance - implementar lazy loading para pacotes pesados"
                )

            # Curto prazo
            recommendations["short_term"].extend([
                "Implementar sistema de lazy loading",
                "Criar requirements otimizados por categoria",
                "Configurar build system com múltiplas variantes"
            ])

            # Longo prazo
            recommendations["long_term"].extend([
                "Implementar plugin system extensível",
                "Otimizar para diferentes perfis de hardware",
                "Implementar caching inteligente de módulos"
            ])

        return recommendations

    def _generate_summary(self) -> Dict[str, Any]:
        """Gerar resumo da análise"""

        return {
            "timestamp": "2024-12-24T17:00:00Z",
            "analyzer_version": "1.0.0",
            "project": "Automator Web IA v8.0",
            "status": "analysis_complete"
        }

    def save_report(self, output_path: Optional[Path] = None):
        """Salvar relatório de análise"""

        if output_path is None:
            output_path = self.project_root / "reports" / "dependency_analysis.json"

        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

        print(f"📊 Relatório salvo em: {output_path}")

        return output_path

    def print_report(self):
        """Imprimir relatório formatado"""

        if not self.analysis_results:
            print("❌ Nenhuma análise executada. Execute run_complete_analysis() primeiro.")
            return

        print("\n" + "="*80)
        print("📊 RELATÓRIO DE ANÁLISE DE DEPENDÊNCIAS")
        print("="*80)

        # Resumo geral
        reqs = self.analysis_results.get("requirements_analysis", {})
        imports = self.analysis_results.get("imports_analysis", {})
        perf = self.analysis_results.get("performance_analysis", {})

        print(f"📦 Total de pacotes: {reqs.get('total_packages', 0)}")
        print(f"🔍 Arquivos Python analisados: {imports.get('total_files', 0)}")
        print(f"⚡ Score de Performance: {perf.get('performance_score', 'N/A')}")
        print(f"⏱️  Tempo de startup estimado: {perf.get('estimated_startup_time', 0):.1f}s")
        print(f"💾 Uso de memória estimado: {perf.get('estimated_memory_usage', 0):.0f}MB")

        # Categorização
        categories = reqs.get("categories", {})
        print("\n📂 Categorização de pacotes:")        for category, packages in categories.items():
            if packages:
                print(f"  {category.title()}: {len(packages)} pacotes")

        # Pacotes pesados
        heavy = reqs.get("heavy_packages", [])
        if heavy:
            print("\n🏋️  Pacotes pesados identificados:")
            for pkg in heavy[:5]:  # Top 5
                print(".1f")
        # Recomendações
        recommendations = self.analysis_results.get("recommendations", {})
        if recommendations.get("immediate_actions"):
            print("\n🚨 AÇÕES IMEDIATAS RECOMENDADAS:")
            for action in recommendations["immediate_actions"]:
                print(f"  • {action}")

        print("\n" + "="*80)


def main():
    """Função principal"""
    analyzer = DependencyAnalyzer()

    try:
        # Executar análise completa
        results = analyzer.run_complete_analysis()

        # Imprimir relatório
        analyzer.print_report()

        # Salvar relatório
        report_path = analyzer.save_report()
        print(f"📁 Relatório detalhado salvo em: {report_path}")

        print("\n✅ Análise de dependências concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
