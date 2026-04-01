from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import WebAppInfo
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Записаться")],
        [KeyboardButton(text="Мои записи")],
        [KeyboardButton(text="Отменить запись")]
    ],
    resize_keyboard=True
)


def get_masters_kb():
    masters = ["Иван", "Алексей"]

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for m in masters:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=m, callback_data=f"master_{m}")
        ])
    return kb


def get_slots_kb(slots):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for t in slots:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=t, callback_data=f"time_{t}")
        ])
    return kb

def get_delete_kb(bookings):
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for b in bookings:
        text = f"{b[3]} {b[4]} | {b[1]}"
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"delete_{b[0]}"
            )
        ])

    return kb

