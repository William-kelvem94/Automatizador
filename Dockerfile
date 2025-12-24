# ===== AUTOMATOR WEB IA v8.0 - ENTERPRISE DOCKERFILE =====
# Multi-stage build para otimização máxima e segurança

# =============================================================================
# STAGE 1: BUILDER - Construção e compilação de dependências
# =============================================================================
FROM python:3.11-slim as builder

# Labels para metadados
LABEL maintainer="Automator IA Enterprise <enterprise@automator.webia.com>"
LABEL version="8.0.0"
LABEL description="Automator Web IA - Enterprise Web Automation Platform"

# Argumentos de build
ARG BUILDKIT_INLINE_CACHE=1
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PYTHONUNBUFFERED=1

# Configurações de segurança e otimização
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependências de sistema para compilação
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libpq-dev \
    libsqlite3-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libncursesw5-dev \
    libgdbm-dev \
    libnss3-dev \
    tk-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para build
RUN groupadd -r automator && useradd -r -g automator automator

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para cache de layers
COPY config/requirements.txt /app/requirements.txt

# Instalar dependências Python em virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências com otimizações
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# =============================================================================
# STAGE 2: PLAYWRIGHT BROWSERS - Instalação otimizada de browsers
# =============================================================================
FROM builder as playwright-setup

# Instalar Node.js para Playwright
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Instalar Playwright browsers de forma simplificada
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/* && \
    pip install playwright==1.45.0 && \
    playwright install chromium --with-deps || playwright install chromium

# =============================================================================
# STAGE 3: PYINSTALLER BUILD - Criação do executável standalone
# =============================================================================
FROM playwright-setup as pyinstaller-build

# Instalar PyInstaller
RUN pip install pyinstaller==6.3.0

# Copiar código fonte
COPY . /app/src/

# Configurar para build
WORKDIR /app/src

# Criar executável com PyInstaller
RUN pyinstaller \
    --clean \
    --noconfirm \
    --onedir \
    --name automator-webia \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtWidgets \
    --hidden-import playwright \
    --hidden-import loguru \
    --hidden-import pydantic \
    --hidden-import fastapi \
    --hidden-import uvicorn \
    --hidden-import sqlalchemy \
    --hidden-import redis \
    --add-data "src:src" \
    --add-data "config:config" \
    --runtime-hook build/runtime_hooks/qt_fixes.py \
    --runtime-hook build/runtime_hooks/playwright_fixes.py \
    --runtime-hook build/runtime_hooks/environment_setup.py \
    launcher.py

# =============================================================================
# STAGE 4: RUNTIME OPTIMIZATION - Imagem final ultra-otimizada
# =============================================================================
FROM ubuntu:22.04 AS runtime

# Labels atualizados
LABEL maintainer="Automator IA Enterprise <enterprise@automator.webia.com>"
LABEL version="8.0.0"
LABEL description="Automator Web IA - Enterprise Web Automation Platform"

# Argumentos de runtime
ARG APP_USER=automator
ARG APP_GROUP=automator
ARG APP_UID=1001
ARG APP_GID=1001

# Configurações de segurança
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    # Configurações da aplicação
    AUTOMATOR_ENV=production \
    AUTOMATOR_VERSION=8.0.0 \
    AUTOMATOR_BUILD_TYPE=container \
    # Configurações de segurança
    QTWEBENGINE_DISABLE_SANDBOX=1 \
    QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu" \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    # Configurações de performance
    PYTHONOPTIMIZE=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1

# Instalar dependências de runtime mínimas
RUN apt-get update && apt-get install -y \
    # Dependências básicas
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libfontconfig1 \
    libfreetype6 \
    libgbm1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    procps \
    wget \
    xdg-utils \
    # Dependências adicionais para Qt/WebEngine
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    # Dependências para gráficos e renderização
    libegl1 \
    libgl1 \
    libgles2 \
    libopengl0 \
    # Dependências para áudio
    libpulse0 \
    # Ferramentas de diagnóstico
    curl \
    htop \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN groupadd -r -g ${APP_GID} ${APP_GROUP} && \
    useradd -r -u ${APP_UID} -g ${APP_GROUP} -s /bin/bash -c "Automator Web IA" ${APP_USER}

# Criar diretórios necessários
RUN mkdir -p \
    /app \
    /app/data \
    /app/logs \
    /app/cache \
    /app/temp \
    /app/browsers \
    && chown -R ${APP_USER}:${APP_GROUP} /app

# Copiar executável do stage de build
COPY --from=pyinstaller-build --chown=${APP_USER}:${APP_GROUP} /app/src/dist/automator-webia /app/

# Copiar browsers do Playwright
COPY --from=playwright-setup --chown=${APP_USER}:${APP_GROUP} /root/.cache/ms-playwright /app/browsers/

# Copiar arquivos de configuração e documentação
COPY --chown=${APP_USER}:${APP_GROUP} \
    config/ \
    docs/ \
    README.md \
    CHANGELOG.md \
    /app/

# Configurar permissões
RUN chmod +x /app/automator-webia && \
    chmod -R 755 /app

# Mudar para usuário não-root
USER ${APP_USER}

# Configurar ambiente
ENV PATH="/app:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH="/app/browsers" \
    AUTOMATOR_DATA_DIR="/app/data" \
    AUTOMATOR_LOG_DIR="/app/logs" \
    AUTOMATOR_CACHE_DIR="/app/cache" \
    AUTOMATOR_TEMP_DIR="/app/temp"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expor portas
EXPOSE 8000 3000

# Volumes para persistência
VOLUME ["/app/data", "/app/logs", "/app/cache"]

# Comando padrão
CMD ["/app/automator-webia", "--web-api", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# STAGE 5: DEBUGGING (opcional) - Para desenvolvimento e debug
# =============================================================================
FROM runtime as debug

# Instalar ferramentas de debug
USER root
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    htop \
    net-tools \
    iputils-ping \
    dnsutils \
    telnet \
    curl \
    wget \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Instalar debugpy para debugging remoto
RUN pip3 install debugpy

# Voltar para usuário não-root
USER ${APP_USER}

# Comando de debug
CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "/app/automator-webia", "--debug"]

# =============================================================================
# METADATA E CONFIGURAÇÕES FINAIS
# =============================================================================

# Labels finais
LABEL org.opencontainers.image.title="Automator Web IA v8.0" \
      org.opencontainers.image.description="Enterprise Web Automation Platform" \
      org.opencontainers.image.version="8.0.0" \
      org.opencontainers.image.vendor="Automator IA Enterprise" \
      org.opencontainers.image.licenses="Enterprise" \
      org.opencontainers.image.source="https://github.com/automator/webia" \
      org.opencontainers.image.documentation="https://docs.automator.webia.com"

# Security scanning annotations
LABEL security.scan.source="trivy" \
      security.scan.schedule="daily" \
      security.scan.critical="block"

# Performance annotations
LABEL performance.cpu.min="1" \
      performance.memory.min="2GB" \
      performance.disk.min="10GB"

# Monitoring annotations
LABEL monitoring.enabled="true" \
      monitoring.endpoints="/health,/metrics" \
      monitoring.logs="json"

# Backup annotations
LABEL backup.enabled="true" \
      backup.schedule="daily" \
      backup.retention="30d"
