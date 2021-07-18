import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram.utils.exceptions import InvalidQueryID

from app.bot.handlers.add_new_item.services import (
    get_overstock_items_list_from_mongodb,
    get_similar_overstock_item_names,
)
from app.bot.helpers.keyboards import get_similar_overstock_item_names_keyboard
from app.main import bot, dp
from app.bot.handlers.add_new_item.states import AddNewItemStates


@dp.message_handler(lambda message: message.text == "Отслеживать новую вещь", state="*")
async def add_new_item_handler(message: Message, state: FSMContext):

    msg_text = (
        "Д'оу! Отправь название вещи на ангельском языке, "
        "и я постараюсь найти подходящие из списка"
    )
    await bot.send_message(message.from_user.id, msg_text)
    await AddNewItemStates.waiting_for_item_name.set()


@dp.message_handler(
    state=AddNewItemStates.waiting_for_item_name,
    content_types=ContentType.ANY,
)
async def subscription_name_handler(message: Message, state: FSMContext):
    if message.content_type is not ContentType.TEXT:
        msg_text = "Напиши название на АНГЛИЙСКОМ ЯЗЫКЕ"
        await bot.send_message(message.from_user.id, msg_text)
        return

    item_name = message.text

    overstock_items = await get_overstock_items_list_from_mongodb()
    suggested_overstock_items = await get_similar_overstock_item_names(
        item_name, overstock_items
    )
    if len(suggested_overstock_items) != 0:
        if len(suggested_overstock_items) == 1:
            msg_text = "Я нашел эту вещь по твоему запросу"
        else:
            msg_text = "Выбери одну из приведенных вещей"
        await state.update_data(suggested_overstock_items=suggested_overstock_items)
        kbd = get_similar_overstock_item_names_keyboard(suggested_overstock_items)
        await bot.send_message(message.from_user.id, msg_text, reply_markup=kbd)
        async with state.proxy() as data:
            data.state = None
        return
    if item_name in [
        elem.get("market_hash_name") for elem in suggested_overstock_items
    ]:
        item = [
            elem
            for elem in suggested_overstock_items
            if elem["market_hash_name"] == item_name
        ][0]
        async with state.proxy() as data:
            following_items = data.get("following_items")
        if following_items is None:
            await state.update_data(following_items=[item])
        else:
            if item not in following_items:
                following_items.append(item)
                await state.update_data(following_items=following_items)
                msg_text = f"Вещь {item['name']}, успешно зарегистирирована и будет мною отслеживаться"
                await bot.send_message(message.from_user.id, msg_text)
            else:
                msg_text = (
                    f"Вещь {item['name']}, уже имеется в твоем списке отслеживаемых"
                )
                msg = await bot.send_message(message.from_user.id, msg_text)
                await asyncio.sleep(2)
                await bot.delete_message(message.chat.id, msg.message_id)
    else:
        msg_text = "К сожалению, я ничего не нашел по твоему запросу"
        await bot.send_message(message.from_user.id, msg_text)
    async with state.proxy() as data:
        data.state = None


@dp.callback_query_handler(
    lambda callback_query: callback_query.data.startswith("suggested")
)
async def register_item_handler(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
    except InvalidQueryID:
        logging.warning(f"This callback is too old: callback id {callback_query.id}")

    item_id = callback_query.data.split()[1]
    async with state.proxy() as data:
        suggested_overstock_items = data.get("suggested_overstock_items")
        following_items = data.get("following_items")
    item = [elem for elem in suggested_overstock_items if elem["id"] == item_id][0]
    if following_items is None:
        await state.update_data(following_items=[item])
    else:
        if item not in following_items:
            following_items.append(item)
            await state.update_data(following_items=following_items)
            msg_text = f"Вещь {item['name']}, успешно зарегистирирована и будет мною отслеживаться"
            await bot.send_message(callback_query.from_user.id, msg_text)
        else:
            msg_text = f"Вещь {item['name']}, уже имеется в твоем списке отслеживаемых"
            msg = await bot.send_message(callback_query.from_user.id, msg_text)
            await asyncio.sleep(2)
            await bot.delete_message(callback_query.message.chat.id, msg.message_id)
