from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup()
    following_items_button = KeyboardButton("Мои отслеживаемые вещи")
    add_new_item_button = KeyboardButton("Отслеживать новую вещь")
    keyboard.row(following_items_button)
    keyboard.row(add_new_item_button)
    return keyboard


def get_similar_overstock_item_names_keyboard(suggested_overstock_items):
    keyboard = InlineKeyboardMarkup()
    for item in suggested_overstock_items:
        keyboard.row(
            InlineKeyboardButton(item["name"], callback_data=f"suggested {item['id']}")
        )
    return keyboard


def get_page_controller_keyboard(
    current_page: int, count_of_pages: int, items: list, set_identifier: str
):
    item_buttons = []
    for i in range(len(items)):
        item_buttons.append(
            InlineKeyboardButton(
                str(i + 1), callback_data=f"{set_identifier} {items[i]['id']}"
            )
        )
    keyboard = InlineKeyboardMarkup()
    if current_page == 0 and count_of_pages != 1:
        next_page = InlineKeyboardButton(
            "Далее", callback_data=f"page {current_page + 1}"
        )
        keyboard.row(next_page)
        keyboard.row(*item_buttons)
        return keyboard
    elif current_page == 0 and count_of_pages == 1:
        keyboard.row(*item_buttons)
        return keyboard
    elif current_page == count_of_pages - 1:
        prev_page = InlineKeyboardButton(
            "Назад", callback_data=f"page {current_page - 1}"
        )
        keyboard.row(prev_page)
        keyboard.row(*item_buttons)
        return keyboard

    prev_page = InlineKeyboardButton("Назад", callback_data=f"page {current_page - 1}")
    next_page = InlineKeyboardButton("Далее", callback_data=f"page {current_page + 1}")
    keyboard.row(prev_page, next_page)
    keyboard.row(*item_buttons)
    return keyboard


def confirmation_keyboard(item_id):
    keyboard = InlineKeyboardMarkup()
    positive_confirmation_button = InlineKeyboardButton(
        "Да", callback_data=f"positive_confirmation {item_id}"
    )
    negative_confirmation_button = InlineKeyboardButton(
        "Нет", callback_data=f"negative_confirmation {item_id}"
    )
    keyboard.row(positive_confirmation_button)
    keyboard.row(negative_confirmation_button)
    return keyboard
