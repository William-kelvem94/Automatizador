"""
LAZY IMPORTER - Automator Web IA v8.0
"""

import importlib
from typing import Any, Optional

class LazyImporter:
    """Importador lazy simples"""

    def __init__(self):
        self._loaded = {}

    def import_module(self, module_name: str) -> Optional[Any]:
        """Import lazy de modulo"""
        if module_name in self._loaded:
            return self._loaded[module_name]

        try:
            module = importlib.import_module(module_name)
            self._loaded[module_name] = module
            print(f"Lazy loaded: {module_name}")
            return module
        except ImportError:
            print(f"Failed to load: {module_name}")
            return None

lazy_importer = LazyImporter()

def lazy_import(module_name: str):
    """Funcao de conveniencia"""
    return lazy_importer.import_module(module_name)
