-- ===== AUTOMATOR WEB IA v8.0 - DATABASE INITIALIZATION =====
-- Script de inicialização do banco de dados PostgreSQL

-- Criar schema principal se não existir
CREATE SCHEMA IF NOT EXISTS automator;

-- Configurar permissões
GRANT ALL PRIVILEGES ON SCHEMA automator TO automator;
GRANT ALL PRIVILEGES ON DATABASE automator_db TO automator;

-- Configurar search_path
ALTER ROLE automator SET search_path TO automator, public;

-- Criar tabelas básicas (se necessário)
-- As tabelas serão criadas automaticamente pelo SQLAlchemy
-- Este script serve apenas para inicialização básica

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE 'Automator Web IA v8.0 - Database initialized successfully';
END
$$;
