#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script para o Automatizador IA
Sistema inteligente de automação de login
"""

from setuptools import setup, find_packages
import os

# Ler README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Ler requirements
def read_requirements():
    with open('config/requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Metadados do projeto
setup(
    name="automatizador-ia",
    version="4.0.0",
    author="Sistema Automatizado",
    author_email="suporte@automatizador-ia.com",
    description="Sistema inteligente de automação de login com IA integrada",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-repo/automatizador-ia",
    project_urls={
        "Bug Tracker": "https://github.com/seu-repo/automatizador-ia/issues",
        "Documentation": "https://github.com/seu-repo/automatizador-ia/docs",
        "Source Code": "https://github.com/seu-repo/automatizador-ia",
    },

    # Classificação do projeto
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],

    # Dependências
    python_requires=">=3.8",
    install_requires=read_requirements(),

    # Pacotes
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Scripts de entrada
    entry_points={
        "console_scripts": [
            "automatizador-ia=src.main:main",
        ],
        "gui_scripts": [
            "automatizador-gui=src.main:main",
        ]
    },

    # Arquivos de dados
    package_data={
        "": ["*.ini", "*.md", "*.txt"],
    },
    include_package_data=True,

    # Metadados extras
    keywords="automation login selenium webdriver ai intelligent",
    license="MIT",

    # Plataformas suportadas
    platforms=["Windows", "Linux", "MacOS"],

    # Opções extras
    zip_safe=False,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
)
