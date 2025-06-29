from aiogram.dispatcher.middlewares.base import BaseMiddleware

class RedisMiddleware(BaseMiddleware):
    def __init__(self, redis):
        super().__init__()
        self.redis = redis

    async def __call__(self, handler, event, data):
        data["redis"] = self.redis
        return await handler(event, data)