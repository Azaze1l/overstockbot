from aiogram.dispatcher import FSMContext

from app.bot.helpers.db import get_db
from app.bot.helpers.keyboards import get_main_keyboard
from app.main import dp, bot
from aiogram.types import Message
from app.bot.helpers.db.users import Users


@dp.message_handler(commands=["start"], state="*")
async def start_scenario_handler(message: Message, state: FSMContext):
    msg_text = (
        "Данил, ты? Помнишь меня? Я твой одноклассник. "
        "Я узнал тебя по твоим шизоидным словам....\nКороче,"
        " вот тебе главное меню, делай с ним ч хочешь"
    )
    db = await get_db()
    await Users.get_or_create_new_user(db=db, chat_id=message.from_user.id)
    await bot.send_message(
        message.from_user.id, msg_text, reply_markup=get_main_keyboard()
    )
