from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


def get_calendar():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    today = datetime.now()

    for i in range(7):
        day = today + timedelta(days=i)
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=day.strftime("%d.%m"),
                callback_data=f"date_{day.strftime('%d.%m')}"
            )
        ])
    return kb