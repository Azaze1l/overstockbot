import math

from app.bot.helpers.keyboards import get_page_controller_keyboard
from app.config import settings
from app.main import bot


async def _get_page(items: list, items_per_page: int, current_page: int):
    pages = [
        items[x : x + items_per_page] for x in range(0, len(items), items_per_page)
    ]
    try:
        page = pages[current_page]
    except IndexError:
        current_page = 0
        page = pages[current_page]
    return page


async def _send_page(msg_id_in_page, chat_id, page_message, reply_markup):
    if msg_id_in_page is None:
        sent_page_msg = await bot.send_message(
            chat_id, text=page_message, reply_markup=reply_markup, parse_mode="HTML"
        )
        return sent_page_msg.message_id
    else:
        await bot.edit_message_text(
            page_message, chat_id, msg_id_in_page, parse_mode="HTML"
        )
        await bot.edit_message_reply_markup(
            chat_id,
            msg_id_in_page,
            reply_markup=reply_markup,
        )


async def send_following_items_message(
    following_items: list, chat_id: int, current_page: int, msg_id_in_page: dict = None
):
    items_per_page = settings.ITEMS_ON_PAGE_WITH_FOLLOWING_ITEMS
    page = await _get_page(following_items, items_per_page, current_page)
    page_message = f"<b>Страница {current_page + 1}/{math.ceil(len(following_items) / items_per_page)}</b>\n\n"
    items_on_page = []
    for i in range(len(page)):
        item = page[i]

        msg_text = f"<b>{i + 1}</b>. {item['name']}\n\n"
        page_message += msg_text
        items_on_page.append(item)

    reply_markup = get_page_controller_keyboard(
        current_page,
        math.ceil(len(following_items) / items_per_page),
        items_on_page,
        set_identifier="del_following_item",
    )
    message_id = await _send_page(msg_id_in_page, chat_id, page_message, reply_markup)
    return message_id
