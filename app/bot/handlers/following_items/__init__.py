import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import InvalidQueryID

from app.bot.handlers.following_items.services import send_following_items_message
from app.bot.helpers.keyboards import confirmation_keyboard
from app.main import bot, dp
from aiogram.types import Message, CallbackQuery


@dp.message_handler(lambda message: message.text == "Мои отслеживаемые вещи", state="*")
async def following_items_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        following_items = data.get("following_items")

    if following_items is None or following_items == []:
        msg_text = "Иди-ка подпишись на какую-нибудь вещь, мне нечего тебе показать"
        await bot.send_message(message.from_user.id, msg_text)
        return

    msg_id_in_page = await send_following_items_message(
        following_items,
        message.chat.id,
        0,
    )
    await state.update_data(
        msg_id_in_page=msg_id_in_page,
    )


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith("page"),
)
async def page_with_addresses_handler(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
    except InvalidQueryID:
        logging.warning(f"This callback is too old: callback id {callback_query.id}")

    page = int(callback_query.data.split()[1])
    async with state.proxy() as data:
        following_items = data.get("following_items")
        msg_id_in_page = data.get("msg_id_in_page")
    await send_following_items_message(
        following_items,
        callback_query.message.chat.id,
        page,
        msg_id_in_page=msg_id_in_page,
    )
    await state.update_data(page=page)


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith("del_following_item")
)
async def delete_following_item_handler(
    callback_query: CallbackQuery, state: FSMContext
):
    try:
        await bot.answer_callback_query(callback_query.id)
    except InvalidQueryID:
        logging.warning(f"This callback is too old: callback id {callback_query.id}")

    async with state.proxy() as data:
        following_items = data.get("following_items")
    item_id = callback_query.data.split()[1]
    item = [elem for elem in following_items if elem["id"] == item_id][0]
    message_text = f"Ты точно хочешь удалить <b>{item['name']}</b>"
    confirmation_msg = await bot.send_message(
        callback_query.from_user.id,
        message_text,
        reply_markup=confirmation_keyboard(item_id),
        parse_mode="HTML",
    )
    await state.update_data(confirmation_msg_id=confirmation_msg.message_id)


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith("positive_confirmation")
    or callback_query.data.startswith("negative_confirmation")
)
async def del_confirmation_handler(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
    except InvalidQueryID:
        logging.warning(f"This callback is too old: callback id {callback_query.id}")

    async with state.proxy() as data:
        following_items = data.get("following_items")
        confirmation_msg_id = data.get("confirmation_msg_id")
        msg_id_in_page = data.get("msg_id_in_page")
        page = data.get("page")
        if page is None:
            page = 0

    confirmation, item_id = callback_query.data.split()
    if confirmation == "positive_confirmation":
        item_index = [elem["id"] for elem in following_items].index(item_id)
        item = following_items.pop(int(item_index))
        await state.update_data(following_items=following_items)
        msg_text = f"<b>{item['name']}</b> успешно убран из подписок"
        await bot.delete_message(callback_query.message.chat.id, confirmation_msg_id)
        msg = await bot.send_message(
            callback_query.from_user.id, msg_text, parse_mode="HTML"
        )
        await asyncio.sleep(2.0)
        await bot.delete_message(callback_query.message.chat.id, msg.message_id)
        await send_following_items_message(
            following_items,
            callback_query.message.chat.id,
            page,
            msg_id_in_page=msg_id_in_page,
        )
    else:
        await bot.delete_message(callback_query.message.chat.id, confirmation_msg_id)
