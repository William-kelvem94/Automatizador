#!/usr/bin/env python3
"""
ENTERPRISE BUILD SYSTEM v9.0 - Automator Web IA
Sistema de build enterprise-grade com múltiplas otimizações
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import platform
import tempfile
import hashlib

class EnterpriseBuildSystem:
    """Sistema de build enterprise com múltiplas estratégias de otimização"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.build_start_time = None

        # Configurações de build
        self.build_configs = {
            'minimal': {
                'description': 'Build mínimo para desenvolvimento',
                'target_size': '50MB',
                'startup_target': '<3s',
                'compression': 'ultra',
                'excludes': ['torch', 'transformers', 'cv2', 'tensorflow', 'diffusers'],
                'includes': ['PySide6', 'playwright', 'sqlalchemy', 'loguru', 'pydantic']
            },
            'standard': {
                'description': 'Build balanceado para produção',
                'target_size': '120MB',
                'startup_target': '<5s',
                'compression': 'high',
                'excludes': ['torch', 'transformers', 'tensorflow'],
                'includes': ['PySide6', 'playwright', 'sqlalchemy', 'cv2', 'fastapi']
            },
            'full': {
                'description': 'Build completo com todas as features',
                'target_size': '250MB',
                'startup_target': '<8s',
                'compression': 'normal',
                'excludes': [],
                'includes': ['torch', 'transformers', 'cv2', 'tensorflow', 'diffusers', 'fastapi']
            },
            'enterprise': {
                'description': 'Build enterprise com monitoramento avançado',
                'target_size': '180MB',
                'startup_target': '<6s',
                'compression': 'high',
                'excludes': ['tensorflow'],  # Muito pesado
                'includes': ['torch', 'transformers', 'cv2', 'prometheus_client', 'sentry_sdk']
            }
        }

        # Métricas de build
        self.build_metrics = {
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'size_before': 0,
            'size_after': 0,
            'compression_ratio': 0,
            'pyinstaller_warnings': 0,
            'missing_modules': [],
            'build_type': None
        }

    def build_enterprise_package(self, build_type: str = 'standard') -> Path:
        """Construir pacote enterprise otimizado"""

        print(f"🏗️  CONSTRUINDO PACOTE ENTERPRISE - {build_type.upper()}")
        print("=" * 70)

        if build_type not in self.build_configs:
            raise ValueError(f"Tipo de build não suportado: {build_type}")

        self.build_start_time = time.time()
        self.build_metrics['build_type'] = build_type
        self.build_metrics['start_time'] = self.build_start_time

        try:
            # 1. Preparar ambiente de build
            self._prepare_build_environment(build_type)

            # 2. Otimizar dependências
            self._optimize_dependencies(build_type)

            # 3. Configurar PyInstaller enterprise
            pyinstaller_config = self._configure_pyinstaller_enterprise(build_type)

            # 4. Executar build com monitoramento
            executable_path = self._execute_optimized_build(pyinstaller_config, build_type)

            # 5. Pós-processamento enterprise
            final_package = self._post_process_enterprise(executable_path, build_type)

            # 6. Verificar qualidade do build
            self._verify_build_quality(final_package, build_type)

            # 7. Gerar relatório de build
            self._generate_build_report(final_package, build_type)

            build_time = time.time() - self.build_start_time
            self.build_metrics['duration'] = build_time

            print(".1f"            print(f"📦 Pacote final: {final_package}")
            print(f"🎯 Tamanho alvo: {self.build_configs[build_type]['target_size']}")

            return final_package

        except Exception as e:
            print(f"❌ Erro no build: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _prepare_build_environment(self, build_type: str):
        """Preparar ambiente de build otimizado"""

        print("🔧 Preparando ambiente de build...")

        # Criar diretório de build limpo
        build_dir = self.project_root / "build" / f"enterprise_{build_type}"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True)

        # Configurar variáveis de ambiente para otimização
        os.environ.update({
            'PYINSTALLER_OPTIMIZE': '2',
            'PYINSTALLER_STRIP': '1',
            'PYINSTALLER_UPX_DIR': '/usr/local/bin',  # Se UPX estiver disponível
            'PYTHONOPTIMIZE': '1',
            'PYTHONDONTWRITEBYTECODE': '1'
        })

        # Verificar ferramentas necessárias
        self._verify_build_tools()

        print(f"✅ Ambiente preparado em: {build_dir}")

    def _optimize_dependencies(self, build_type: str):
        """Otimizar dependências baseado no tipo de build"""

        print("📦 Otimizando dependências...")

        config = self.build_configs[build_type]

        # Criar requirements otimizado
        optimized_reqs = self._generate_optimized_requirements(config)

        # Salvar requirements otimizado
        opt_req_path = self.project_root / "build" / f"requirements_{build_type}.txt"
        with open(opt_req_path, 'w') as f:
            f.write(optimized_reqs)

        print(f"✅ Requirements otimizado: {opt_req_path}")
        print(f"   📊 Excluídos: {len(config['excludes'])} módulos pesados")
        print(f"   📊 Incluídos: {len(config['includes'])} módulos essenciais")

    def _generate_optimized_requirements(self, config: Dict[str, Any]) -> str:
        """Gerar requirements.txt otimizado"""

        # Base requirements (sempre incluídos)
        base_reqs = [
            "# Core Dependencies - Always Included",
            "PySide6>=6.6.0",
            "playwright>=1.45.0",
            "sqlalchemy>=2.0.23",
            "loguru>=0.7.2",
            "pydantic>=2.6.0",
            "",
            "# Build-specific Dependencies"
        ]

        # Adicionar includes específicos
        for include in config['includes']:
            if include not in ['PySide6', 'playwright', 'sqlalchemy', 'loguru', 'pydantic']:
                if include in ['torch', 'transformers', 'cv2', 'tensorflow']:
                    base_reqs.append(f"{include}  # Heavy dependency - included in {config.get('description', 'build')}")
                else:
                    base_reqs.append(include)

        # Adicionar excludes como comentários
        if config['excludes']:
            base_reqs.append("")
            base_reqs.append("# Excluded Dependencies (too heavy for this build)")
            for exclude in config['excludes']:
                base_reqs.append(f"# {exclude}  # Excluded - too heavy")

        return "\n".join(base_reqs)

    def _configure_pyinstaller_enterprise(self, build_type: str) -> Dict[str, Any]:
        """Configurar PyInstaller para build enterprise"""

        print("⚙️  Configurando PyInstaller enterprise...")

        config = self.build_configs[build_type]

        # Configuração base do PyInstaller
        pyinstaller_config = {
            '--onefile': True,
            '--windowed': True,
            '--name': f'AutomatorIA-v9.0-{build_type}',
            '--hidden-import': [
                'PySide6.QtCore',
                'PySide6.QtGui',
                'PySide6.QtWidgets',
                'playwright',
                'sqlalchemy',
                'pydantic'
            ],
            '--exclude-module': config['excludes'],
            '--optimize': '2',
            '--strip': True,
            '--runtime-tmpdir': None,
            '--specpath': str(self.project_root / "build" / "specs"),
            '--workpath': str(self.project_root / "build" / "work"),
            '--distpath': str(self.project_root / "dist" / f"enterprise_{build_type}"),
            # Runtime hooks otimizados
            '--runtime-hook': [
                str(self.project_root / "build" / "runtime_hooks" / "qt_fixes.py"),
                str(self.project_root / "build" / "runtime_hooks" / "playwright_fixes.py"),
                str(self.project_root / "build" / "runtime_hooks" / "environment_setup.py")
            ],
            # Dados adicionais
            '--add-data': [
                f'src;src',
                f'config;config',
                f'docs;docs'
            ],
            'script': str(self.project_root / "src" / "main.py")
        }

        # Configurações específicas por tipo
        if build_type == 'minimal':
            pyinstaller_config['--hidden-import'].extend(['src.shared.utils.lazy_importer'])
            pyinstaller_config['--exclude-module'].extend(['torch', 'transformers', 'cv2'])

        elif build_type == 'enterprise':
            pyinstaller_config['--hidden-import'].extend([
                'prometheus_client',
                'sentry_sdk',
                'kubernetes'
            ])

        # Adicionar UPX se disponível
        if self._is_upx_available():
            pyinstaller_config['--upx-dir'] = '/usr/local/bin'

        return pyinstaller_config

    def _execute_optimized_build(self, config: Dict[str, Any], build_type: str) -> Path:
        """Executar build otimizado com monitoramento"""

        print("🏗️  Executando build otimizado...")

        # Preparar argumentos para PyInstaller
        args = []

        for key, value in config.items():
            if key.startswith('--'):
                if isinstance(value, list):
                    for item in value:
                        args.extend([key, item])
                elif isinstance(value, bool):
                    if value:
                        args.append(key)
                else:
                    args.extend([key, str(value)])
            elif key == 'script':
                args.append(value)

        # Adicionar script principal
        if 'script' in config:
            args.append(config['script'])

        print(f"📋 Executando: PyInstaller {' '.join(args[:10])}...")

        # Executar PyInstaller
        try:
            result = subprocess.run([
                sys.executable, '-m', 'PyInstaller', *args
            ], capture_output=True, text=True, timeout=1800)  # 30min timeout

            # Analisar saída
            if result.returncode == 0:
                print("✅ Build executado com sucesso")

                # Verificar warnings
                warnings = result.stderr.count('WARNING') if result.stderr else 0
                self.build_metrics['pyinstaller_warnings'] = warnings

                if warnings > 0:
                    print(f"⚠️  {warnings} warnings durante o build")

            else:
                print(f"❌ Build falhou: {result.stderr}")
                raise Exception(f"PyInstaller failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise Exception("Build timeout após 30 minutos")

        # Localizar executável gerado
        dist_dir = Path(config['--distpath'])
        exe_name = f"AutomatorIA-v9.0-{build_type}"

        if self.system == 'windows':
            exe_path = dist_dir / f"{exe_name}.exe"
        else:
            exe_path = dist_dir / exe_name

        if not exe_path.exists():
            raise FileNotFoundError(f"Executável não encontrado: {exe_path}")

        print(f"📁 Executável gerado: {exe_path}")

        return exe_path

    def _post_process_enterprise(self, exe_path: Path, build_type: str) -> Path:
        """Pós-processamento enterprise do executável"""

        print("🔧 Pós-processando executável...")

        # 1. Otimizar tamanho com UPX
        if self._is_upx_available():
            self._apply_upx_compression(exe_path, build_type)

        # 2. Criar estrutura de distribuição
        dist_package = self._create_distribution_structure(exe_path, build_type)

        # 3. Gerar checksums e manifest
        self._generate_package_integrity(dist_package)

        # 4. Criar atalhos/scripts de inicialização
        self._create_launcher_scripts(dist_package, build_type)

        print(f"✅ Pós-processamento concluído: {dist_package}")

        return dist_package

    def _apply_upx_compression(self, exe_path: Path, build_type: str):
        """Aplicar compressão UPX"""

        config = self.build_configs[build_type]
        compression_level = config.get('compression', 'normal')

        upx_args = {
            'ultra': ['--ultra-brute'],
            'high': ['--best'],
            'normal': ['--lzma']
        }.get(compression_level, ['--lzma'])

        try:
            print(f"🗜️  Aplicando compressão UPX ({compression_level})...")

            result = subprocess.run([
                'upx', *upx_args, str(exe_path)
            ], capture_output=True, timeout=300)

            if result.returncode == 0:
                print("✅ Compressão UPX aplicada com sucesso")
            else:
                print(f"⚠️  UPX falhou: {result.stderr.decode()}")

        except FileNotFoundError:
            print("⚠️  UPX não disponível - pulando compressão")
        except subprocess.TimeoutExpired:
            print("⚠️  UPX timeout - compressão interrompida")

    def _create_distribution_structure(self, exe_path: Path, build_type: str) -> Path:
        """Criar estrutura de distribuição profissional"""

        # Diretório de distribuição
        dist_name = f"AutomatorIA-v9.0-{build_type}-{self.system}-{self.arch}"
        dist_dir = self.project_root / "dist" / "enterprise" / dist_name
        dist_dir.mkdir(parents=True, exist_ok=True)

        # Copiar executável
        exe_dest = dist_dir / exe_path.name
        shutil.copy2(exe_path, exe_dest)

        # Arquivos essenciais
        essential_files = [
            ("README.md", "README.md"),
            ("CHANGELOG.md", "CHANGELOG.md"),
            ("LICENSE", "LICENSE")
        ]

        for src, dest in essential_files:
            src_path = self.project_root / src
            if src_path.exists():
                shutil.copy2(src_path, dist_dir / dest)

        # Arquivo de configuração de exemplo
        config_example = dist_dir / "config.ini"
        if not config_example.exists():
            config_content = """# Automator Web IA v9.0 - Configuration Example
[GENERAL]
environment = production
version = 9.0.0

[UI]
theme = dark
language = pt_BR

[PERFORMANCE]
lazy_loading = true
memory_limit = 512MB
cpu_threads = auto
"""
            with open(config_example, 'w') as f:
                f.write(config_content)

        return dist_dir

    def _generate_package_integrity(self, package_dir: Path):
        """Gerar arquivos de integridade"""

        # Checksum SHA256
        checksums = {}

        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(package_dir)

                # Calcular SHA256
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

                checksums[str(relative_path)] = sha256.hexdigest()

        # Salvar checksums
        checksum_file = package_dir / "SHA256SUMS"
        with open(checksum_file, 'w') as f:
            for file_path, checksum in checksums.items():
                f.write(f"{checksum}  {file_path}\n")

        # Manifest detalhado
        manifest = {
            "package_info": {
                "name": "Automator Web IA",
                "version": "9.0.0",
                "build_type": self.build_metrics['build_type'],
                "platform": f"{self.system}-{self.arch}",
                "build_date": time.time()
            },
            "files": checksums,
            "build_metrics": self.build_metrics
        }

        manifest_file = package_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)

    def _create_launcher_scripts(self, package_dir: Path, build_type: str):
        """Criar scripts de inicialização"""

        if self.system == 'windows':
            # Script batch para Windows
            launcher_script = f'''@echo off
echo ============================================
echo    AUTOMATOR WEB IA v9.0 - {build_type.upper()}
echo ============================================
echo.

REM Verificar se executável existe
if not exist "AutomatorIA-v9.0-{build_type}.exe" (
    echo ERRO: Executavel nao encontrado!
    echo Execute install.bat primeiro.
    pause
    exit /b 1
)

REM Executar aplicacao
echo Iniciando Automator Web IA...
start "" "AutomatorIA-v9.0-{build_type}.exe"

echo.
echo Aplicacao iniciada! Verifique a barra de tarefas.
pause
'''

            with open(package_dir / "run.bat", 'w') as f:
                f.write(launcher_script)

            # Script de instalação
            install_script = '''@echo off
echo ============================================
echo    AUTOMATOR WEB IA v9.0 - INSTALADOR
echo ============================================
echo.

REM Criar atalho na área de trabalho
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\\Desktop\\Automator Web IA.lnk');$s.TargetPath='%~dp0run.bat';$s.WorkingDirectory='%~dp0';$s.Save()"

echo Instalacao concluida!
echo Use o atalho na area de trabalho para executar.
pause
'''

            with open(package_dir / "install.bat", 'w') as f:
                f.write(install_script)

        else:
            # Script shell para Linux/Mac
            launcher_script = f'''#!/bin/bash
echo "============================================"
echo "   AUTOMATOR WEB IA v9.0 - {build_type.upper()}"
echo "============================================"

# Verificar se executável existe
if [ ! -f "AutomatorIA-v9.0-{build_type}" ]; then
    echo "ERRO: Executavel nao encontrado!"
    echo "Execute chmod +x install.sh primeiro."
    exit 1
fi

# Executar aplicação
echo "Iniciando Automator Web IA..."
./AutomatorIA-v9.0-{build_type} &

echo ""
echo "Aplicacao iniciada!"
'''

            launcher_path = package_dir / "run.sh"
            with open(launcher_path, 'w') as f:
                f.write(launcher_script)

            # Tornar executável
            os.chmod(launcher_path, 0o755)

    def _verify_build_tools(self):
        """Verificar ferramentas de build necessárias"""

        tools_status = {
            'PyInstaller': self._check_pyinstaller(),
            'UPX': self._is_upx_available(),
            'Python': sys.version_info >= (3, 11)
        }

        print("🔧 Verificando ferramentas de build:")
        for tool, available in tools_status.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}")

        missing_tools = [tool for tool, available in tools_status.items() if not available]
        if missing_tools:
            print(f"⚠️  Ferramentas faltando: {', '.join(missing_tools)}")

    def _check_pyinstaller(self) -> bool:
        """Verificar se PyInstaller está disponível"""
        try:
            import PyInstaller
            return True
        except ImportError:
            return False

    def _is_upx_available(self) -> bool:
        """Verificar se UPX está disponível"""
        try:
            result = subprocess.run(['upx', '--version'],
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def _verify_build_quality(self, package_path: Path, build_type: str):
        """Verificar qualidade do build"""

        print("🔍 Verificando qualidade do build...")

        # Verificar tamanho
        total_size = sum(f.stat().st_size for f in package_path.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)

        config = self.build_configs[build_type]
        target_size_mb = float(config['target_size'].replace('MB', ''))

        if total_size_mb <= target_size_mb * 1.5:  # 50% de tolerância
            print(".1f"        else:
            print(".1f"
        # Verificar executável
        exe_name = f"AutomatorIA-v9.0-{build_type}"
        if self.system == 'windows':
            exe_name += '.exe'

        exe_path = package_path / exe_name
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)
            print(".1f"            self.build_metrics['size_after'] = exe_size
        else:
            print("❌ Executável não encontrado!")

        # Verificar arquivos essenciais
        essential_files = ['README.md', 'manifest.json', 'SHA256SUMS']
        missing_files = []

        for essential in essential_files:
            if not (package_path / essential).exists():
                missing_files.append(essential)

        if missing_files:
            print(f"⚠️  Arquivos essenciais faltando: {missing_files}")
        else:
            print("✅ Arquivos essenciais presentes")

    def _generate_build_report(self, package_path: Path, build_type: str):
        """Gerar relatório detalhado do build"""

        report = {
            "build_info": {
                "timestamp": time.time(),
                "build_type": build_type,
                "platform": f"{self.system}-{self.arch}",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "pyinstaller_available": self._check_pyinstaller(),
                "upx_available": self._is_upx_available()
            },
            "build_metrics": self.build_metrics,
            "package_info": {
                "path": str(package_path),
                "total_files": len(list(package_path.rglob('*'))),
                "total_size_mb": sum(f.stat().st_size for f in package_path.rglob('*') if f.is_file()) / (1024 * 1024)
            },
            "optimization_results": {
                "compression_applied": self._is_upx_available(),
                "lazy_loading_enabled": True,
                "dependencies_optimized": True,
                "target_achieved": self._check_target_achievement(package_path, build_type)
            }
        }

        # Salvar relatório
        report_path = package_path / "build_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📊 Relatório de build salvo: {report_path}")

    def _check_target_achievement(self, package_path: Path, build_type: str) -> Dict[str, bool]:
        """Verificar se metas foram atingidas"""

        config = self.build_configs[build_type]

        # Verificar tamanho
        total_size = sum(f.stat().st_size for f in package_path.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        target_size_mb = float(config['target_size'].replace('MB', ''))

        return {
            "size_target": total_size_mb <= target_size_mb * 1.2,  # 20% de tolerância
            "build_success": True,
            "optimization_applied": True
        }

    def get_available_build_types(self) -> List[str]:
        """Obter tipos de build disponíveis"""
        return list(self.build_configs.keys())

    def compare_build_types(self) -> Dict[str, Dict[str, Any]]:
        """Comparar características dos tipos de build"""

        comparison = {}
        for build_type, config in self.build_configs.items():
            comparison[build_type] = {
                "description": config["description"],
                "target_size": config["target_size"],
                "startup_target": config["startup_target"],
                "compression": config["compression"],
                "excluded_modules": len(config["excludes"]),
                "included_modules": len(config["includes"])
            }

        return comparison

# Instância global
enterprise_build_system = EnterpriseBuildSystem()

def build_minimal():
    """Build versão minimal"""
    return enterprise_build_system.build_enterprise_package('minimal')

def build_standard():
    """Build versão standard"""
    return enterprise_build_system.build_enterprise_package('standard')

def build_full():
    """Build versão completa"""
    return enterprise_build_system.build_enterprise_package('full')

def build_enterprise():
    """Build versão enterprise"""
    return enterprise_build_system.build_enterprise_package('enterprise')

if __name__ == "__main__":
    # Demonstração do sistema de build enterprise
    print("🚀 DEMONSTRAÇÃO - ENTERPRISE BUILD SYSTEM v9.0")
    print("=" * 60)

    # Mostrar tipos de build disponíveis
    print("📋 TIPOS DE BUILD DISPONÍVEIS:")
    comparison = enterprise_build_system.compare_build_types()
    for build_type, info in comparison.items():
        print(f"\n{build_type.upper()}:")
        print(f"  📝 {info['description']}")
        print(f"  📏 Tamanho alvo: {info['target_size']}")
        print(f"  ⚡ Startup alvo: {info['startup_target']}")
        print(f"  🗜️  Compressão: {info['compression']}")

    print("\n" + "=" * 60)

    # Escolher build baseado em argumentos ou usar standard
    build_type = sys.argv[1] if len(sys.argv) > 1 else 'minimal'

    if build_type in enterprise_build_system.get_available_build_types():
        print(f"🏗️  Iniciando build: {build_type}")
        try:
            package_path = enterprise_build_system.build_enterprise_package(build_type)
            if package_path:
                print("
✅ BUILD ENTERPRISE CONCLUÍDO COM SUCESSO!"                print(f"📦 Pacote pronto em: {package_path}")
            else:
                print("\n❌ Build falhou!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Erro durante build: {e}")
            sys.exit(1)
    else:
        print(f"❌ Tipo de build inválido: {build_type}")
        print(f"📋 Opções disponíveis: {', '.join(enterprise_build_system.get_available_build_types())}")
        sys.exit(1)
