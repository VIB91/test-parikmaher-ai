from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_filter_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="filter_today"),
            InlineKeyboardButton(text="📅 Завтра", callback_data="filter_tomorrow")
        ],
        [
            InlineKeyboardButton(text="📊 Все записи", callback_data="filter_all")
        ]
    ])