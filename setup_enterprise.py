#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SETUP ENTERPRISE v9.0 - Automator Web IA
Setup profissional com lazy loading e conditional dependencies
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from typing import Dict, List, Any

# Constants
VERSION = "9.0.0"
AUTHOR = "Automator IA Enterprise"
AUTHOR_EMAIL = "enterprise@automator.webia.com"
DESCRIPTION = "Automator Web IA - Enterprise Web Automation Platform"
URL = "https://automator.webia.com"

def get_requirements() -> Dict[str, List[str]]:
    """Obter requirements organizados por categoria"""

    requirements = {
        'core': [
            'PySide6>=6.6.0',
            'PySide6-Qt6>=6.6.0',
            'sqlalchemy>=2.0.23',
            'loguru>=0.7.2',
            'pydantic>=2.6.0',
        ],

        'ai': [
            'torch>=2.1.2',
            'transformers>=4.36.0',
            'openai>=1.3.0',
            'anthropic>=0.7.8',
            'scikit-learn>=1.4.0',
            'numpy>=1.26.2',
        ],

        'vision': [
            'opencv-python>=4.8.1',
            'Pillow>=10.1.0',
            'scikit-image>=0.21.0',
        ],

        'web': [
            'fastapi>=0.108.0',
            'uvicorn>=0.25.0',
            'strawberry-graphql>=0.235.0',
            'httpx>=0.26.0',
            'aiohttp>=3.9.1',
        ],

        'database': [
            'psycopg2-binary>=2.9.9',
            'redis>=5.0.1',
            'alembic>=1.13.0',
        ],

        'automation': [
            'playwright>=1.45.0',
            'selenium>=4.20.0',
            'webdriver-manager>=4.0.1',
            'undetected-chromedriver>=3.5.4',
        ],

        'monitoring': [
            'prometheus-client>=0.19.0',
            'sentry-sdk>=1.38.0',
            'grafana-api>=1.0.3',
            'opentelemetry-distro>=0.44b0',
            'opentelemetry-instrumentation>=0.44b0',
        ],

        'security': [
            'cryptography>=41.0.7',
            'bcrypt>=4.1.2',
            'python-jose>=3.3.0',
            'passlib>=1.7.4',
            'python-multipart>=0.0.6',
        ],

        'enterprise': [
            'kubernetes>=28.1.0',
            'docker>=7.0.0',
            'boto3>=1.34.0',
            'azure-storage-blob>=12.19.0',
        ],

        'dev': [
            'pytest>=7.4.3',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'black>=23.12.1',
            'isort>=5.13.2',
            'mypy>=1.7.1',
            'flake8>=6.1.0',
            'pre-commit>=3.6.0',
            'locust>=2.17.0',
        ],

        'build': [
            'pyinstaller>=6.3.0',
            'cx-Freeze>=6.15',
        ],
    }

    # Adicionar system dependencies
    if sys.platform == 'win32':
        requirements['core'].extend([
            'pywin32>=306',
            'winshell>=0.6',
        ])
    else:
        requirements['core'].append('python-magic>=0.4.27')

    return requirements

def get_install_requires() -> List[str]:
    """Dependencies obrigatórias (core)"""
    return get_requirements()['core']

def get_extras_require() -> Dict[str, List[str]]:
    """Dependencies opcionais por categoria"""
    reqs = get_requirements()

    # Remover core das extras
    extras = {k: v for k, v in reqs.items() if k != 'core'}

    # Adicionar combinações comuns
    extras['all'] = []
    for category_reqs in extras.values():
        extras['all'].extend(category_reqs)

    extras['full'] = extras['all']  # Alias

    # Desktop (GUI + automation básica)
    extras['desktop'] = reqs['automation'] + reqs.get('database', [])

    # Server (API + monitoring)
    extras['server'] = reqs['web'] + reqs['monitoring'] + reqs['database'] + reqs['security']

    # AI Complete
    extras['ai-full'] = reqs['ai'] + reqs['vision']

    return extras

def get_package_data() -> Dict[str, List[str]]:
    """Arquivos de dados a incluir"""
    return {
        'automator': [
            'config/*.json',
            'config/*.yaml',
            'config/*.yml',
            'assets/*',
            'docs/*',
            'templates/*',
        ]
    }

def get_entry_points() -> Dict[str, List[str]]:
    """Entry points para linha de comando"""
    return {
        'console_scripts': [
            'automator=src.presentation.cli.automator_cli:main',
            'automator-gui=launcher_enterprise:main',
            'automator-api=src.presentation.apis.fastapi_app:start_server',
        ],
        'gui_scripts': [
            'automator-desktop=launcher_enterprise:main',
        ]
    }

def get_classifiers() -> List[str]:
    """Classificadores PyPI"""
    return [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
    ]

def pre_install_checks():
    """Verificações pré-instalação"""
    print("🔍 Verificando pré-requisitos...")

    # Python version
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ requerido. Encontrado: {sys.version}")
        sys.exit(1)

    # Platform check
    supported_platforms = ['win32', 'linux', 'darwin']
    if sys.platform not in supported_platforms:
        print(f"⚠️ Plataforma {sys.platform} não testada oficialmente")

    print("✅ Pré-requisitos OK")

def post_install_setup():
    """Setup pós-instalação"""
    print("🔧 Executando setup pós-instalação...")

    try:
        # Criar diretórios necessários
        dirs = ['data', 'logs', 'cache', 'backups']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)

        # Configuração inicial
        config = {
            'version': VERSION,
            'installed_at': str(Path.cwd()),
            'platform': sys.platform,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }

        import json
        with open('automator_install.json', 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ Setup concluído")

    except Exception as e:
        print(f"⚠️ Setup pós-instalação falhou: {e}")

# Executar checks pré-instalação
pre_install_checks()

# Configuração principal do setup
setup(
    # Basic info
    name="automator-web-ia-enterprise",
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=Path("README.md").read_text(encoding='utf-8') if Path("README.md").exists() else DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,

    # Packages
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=get_package_data(),

    # Dependencies
    python_requires=">=3.11,<3.13",
    install_requires=get_install_requires(),
    extras_require=get_extras_require(),

    # Entry points
    entry_points=get_entry_points(),

    # Classifiers
    classifiers=get_classifiers(),

    # Additional metadata
    keywords="automation web ia machine-learning playwright selenium enterprise",
    project_urls={
        "Documentation": "https://docs.automator.webia.com",
        "Source": "https://github.com/automator/webia",
        "Tracker": "https://github.com/automator/webia/issues",
        "Changelog": "https://github.com/automator/webia/blob/main/CHANGELOG.md",
    },

    # Additional options
    zip_safe=False,
    include_package_data=True,
)

# Executar setup pós-instalação
post_install_setup()
