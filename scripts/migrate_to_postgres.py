#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIGRAÇÃO PARA POSTGRESQL ENTERPRISE
Script completo para migração de SQLite para PostgreSQL com validação
"""

import os
import sys
import json
import sqlite3
import psycopg2
import psycopg2.extras
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

# Adiciona src ao path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseMigration:
    """Gerenciador de migração de banco de dados"""

    def __init__(self,
                 sqlite_path: str = "./data/automator.db",
                 postgres_url: str = "postgresql://automator:automator_pass@localhost:5432/automator_db"):
        self.sqlite_path = Path(sqlite_path)
        self.postgres_url = postgres_url
        self.backup_dir = project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Estatísticas da migração
        self.stats = {
            'tables_migrated': 0,
            'records_migrated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    def validate_prerequisites(self) -> bool:
        """Valida pré-requisitos da migração"""
        logger.info("🔍 Validando pré-requisitos da migração...")

        issues = []

        # Verificar se SQLite existe
        if not self.sqlite_path.exists():
            issues.append(f"Arquivo SQLite não encontrado: {self.sqlite_path}")

        # Verificar conexão PostgreSQL
        try:
            conn = psycopg2.connect(self.postgres_url)
            conn.close()
        except Exception as e:
            issues.append(f"Erro de conexão PostgreSQL: {e}")

        # Verificar espaço em disco
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024**3)
            if free_gb < 5:
                issues.append(".1f"        except ImportError:
            logger.warning("Não foi possível verificar espaço em disco")

        # Verificar se PostgreSQL tem as extensões necessárias
        try:
            conn = psycopg2.connect(self.postgres_url)
            cur = conn.cursor()

            # Verificar extensão UUID
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'uuid-ossp';")
            if not cur.fetchone():
                logger.warning("Extensão uuid-ossp não encontrada - será criada automaticamente")

            # Verificar extensão pg_stat_statements para monitoring
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'pg_stat_statements';")
            if not cur.fetchone():
                logger.warning("Extensão pg_stat_statements não encontrada - recomendado para monitoring")

            cur.close()
            conn.close()

        except Exception as e:
            issues.append(f"Erro ao verificar extensões PostgreSQL: {e}")

        if issues:
            logger.error("❌ Pré-requisitos não atendidos:")
            for issue in issues:
                logger.error(f"  • {issue}")
            return False

        logger.info("✅ Pré-requisitos validados com sucesso")
        return True

    def create_backup(self) -> Optional[str]:
        """Cria backup do banco SQLite"""
        logger.info("💾 Criando backup do banco SQLite...")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"automator_sqlite_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name

            # Copiar arquivo
            import shutil
            shutil.copy2(self.sqlite_path, backup_path)

            # Calcular hash para verificação
            with open(backup_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Salvar metadados
            metadata = {
                'original_file': str(self.sqlite_path),
                'backup_file': str(backup_path),
                'timestamp': timestamp,
                'file_size': backup_path.stat().st_size,
                'file_hash': file_hash
            }

            metadata_file = backup_path.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Backup criado: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None

    def analyze_sqlite_schema(self) -> Dict[str, Any]:
        """Analisa schema do SQLite"""
        logger.info("📊 Analisando schema do SQLite...")

        schema = {
            'tables': {},
            'indexes': {},
            'triggers': {},
            'views': {}
        }

        try:
            conn = sqlite3.connect(self.sqlite_path)
            cur = conn.cursor()

            # Buscar tabelas
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cur.fetchall()

            for (table_name,) in tables:
                # Schema da tabela
                cur.execute(f"PRAGMA table_info({table_name});")
                columns = cur.fetchall()

                # Indexes da tabela
                cur.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';")
                indexes = cur.fetchall()

                # Foreign keys
                cur.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = cur.fetchall()

                schema['tables'][table_name] = {
                    'columns': columns,
                    'indexes': indexes,
                    'foreign_keys': foreign_keys,
                    'row_count': self._get_table_row_count(cur, table_name)
                }

            cur.close()
            conn.close()

            logger.info(f"✅ Schema analisado: {len(schema['tables'])} tabelas encontradas")
            return schema

        except Exception as e:
            logger.error(f"❌ Erro ao analisar schema: {e}")
            return schema

    def _get_table_row_count(self, cursor, table_name: str) -> int:
        """Conta registros em uma tabela"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            return cursor.fetchone()[0]
        except Exception:
            return 0

    def create_postgres_schema(self, schema: Dict[str, Any]) -> bool:
        """Cria schema no PostgreSQL"""
        logger.info("🏗️ Criando schema no PostgreSQL...")

        try:
            conn = psycopg2.connect(self.postgres_url)
            conn.autocommit = True
            cur = conn.cursor()

            # Criar extensões necessárias
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";")

            # Mapeamento de tipos SQLite para PostgreSQL
            type_mapping = {
                'INTEGER': 'BIGINT',
                'REAL': 'DOUBLE PRECISION',
                'TEXT': 'TEXT',
                'BLOB': 'BYTEA',
                'NUMERIC': 'DECIMAL',
                'BOOLEAN': 'BOOLEAN',
                'DATETIME': 'TIMESTAMP WITH TIME ZONE',
                'DATE': 'DATE'
            }

            # Criar tabelas
            for table_name, table_info in schema['tables'].items():
                self._create_postgres_table(cur, table_name, table_info, type_mapping)

            # Criar indexes
            for table_name, table_info in schema['tables'].items():
                self._create_postgres_indexes(cur, table_name, table_info)

            cur.close()
            conn.close()

            logger.info("✅ Schema PostgreSQL criado com sucesso")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao criar schema PostgreSQL: {e}")
            return False

    def _create_postgres_table(self, cur, table_name: str, table_info: Dict[str, Any], type_mapping: Dict[str, str]):
        """Cria tabela no PostgreSQL"""
        columns = []

        for col in table_info['columns']:
            # col = (cid, name, type, notnull, dflt_value, pk)
            col_name = col[1]
            col_type = col[2].upper() if col[2] else 'TEXT'
            postgres_type = type_mapping.get(col_type, 'TEXT')

            # Ajustes específicos
            if col_name.lower() in ['id', 'uuid'] and postgres_type == 'BIGINT':
                postgres_type = 'UUID DEFAULT uuid_generate_v4() PRIMARY KEY'
            elif 'timestamp' in col_name.lower() or 'created_at' in col_name.lower():
                postgres_type = 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'

            # NOT NULL
            not_null = "NOT NULL" if col[3] else ""

            # Default value
            default = ""
            if col[4] is not None:
                default = f"DEFAULT {col[4]}"

            columns.append(f"{col_name} {postgres_type} {not_null} {default}".strip())

        # Criar tabela
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
        cur.execute(create_sql)

        logger.debug(f"Tabela criada: {table_name}")

    def _create_postgres_indexes(self, cur, table_name: str, table_info: Dict[str, Any]):
        """Cria indexes no PostgreSQL"""
        for index_sql in table_info.get('indexes', []):
            if index_sql and index_sql[0]:
                # Adaptar SQL do SQLite para PostgreSQL
                pg_index_sql = index_sql[0].replace('AUTOINCREMENT', '').replace('PRIMARY KEY', '')
                try:
                    cur.execute(pg_index_sql)
                    logger.debug(f"Index criado para {table_name}")
                except Exception as e:
                    logger.warning(f"Erro ao criar index: {e}")

    def migrate_data(self, schema: Dict[str, Any]) -> bool:
        """Migra dados do SQLite para PostgreSQL"""
        logger.info("🚚 Migrando dados...")

        self.stats['start_time'] = datetime.now()

        try:
            # Conexões
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            pg_conn = psycopg2.connect(self.postgres_url)
            pg_conn.autocommit = False

            sqlite_cur = sqlite_conn.cursor()
            pg_cur = pg_conn.cursor()

            # Migrar cada tabela
            for table_name, table_info in schema['tables'].items():
                if not self._migrate_table(sqlite_cur, pg_cur, table_name, table_info):
                    raise Exception(f"Falha na migração da tabela {table_name}")

            # Commit final
            pg_conn.commit()

            sqlite_cur.close()
            pg_cur.close()
            sqlite_conn.close()
            pg_conn.close()

            self.stats['end_time'] = datetime.now()
            logger.info("✅ Migração de dados concluída com sucesso")
            return True

        except Exception as e:
            logger.error(f"❌ Erro na migração de dados: {e}")
            try:
                if 'pg_conn' in locals():
                    pg_conn.rollback()
            except:
                pass
            return False

    def _migrate_table(self, sqlite_cur, pg_cur, table_name: str, table_info: Dict[str, Any]) -> bool:
        """Migra uma tabela específica"""
        try:
            logger.info(f"Migrando tabela: {table_name}")

            # Buscar dados do SQLite
            sqlite_cur.execute(f"SELECT * FROM {table_name};")
            rows = sqlite_cur.fetchall()

            if not rows:
                logger.info(f"Tabela {table_name} vazia, pulando...")
                return True

            # Inserir no PostgreSQL
            columns = [col[1] for col in table_info['columns']]
            placeholders = ','.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders});"

            # Inserir em batches para performance
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                pg_cur.executemany(insert_sql, batch)

                self.stats['records_migrated'] += len(batch)
                logger.debug(f"Migrados {len(batch)} registros de {table_name}")

            self.stats['tables_migrated'] += 1
            logger.info(f"✅ Tabela {table_name} migrada: {len(rows)} registros")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao migrar tabela {table_name}: {e}")
            self.stats['errors'] += 1
            return False

    def validate_migration(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Valida integridade da migração"""
        logger.info("🔍 Validando migração...")

        validation = {
            'passed': True,
            'table_counts': {},
            'discrepancies': [],
            'errors': []
        }

        try:
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            pg_conn = psycopg2.connect(self.postgres_url)

            sqlite_cur = sqlite_conn.cursor()
            pg_cur = pg_conn.cursor()

            for table_name in schema['tables'].keys():
                try:
                    # Contar registros SQLite
                    sqlite_cur.execute(f"SELECT COUNT(*) FROM {table_name};")
                    sqlite_count = sqlite_cur.fetchone()[0]

                    # Contar registros PostgreSQL
                    pg_cur.execute(f"SELECT COUNT(*) FROM {table_name};")
                    pg_count = pg_cur.fetchone()[0]

                    validation['table_counts'][table_name] = {
                        'sqlite': sqlite_count,
                        'postgres': pg_count
                    }

                    if sqlite_count != pg_count:
                        validation['passed'] = False
                        validation['discrepancies'].append({
                            'table': table_name,
                            'sqlite_count': sqlite_count,
                            'postgres_count': pg_count,
                            'difference': abs(sqlite_count - pg_count)
                        })

                except Exception as e:
                    validation['passed'] = False
                    validation['errors'].append(f"Erro na validação de {table_name}: {e}")

            sqlite_cur.close()
            pg_cur.close()
            sqlite_conn.close()
            pg_conn.close()

        except Exception as e:
            validation['passed'] = False
            validation['errors'].append(f"Erro geral na validação: {e}")

        if validation['passed']:
            logger.info("✅ Validação da migração passou!")
        else:
            logger.error("❌ Problemas encontrados na validação:")
            for disc in validation['discrepancies']:
                logger.error(f"  • {disc['table']}: SQLite={disc['sqlite_count']}, PostgreSQL={disc['postgres_count']}")

        return validation

    def generate_report(self) -> str:
        """Gera relatório da migração"""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        report = f"""
MIGRAÇÃO DATABASE - RELATÓRIO FINAL
{'=' * 50}

📊 ESTATÍSTICAS GERAIS:
• Tabelas migradas: {self.stats['tables_migrated']}
• Registros migrados: {self.stats['records_migrated']:,}
• Erros encontrados: {self.stats['errors']}
• Tempo total: {duration:.2f}s se duration else 'N/A'}

