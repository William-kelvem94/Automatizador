#!/usr/bin/env python3
"""
ANALISADOR SIMPLIFICADO DE DEPENDENCIAS - Automator Web IA v8.0
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import requirements

class SimpleDependencyAnalyzer:
    """Analisador simplificado de dependencias"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_path = self.project_root / "config" / "requirements.txt"

    def analyze(self) -> Dict[str, Any]:
        """Analise basica das dependencias"""

        print("ANALISANDO DEPENDENCIAS DO PROJETO...")
        print("=" * 50)

        # Ler requirements.txt
        if not self.requirements_path.exists():
            return {"error": "requirements.txt nao encontrado"}

        with open(self.requirements_path, 'r') as f:
            content = f.read()

        # Parse requirements
        reqs = []
        for req in requirements.parse(content):
            reqs.append({
                "name": req.name,
                "line": str(req)
            })

        analysis = {
            "total_packages": len(reqs),
            "packages": reqs,
            "heavy_packages": self._identify_heavy_packages(reqs),
            "optional_packages": self._identify_optional_packages(reqs)
        }

        return analysis

    def _identify_heavy_packages(self, packages: List[Dict]) -> List[Dict]:
        """Identificar pacotes pesados"""

        heavy_packages = [
            "torch", "transformers", "opencv-python", "PySide6",
            "PyQt6", "numpy", "pandas", "tensorflow"
        ]

        heavy_found = []
        for package in packages:
            if any(heavy in package["name"].lower() for heavy in heavy_packages):
                heavy_found.append({
                    "name": package["name"],
                    "category": "heavy"
                })

        return heavy_found

    def _identify_optional_packages(self, packages: List[Dict]) -> List[Dict]:
        """Identificar pacotes opcionais"""

        optional_patterns = [
            "torch", "transformers", "opencv", "tensorflow", "scikit",
            "pillow", "numpy", "scipy", "pandas", "matplotlib",
            "fastapi", "uvicorn", "starlette", "httpx"
        ]

        optional_found = []
        for package in packages:
            if any(opt in package["name"].lower() for opt in optional_patterns):
                optional_found.append({
                    "name": package["name"],
                    "can_be_lazy": True
                })

        return optional_found

    def print_report(self, analysis: Dict[str, Any]):
        """Imprimir relatorio"""

        print("\n" + "="*50)
        print("RELATORIO DE ANALISE DE DEPENDENCIAS")
        print("="*50)

        print(f"Total de pacotes: {analysis.get('total_packages', 0)}")

        heavy = analysis.get("heavy_packages", [])
        if heavy:
            print(f"Pacotes pesados: {len(heavy)}")
            for pkg in heavy[:3]:
                print(f"  - {pkg['name']}")

        optional = analysis.get("optional_packages", [])
        if optional:
            print(f"Pacotes opcionais: {len(optional)}")
            for pkg in optional[:3]:
                print(f"  - {pkg['name']}")

        print("\nRECOMENDACOES:")
        print("- Implementar lazy loading")
        print("- Separar dependencias por categoria")
        print("- Otimizar requirements.txt")

        print("="*50)

def main():
    """Funcao principal"""
    analyzer = SimpleDependencyAnalyzer()

    try:
        results = analyzer.analyze()
        analyzer.print_report(results)

        # Salvar relatorio
        report_path = analyzer.project_root / "reports" / "simple_analysis.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"\nRelatorio salvo em: {report_path}")
        print("Analise concluida!")

    except Exception as e:
        print(f"Erro: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
