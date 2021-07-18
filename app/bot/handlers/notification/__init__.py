import logging

from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import InvalidQueryID
from celery.worker.control import revoke

from app.main import dp, bot
from aiogram.types import CallbackQuery


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith("notification"), state="*"
)
async def confirm_reaction_on_notification(
    callback_query: CallbackQuery, state: FSMContext
):
    try:
        await bot.answer_callback_query(callback_query.id)
    except InvalidQueryID:
        logging.warning(f"This callback is too old: callback id {callback_query.id}")

    item_id = callback_query.data.split()[1]
    async with state.proxy() as data:
        following_items = data.get("following_items")
        task_id = data.get("notification_task_id")
    revoke(task_id, terminate=True)
    try:
        item_index = [elem["id"] for elem in following_items].index(item_id)
        item = following_items.pop(item_index)
        logging.info(f"item {item} on user {callback_query.from_user.id} was confirmed")
        await state.update_data(following_items=following_items)
        msg_text = "А я думал тебе нравятся мои анекдоты((((((((((((((9"
        await bot.send_message(callback_query.from_user.id, msg_text)
    except Exception:
        msg_text = "Хватит жмякать я уже успокоился...."
        await bot.send_message(callback_query.from_user.id, msg_text)
