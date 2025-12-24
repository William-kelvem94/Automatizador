#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SERVIÇO DE CACHE
Implementação de cache distribuído com Redis fallback para memória
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ...domain.interfaces.automation_repository import ICacheService
from ...shared.utils.logger import get_logger


class RedisCacheService(ICacheService):
    """Implementação do cache usando Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.logger = get_logger(__name__)

        try:
            import redis.asyncio as redis
            self.redis = redis.from_url(redis_url)
            self.logger.info("Redis cache inicializado")
        except ImportError:
            self.logger.warning("Redis não disponível - usando cache em memória")
            self.redis = None
        except Exception as e:
            self.logger.error(f"Erro ao conectar com Redis: {e}")
            self.redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        try:
            if not self.redis:
                return None

            value = await self.redis.get(key)
            if value:
                # Desserializa JSON se necessário
                try:
                    return json.loads(value)
                except:
                    return value.decode('utf-8') if isinstance(value, bytes) else value

            return None

        except Exception as e:
            self.logger.error(f"Erro ao buscar cache {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define valor no cache"""
        try:
            if not self.redis:
                return False

            # Serializa valor para JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, (str, bytes, int, float)):
                value = str(value)

            success = await self.redis.set(key, value, ex=ttl)
            return bool(success)

        except Exception as e:
            self.logger.error(f"Erro ao definir cache {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            if not self.redis:
                return False

            result = await self.redis.delete(key)
            return result > 0

        except Exception as e:
            self.logger.error(f"Erro ao remover cache {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            if not self.redis:
                return False

            await self.redis.flushdb()
            self.logger.info("Cache Redis limpo")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        try:
            if not self.redis:
                return False

            return bool(await self.redis.exists(key))

        except Exception as e:
            self.logger.error(f"Erro ao verificar cache {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Retorna TTL da chave"""
        try:
            if not self.redis:
                return -1

            return await self.redis.ttl(key)

        except Exception as e:
            self.logger.error(f"Erro ao obter TTL {key}: {e}")
            return -1

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do cache Redis"""
        try:
            if not self.redis:
                return {
                    'service': 'RedisCache',
                    'status': 'unavailable',
                    'message': 'Redis client not initialized'
                }

            # Testa conexão
            await self.redis.ping()

            # Estatísticas básicas
            info = await self.redis.info()
            db_size = info.get('db0', {}).get('keys', 0)

            return {
                'service': 'RedisCache',
                'status': 'healthy',
                'keys_count': db_size,
                'memory_used': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'service': 'RedisCache',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class InMemoryCacheService(ICacheService):
    """Implementação do cache em memória (fallback)"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(__name__)
        self.logger.info("Cache em memória inicializado")

    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache em memória"""
        try:
            if key in self._cache:
                entry = self._cache[key]

                # Verifica expiração
                if entry['expires_at'] > time.time():
                    return entry['value']
                else:
                    # Remove entrada expirada
                    del self._cache[key]

            return None

        except Exception as e:
            self.logger.error(f"Erro ao buscar cache {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define valor no cache em memória"""
        try:
            expires_at = time.time() + ttl

            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }

            return True

        except Exception as e:
            self.logger.error(f"Erro ao definir cache {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove valor do cache em memória"""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

        except Exception as e:
            self.logger.error(f"Erro ao remover cache {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Limpa todo o cache em memória"""
        try:
            self._cache.clear()
            self.logger.info("Cache em memória limpo")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache"""
        try:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires_at'] > time.time():
                    return True
                else:
                    # Remove entrada expirada
                    del self._cache[key]
            return False

        except Exception as e:
            self.logger.error(f"Erro ao verificar cache {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Retorna TTL da chave em segundos"""
        try:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires_at'] > time.time():
                    return int(entry['expires_at'] - time.time())
                else:
                    # Remove entrada expirada
                    del self._cache[key]
            return -1

        except Exception as e:
            self.logger.error(f"Erro ao obter TTL {key}: {e}")
            return -1

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache em memória"""
        try:
            now = time.time()
            total_keys = len(self._cache)
            expired_keys = sum(1 for entry in self._cache.values() if entry['expires_at'] <= now)

            # Remove chaves expiradas
            self._cache = {k: v for k, v in self._cache.items() if v['expires_at'] > now}

            return {
                'total_keys': total_keys,
                'active_keys': len(self._cache),
                'expired_keys': expired_keys,
                'memory_usage': 'unknown'  # Não podemos medir facilmente
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do cache em memória"""
        try:
            stats = self.get_stats()

            return {
                'service': 'InMemoryCache',
                'status': 'healthy',
                'active_keys': stats.get('active_keys', 0),
                'total_keys': stats.get('total_keys', 0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'service': 'InMemoryCache',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class HybridCacheService(ICacheService):
    """Cache híbrido: Redis + Memória como fallback"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_cache = RedisCacheService(redis_url)
        self.memory_cache = InMemoryCacheService()
        self.logger = get_logger(__name__)

        # Determina qual usar como primário
        self.primary_cache = self.redis_cache if self.redis_cache.redis else self.memory_cache
        self.fallback_cache = self.memory_cache if self.redis_cache.redis else self.redis_cache

        cache_type = "Redis" if self.redis_cache.redis else "Memória"
        self.logger.info(f"Cache híbrido inicializado - Primário: {cache_type}")

    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache (primário primeiro, fallback depois)"""
        # Tenta cache primário
        value = await self.primary_cache.get(key)
        if value is not None:
            return value

        # Fallback para cache secundário
        value = await self.fallback_cache.get(key)
        if value is not None:
            # Replica para cache primário se possível
            await self.primary_cache.set(key, value, ttl=3600)
            return value

        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define valor em ambos os caches"""
        primary_success = await self.primary_cache.set(key, value, ttl)
        fallback_success = await self.fallback_cache.set(key, value, ttl)

        success = primary_success or fallback_success

        if success:
            self.logger.debug(f"Cache definido: {key}")
        else:
            self.logger.warning(f"Falha ao definir cache: {key}")

        return success

    async def delete(self, key: str) -> bool:
        """Remove valor de ambos os caches"""
        primary_success = await self.primary_cache.delete(key)
        fallback_success = await self.fallback_cache.delete(key)

        return primary_success or fallback_success

    async def clear(self) -> bool:
        """Limpa ambos os caches"""
        primary_success = await self.primary_cache.clear()
        fallback_success = await self.fallback_cache.clear()

        return primary_success and fallback_success

    async def exists(self, key: str) -> bool:
        """Verifica se chave existe em algum cache"""
        return await self.primary_cache.exists(key) or await self.fallback_cache.exists(key)

    async def get_ttl(self, key: str) -> int:
        """Retorna TTL da chave (do cache primário)"""
        ttl = await self.primary_cache.get_ttl(key)
        if ttl == -1:
            ttl = await self.fallback_cache.get_ttl(key)
        return ttl

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde de ambos os caches"""
        primary_health = await self.primary_cache.health_check()
        fallback_health = await self.fallback_cache.health_check()

        overall_status = "healthy"
        if primary_health['status'] == 'unhealthy' and fallback_health['status'] == 'unhealthy':
            overall_status = "unhealthy"
        elif primary_health['status'] == 'unhealthy':
            overall_status = "degraded"

        return {
            'service': 'HybridCache',
            'status': overall_status,
            'primary_cache': primary_health,
            'fallback_cache': fallback_health,
            'timestamp': datetime.now().isoformat()
        }


# Factory function para criar o cache apropriado
def create_cache_service(redis_url: Optional[str] = None) -> ICacheService:
    """Factory para criar serviço de cache apropriado"""
    if redis_url:
        return HybridCacheService(redis_url)
    else:
        # Tenta Redis local, fallback para memória
        try:
            return HybridCacheService()
        except:
            return InMemoryCacheService()
