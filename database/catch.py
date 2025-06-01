import redis.asyncio as aioredis
import os
from dotenv import load_dotenv
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


# 建立連線池
class RedisHandler():
    def __init__(self):
        try:
            self.redis_client = aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
        except Exception as e:
            print(e)
        self.counter_key = 'uuid_counter'

    def get_redis_client(self):
        return self.redis_client

    async def get_next_num(self):
        return await self.redis_client.incr(self.counter_key)


redis_handler = RedisHandler()
