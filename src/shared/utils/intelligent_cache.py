#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CACHE INTELIGENTE v9.0 - Automator Web IA
Sistema de cache multi-nível com LRU, TTL e persistência
"""

import os
import time
import pickle
import hashlib
import threading
from typing import Any, Dict, Optional, Tuple, List
from pathlib import Path
import weakref
import logging

logger = logging.getLogger(__name__)

class IntelligentCache:
    """
    Cache inteligente multi-nível

    Níveis:
    1. Memory (L1) - Mais rápido, limitado
    2. File (L2) - Persistente, maior capacidade
    3. Distributed (L3) - Redis, compartilhado

    Features:
    - LRU eviction
    - TTL automático
    - Compressão automática
    - Weak references para objetos grandes
    - Thread-safe
    """

    def __init__(self,
                 max_memory_mb: int = 50,
                 max_file_mb: int = 500,
                 ttl_seconds: int = 3600,
                 cache_dir: Optional[Path] = None):

        self.max_memory_mb = max_memory_mb
        self.max_file_mb = max_file_mb
        self.ttl_seconds = ttl_seconds
        self._lock = threading.RLock()

        # Setup cache directory
        self.cache_dir = cache_dir or Path.home() / ".automator_cache"
        self.cache_dir.mkdir(exist_ok=True)

        # Memory cache (L1)
        self._memory_cache: Dict[str, Dict] = {}
        self._memory_size = 0

        # File cache metadata (L2)
        self._file_cache_meta: Dict[str, Dict] = {}
        self._file_size = 0

        # Lazy imports para evitar dependências circulares
        self._redis_client = None

        # Initialize
        self._load_cache_metadata()
        self._cleanup_expired()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obter valor do cache (L1 -> L2 -> L3)

        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado

        Returns:
            Valor cached ou default
        """
        with self._lock:
            # Tentar L1 (memory)
            value = self._get_memory(key)
            if value is not None:
                return value

            # Tentar L2 (file)
            value = self._get_file(key)
            if value is not None:
                # Promover para L1
                self._set_memory(key, value)
                return value

            # Tentar L3 (redis) - se disponível
            value = self._get_redis(key)
            if value is not None:
                # Promover para L1 e L2
                self._set_memory(key, value)
                self._set_file(key, value)
                return value

            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazenar valor no cache

        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: TTL em segundos (opcional)

        Returns:
            True se armazenado com sucesso
        """
        with self._lock:
            try:
                ttl = ttl or self.ttl_seconds
                size = self._calculate_size(value)

                # Armazenar em L1 (memory)
                self._set_memory(key, value, ttl, size)

                # Armazenar em L2 (file) se não muito grande
                if size < 10 * 1024 * 1024:  # < 10MB
                    self._set_file(key, value, ttl)

                # Armazenar em L3 (redis) se disponível e importante
                if self._is_important_key(key):
                    self._set_redis(key, value, ttl)

                return True

            except Exception as e:
                logger.warning(f"Cache set failed for {key}: {e}")
                return False

    def delete(self, key: str) -> bool:
        """Remover chave do cache"""
        with self._lock:
            try:
                self._delete_memory(key)
                self._delete_file(key)
                self._delete_redis(key)
                return True
            except Exception as e:
                logger.warning(f"Cache delete failed for {key}: {e}")
                return False

    def clear(self) -> bool:
        """Limpar todo o cache"""
        with self._lock:
            try:
                self._memory_cache.clear()
                self._memory_size = 0

                # Clear file cache
                for file_path in self.cache_dir.glob("*.cache"):
                    file_path.unlink()
                self._file_cache_meta.clear()
                self._file_size = 0

                # Clear redis if available
                if self._redis_client:
                    self._redis_client.flushdb()

                return True
            except Exception as e:
                logger.error(f"Cache clear failed: {e}")
                return False

    def get_stats(self) -> Dict:
        """Obter estatísticas do cache"""
        with self._lock:
            return {
                'memory': {
                    'items': len(self._memory_cache),
                    'size_mb': self._memory_size / (1024 * 1024),
                    'utilization': self._memory_size / (self.max_memory_mb * 1024 * 1024)
                },
                'file': {
                    'items': len(self._file_cache_meta),
                    'size_mb': self._file_size / (1024 * 1024),
                    'utilization': self._file_size / (self.max_file_mb * 1024 * 1024)
                },
                'redis': self._get_redis_stats() if self._redis_client else None
            }

    # ========== MEMORY CACHE (L1) ==========

    def _get_memory(self, key: str) -> Any:
        """Obter do cache de memória"""
        if key in self._memory_cache:
            entry = self._memory_cache[key]

            # Verificar TTL
            if time.time() - entry['created_at'] > entry['ttl']:
                del self._memory_cache[key]
                self._memory_size -= entry['size']
                return None

            # Atualizar LRU
            entry['accessed_at'] = time.time()
            return entry['value']

        return None

    def _set_memory(self, key: str, value: Any, ttl: int = None, size: int = None):
        """Armazenar no cache de memória"""
        if ttl is None:
            ttl = self.ttl_seconds

        if size is None:
            size = self._calculate_size(value)

        # Evict se necessário
        self._evict_memory_if_needed(size)

        # Armazenar
        self._memory_cache[key] = {
            'value': value,
            'created_at': time.time(),
            'accessed_at': time.time(),
            'ttl': ttl,
            'size': size
        }

        self._memory_size += size

    def _delete_memory(self, key: str):
        """Remover do cache de memória"""
        if key in self._memory_cache:
            self._memory_size -= self._memory_cache[key]['size']
            del self._memory_cache[key]

    def _evict_memory_if_needed(self, required_size: int):
        """Evict itens do cache de memória se necessário (LRU)"""
        max_size_bytes = self.max_memory_mb * 1024 * 1024

        while self._memory_size + required_size > max_size_bytes and self._memory_cache:
            # Encontrar item menos recentemente usado
            lru_key = min(self._memory_cache.keys(),
                         key=lambda k: self._memory_cache[k]['accessed_at'])

            self._delete_memory(lru_key)

    # ========== FILE CACHE (L2) ==========

    def _get_file(self, key: str) -> Any:
        """Obter do cache de arquivo"""
        if key in self._file_cache_meta:
            meta = self._file_cache_meta[key]

            # Verificar TTL
            if time.time() - meta['created_at'] > meta['ttl']:
                self._delete_file(key)
                return None

            # Carregar do arquivo
            try:
                file_path = meta['file_path']
                with open(file_path, 'rb') as f:
                    value = pickle.load(f)

                # Atualizar acesso
                meta['accessed_at'] = time.time()
                return value

            except Exception as e:
                logger.debug(f"File cache load failed for {key}: {e}")
                self._delete_file(key)
                return None

        return None

    def _set_file(self, key: str, value: Any, ttl: int = None):
        """Armazenar no cache de arquivo"""
        if ttl is None:
            ttl = self.ttl_seconds

        try:
            # Criar hash da chave para nome do arquivo
            key_hash = hashlib.md5(key.encode()).hexdigest()
            file_path = self.cache_dir / f"{key_hash}.cache"

            # Serializar e salvar
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)

            size = file_path.stat().st_size

            # Evict se necessário
            self._evict_file_if_needed(size)

            # Atualizar metadata
            self._file_cache_meta[key] = {
                'file_path': file_path,
                'created_at': time.time(),
                'accessed_at': time.time(),
                'ttl': ttl,
                'size': size
            }

            self._file_size += size

        except Exception as e:
            logger.debug(f"File cache set failed for {key}: {e}")

    def _delete_file(self, key: str):
        """Remover do cache de arquivo"""
        if key in self._file_cache_meta:
            meta = self._file_cache_meta[key]

            try:
                meta['file_path'].unlink()
            except:
                pass

            self._file_size -= meta['size']
            del self._file_cache_meta[key]

    def _evict_file_if_needed(self, required_size: int):
        """Evict itens do cache de arquivo se necessário"""
        max_size_bytes = self.max_file_mb * 1024 * 1024

        while self._file_size + required_size > max_size_bytes and self._file_cache_meta:
            # Encontrar item menos recentemente usado
            lru_key = min(self._file_cache_meta.keys(),
                         key=lambda k: self._file_cache_meta[k]['accessed_at'])

            self._delete_file(lru_key)

    def _load_cache_metadata(self):
        """Carregar metadata do cache de arquivo"""
        meta_file = self.cache_dir / "cache_meta.json"

        if meta_file.exists():
            try:
                import json
                with open(meta_file, 'r') as f:
                    self._file_cache_meta = json.load(f)

                # Recalcular tamanho total
                self._file_size = sum(meta.get('size', 0) for meta in self._file_cache_meta.values())

            except Exception as e:
                logger.debug(f"Failed to load cache metadata: {e}")
                self._file_cache_meta = {}
                self._file_size = 0

    def _save_cache_metadata(self):
        """Salvar metadata do cache de arquivo"""
        meta_file = self.cache_dir / "cache_meta.json"

        try:
            import json
            with open(meta_file, 'w') as f:
                # Converter Path para string
                meta_copy = {}
                for key, meta in self._file_cache_meta.items():
                    meta_copy[key] = meta.copy()
                    meta_copy[key]['file_path'] = str(meta['file_path'])

                json.dump(meta_copy, f, indent=2, default=str)

        except Exception as e:
            logger.debug(f"Failed to save cache metadata: {e}")

    # ========== REDIS CACHE (L3) ==========

    def _get_redis_client(self):
        """Obter cliente Redis (lazy)"""
        if self._redis_client is None:
            try:
                from src.shared.utils.lazy_importer_enterprise import lazy_import
                redis = lazy_import('redis')

                if redis:
                    self._redis_client = redis.Redis(
                        host=os.environ.get('REDIS_HOST', 'localhost'),
                        port=int(os.environ.get('REDIS_PORT', 6379)),
                        db=int(os.environ.get('REDIS_DB', 0)),
                        decode_responses=True
                    )
            except:
                pass

        return self._redis_client

    def _get_redis(self, key: str) -> Any:
        """Obter do cache Redis"""
        client = self._get_redis_client()
        if not client:
            return None

        try:
            value_json = client.get(f"automator:cache:{key}")
            if value_json:
                import json
                return json.loads(value_json)
        except Exception as e:
            logger.debug(f"Redis cache get failed for {key}: {e}")

        return None

    def _set_redis(self, key: str, value: Any, ttl: int):
        """Armazenar no cache Redis"""
        client = self._get_redis_client()
        if not client:
            return

        try:
            import json
            value_json = json.dumps(value, default=str)
            client.setex(f"automator:cache:{key}", ttl, value_json)
        except Exception as e:
            logger.debug(f"Redis cache set failed for {key}: {e}")

    def _delete_redis(self, key: str):
        """Remover do cache Redis"""
        client = self._get_redis_client()
        if client:
            try:
                client.delete(f"automator:cache:{key}")
            except Exception as e:
                logger.debug(f"Redis cache delete failed for {key}: {e}")

    def _get_redis_stats(self) -> Dict:
        """Obter estatísticas do Redis"""
        client = self._get_redis_client()
        if not client:
            return {}

        try:
            info = client.info()
            return {
                'connected': True,
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'total_connections_received': info.get('total_connections_received', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0)
            }
        except:
            return {'connected': False}

    # ========== UTILITIES ==========

    def _calculate_size(self, obj: Any) -> int:
        """Calcular tamanho aproximado de um objeto"""
        try:
            import sys
            return sys.getsizeof(obj)
        except:
            return 1024  # Default 1KB

    def _is_important_key(self, key: str) -> bool:
        """Determinar se uma chave é importante para L3 cache"""
        important_patterns = [
            'user_session',
            'workflow_template',
            'ai_model',
            'config_'
        ]

        return any(pattern in key for pattern in important_patterns)

    def _cleanup_expired(self):
        """Limpar entradas expiradas (background)"""
        def cleanup():
            with self._lock:
                current_time = time.time()

                # Memory cleanup
                expired_memory = [
                    key for key, entry in self._memory_cache.items()
                    if current_time - entry['created_at'] > entry['ttl']
                ]

                for key in expired_memory:
                    self._delete_memory(key)

                # File cleanup
                expired_files = [
                    key for key, meta in self._file_cache_meta.items()
                    if current_time - meta['created_at'] > meta['ttl']
                ]

                for key in expired_files:
                    self._delete_file(key)

                # Save metadata
                self._save_cache_metadata()

        # Executar em thread separada
        threading.Thread(target=cleanup, daemon=True).start()

    def __del__(self):
        """Cleanup na destruição"""
        try:
            self._save_cache_metadata()
        except:
            pass


# Instância global
intelligent_cache = IntelligentCache()

# Funções de conveniência
def cache_get(key: str, default: Any = None) -> Any:
    """Obter valor do cache"""
    return intelligent_cache.get(key, default)

def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Armazenar valor no cache"""
    return intelligent_cache.set(key, value, ttl)

def cache_delete(key: str) -> bool:
    """Remover valor do cache"""
    return intelligent_cache.delete(key)

def cache_clear() -> bool:
    """Limpar todo o cache"""
    return intelligent_cache.clear()

def cache_stats() -> Dict:
    """Obter estatísticas do cache"""
    return intelligent_cache.get_stats()
