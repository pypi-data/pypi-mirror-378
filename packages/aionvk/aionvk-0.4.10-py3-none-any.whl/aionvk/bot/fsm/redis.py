import json
from typing import Any, Dict, Optional

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from .storage import BaseStorage


class RedisStorage(BaseStorage):
    def __init__(self, redis_client: "redis.Redis", key_prefix: str = "aionvk:fsm"):
        if redis is None:
            raise RuntimeError(
                "Для RedisStorage нужна библиотека redis: pip install redis"
            )
        self.redis = redis_client
        self.key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        return f"{self.key_prefix}:{key.split(':', 1)[1]}"

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        redis_key = self._make_key(key)
        data_raw = await self.redis.get(redis_key)
        if data_raw:
            return json.loads(data_raw)
        return None

    async def set_state(self, key: str, state_data: Dict[str, Any]) -> None:
        redis_key = self._make_key(key)
        await self.redis.set(redis_key, json.dumps(state_data))

    async def clear_state(self, key: str) -> None:
        redis_key = self._make_key(key)
        await self.redis.delete(redis_key)

    async def close(self):
        await self.redis.close()
