import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.bot.helpers.db import connect_to_mongodb, close_mongodb_connection
from app.config import settings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TG_TOKEN)
storage = RedisStorage2(host=settings.REDIS_HOST, db=10)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    await connect_to_mongodb()
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning("Shutting down..")

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await close_mongodb_connection()
    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning("Bye!")