🔄 PERFORMANCE:
• Registros/segundo: {self.stats['records_migrated'] / duration:.0f} se duration and duration > 0 else 'N/A'}

✅ STATUS: {'SUCESSO' if self.stats['errors'] == 0 else 'PARCIAL'}

📝 DETALHES:
• Arquivo SQLite: {self.sqlite_path}
• PostgreSQL URL: {self.postgres_url.replace('://', '://[REDACTED]@') if '://' in self.postgres_url else self.postgres_url}
• Timestamp: {datetime.now().isoformat()}

⚠️  RECOMENDAÇÕES PÓS-MIGRAÇÃO:
• Execute testes funcionais na aplicação
• Verifique logs por erros relacionados ao banco
• Atualize connection strings na configuração
• Considere otimizar indexes baseado em queries comuns
• Configure backups automáticos do PostgreSQL
"""

        return report.strip()

    def run_full_migration(self) -> bool:
        """Executa migração completa"""
        logger.info("🚀 Iniciando migração completa SQLite → PostgreSQL")

        try:
            # 1. Validar pré-requisitos
            if not self.validate_prerequisites():
                return False

            # 2. Criar backup
            backup_path = self.create_backup()
            if not backup_path:
                logger.error("Falha ao criar backup - abortando migração")
                return False

            # 3. Analisar schema
            schema = self.analyze_sqlite_schema()
            if not schema['tables']:
                logger.error("Nenhuma tabela encontrada para migrar")
                return False

            # 4. Criar schema PostgreSQL
            if not self.create_postgres_schema(schema):
                return False

            # 5. Migrar dados
            if not self.migrate_data(schema):
                return False

            # 6. Validar migração
            validation = self.validate_migration(schema)
            if not validation['passed']:
                logger.error("Validação da migração falhou!")
                return False

            # 7. Gerar relatório
            report = self.generate_report()
            logger.info("\n" + report)

            # Salvar relatório
            report_file = self.backup_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            logger.info(f"✅ Migração concluída com sucesso! Relatório salvo em: {report_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro crítico na migração: {e}")
            return False


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Migração SQLite para PostgreSQL - Automator Web IA v8.0')
    parser.add_argument('--sqlite-path', default='./data/automator.db', help='Caminho do arquivo SQLite')
    parser.add_argument('--postgres-url', help='URL de conexão PostgreSQL')
    parser.add_argument('--dry-run', action='store_true', help='Executar apenas validação (sem migrar)')

    args = parser.parse_args()

    # Se não especificado, usar variável de ambiente
    postgres_url = args.postgres_url or os.environ.get('DATABASE_URL')
    if not postgres_url:
        logger.error("PostgreSQL URL não especificada. Use --postgres-url ou variável DATABASE_URL")
        sys.exit(1)

    # Executar migração
    migration = DatabaseMigration(args.sqlite_path, postgres_url)

    if args.dry_run:
        logger.info("🔍 Executando validação (dry-run)...")
        success = migration.validate_prerequisites()
        if success:
            schema = migration.analyze_sqlite_schema()
            logger.info(f"📊 Schema analisado: {len(schema['tables'])} tabelas encontradas")
        sys.exit(0 if success else 1)

    success = migration.run_full_migration()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
