from aiogram import Router, F
from aiogram.types import Message
from config import ADMIN_ID
from database import get_all_bookings, get_bookings_by_date
from datetime import datetime, timedelta
from keyboards.admin_kb import get_admin_filter_kb

router = Router()


@router.message(F.text == "CRM")
async def crm(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📊 Выберите фильтр:",
        reply_markup=get_admin_filter_kb()
    )

    bookings = await get_all_bookings()

    if not bookings:
        await message.answer("Нет записей")
        return

    text = "📊 *Все записи:*\n\n"

    for b in bookings:
        nice_date = datetime.strptime(b[3], "%Y-%m-%d").strftime("%d.%m.%Y")
        text += (
            f"👤 ID: {b[0]}\n"
            f"💇 {b[1]}\n"
            f"🧾 {b[2]}\n"
            f"📅 {nice_date} {b[4]}\n"
            f"------------------\n"
        )

    await message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data.startswith("filter_"))
async def handle_filter(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    filter_type = callback.data

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    if filter_type == "filter_today":
        bookings = await get_bookings_by_date(today)
        title = "📅 Сегодня"

    elif filter_type == "filter_tomorrow":
        bookings = await get_bookings_by_date(tomorrow)
        title = "📅 Завтра"

    else:
        bookings = await get_all_bookings()
        title = "📊 Все записи"

    if not bookings:
        await callback.message.answer(f"{title}\n\nНет записей")
        return

    text = f"{title}\n\n"

    for b in bookings:
        nice_date = datetime.strptime(b[3], "%Y-%m-%d").strftime("%d.%m.%Y")

        text += (
            f"👤 {b[0]}\n"
            f"💇 {b[1]}\n"
            f"🧾 {b[2]}\n"
            f"📅 {nice_date} {b[4]}\n"
            f"------------------\n"
        )

    await callback.message.answer(text)