from app.celery_app.custom_tools.schemas import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_confirm_notification_keyboard(item_index):
    confirm_notification_button = InlineKeyboardButton(
        text="Заткнись", callback_data=f"notification {item_index}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [confirm_notification_button],
        ]
    )
    return keyboard
