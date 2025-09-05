import aioredis
import hashlib

from typing import Optional, Mapping, Union, Tuple
from abc import ABC, abstractmethod
from pydantic import RedisDsn


class CacheAbstract(ABC):

    @abstractmethod
    async def get(self, key) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, key, value, ttl) -> None:
        pass

    @abstractmethod
    async def delete(self, key) -> bool:
        pass


class RedisCache(CacheAbstract):
    def __init__(self):
        self.conn = None

    async def init(self, redis_url: RedisDsn):
        """
        This needs to be done here because it's an async operation. Create a Redis instance with
        ConnectionsPool
        :return:
        """
        self.conn = await aioredis.create_redis_pool(redis_url)

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from redis using a key
        :param key:
        :return: String value or None if not set
        """
        return await self.conn.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        Set value in redis
        :param key:
        :param value:
        :param ttl: The ttl is expressed in seconds
        :return:
        """
        return await self.conn.set(key, value, expire=ttl)

    async def delete(self, key) -> bool:
        """
        Delete value in redis
        :param key:
        :return: if key was found
        """
        n_deleted = await self.conn.delete(key)
        return n_deleted != 0

    async def get_from_hash(self, payload: Union[Mapping, str]) -> Tuple[str, str]:
        """
        This is used to calculate and get the value for a hash calculation given the contents of "payload" argument
        :param payload: The data to be hashed to create the key
        :return:
        """
        # Cache check
        hash_calc = hashlib.md5()
        hash_calc.update( str(payload).encode('utf-8') )

        cache_hash  = hash_calc.hexdigest()
        value       = await self.get( hash_calc.hexdigest() )

        return cache_hash, value

    async def publish(self, channel: str, payload: bytes) -> int:
        """
        Publish a message to a specified channel
        :param channel: The name of the channel receiving the message
        :param payload: The data to send to the channel
        :return: The number of clients that received the message
        """
        return await self.conn.publish(channel, payload)

    async def get_next(self, seq_name: str = '') -> int:
        """
        Get next value for a sequence name using the atomic operator incr
        :param seq_name: Name for the desired sequence
        :return: Next value for the sequence
        """
        return await self.conn.incr(f'sequence_{seq_name}')


# singleton
cache = RedisCache()
