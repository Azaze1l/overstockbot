from app.bot.helpers.db import connect_to_mongodb, close_mongodb_connection
from app.main import dp, on_startup, on_shutdown
from aiogram import executor

if __name__ == "__main__":
    from app.bot import handlers

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
