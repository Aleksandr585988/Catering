import json

import redis
from django.conf import settings


class CacheService:
    def __init__(self, connection_string: str | None = None):
        self.connection: redis.Redis = redis.Redis.from_url(
            connection_string or settings.CACHE_CONNECTION_STRING
        )

    @staticmethod
    def _build_key(namespace: str, key: str):
        return f"{namespace}:{key}"

    def set(self, namespace: str, key: str, instance: dict, ttl: int | None = 259200):
        payload: str = json.dumps(instance)
        self.connection.set(name=self._build_key(namespace, key), value=payload, ex=ttl)

    def get(self, namespace: str, key: str) -> dict:
        result: str = self.connection.get(self._build_key(namespace, key))  # type: ignore
        
        if result is None:
            return None
        
        return json.loads(result)
