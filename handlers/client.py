from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.client_kb import main_kb, get_masters_kb, get_slots_kb, get_services_kb, get_delete_kb
from services.booking_service import get_free_slots
from database import add_booking, get_user_bookings, delete_booking_by_id
from config import ADMIN_ID
from datetime import datetime, timedelta
from services.ai_booking import parse_booking, parse_simple_booking
from aiogram.filters import Command

router = Router()


class Booking(StatesGroup):
    master = State()
    service = State()
    date = State()


@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer("✅ Бот работает")


@router.message(F.text == "старт")
async def start(message: Message):
    await message.answer(
        "💈 Добро пожаловать в Парикмахерскую!\n\nВыберите действие 👇",
        reply_markup=main_kb
    )


@router.message(F.text == "Записаться")
async def choose_master(message: Message, state: FSMContext):
    await message.answer("Выберите мастера:", reply_markup=get_masters_kb())
    await state.clear()  # очищаем старые данные


@router.callback_query(F.data.startswith("master_"))
async def select_master(callback: CallbackQuery, state: FSMContext):
    master = callback.data.split("_")[1]
    await state.update_data(master=master)

    await callback.message.answer("Выберите услугу:", reply_markup=get_services_kb())
    await state.set_state(Booking.service)


@router.callback_query(F.data.startswith("service_"))
async def select_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(service=service)

    # Кнопки для даты на 7 дней вперед
    keyboard = []
    for i in range(7):
        day = datetime.now() + timedelta(days=i)
        day_str = day.strftime("%d.%m.%Y")
        keyboard.append([InlineKeyboardButton(text=day_str, callback_data=f"date_{day_str}")])

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer("Выберите дату:", reply_markup=kb)
    await state.set_state(Booking.date)


@router.callback_query(F.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    raw_date = callback.data.split("_")[1]  # '25.03.2026'
    date_obj = datetime.strptime(raw_date, "%d.%m.%Y")
    date = date_obj.strftime("%Y-%m-%d")

    data = await state.get_data()
    master = data.get("master")
    if not master:
        await callback.message.answer("❌ Ошибка: мастер не выбран")
        return

    slots = await get_free_slots(date, master)
    await callback.message.answer("Выберите время:", reply_markup=get_slots_kb(slots))
    await state.update_data(date=date)


@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_")[1]
    data = await state.get_data()
    if "edit_id" in data:
        booking_id = data["edit_id"]

        import aiosqlite
        async with aiosqlite.connect("barber.db") as db:
            await db.execute(
                "UPDATE bookings SET time = ? WHERE id = ?",
                (time, booking_id)
            )
            await db.commit()

        await callback.message.answer("✅ Время обновлено")
        await state.clear()
        return

    await add_booking(
        callback.from_user.id,
        data["master"],
        data["service"],
        data["date"],
        time
    )

    # ✅ сообщение клиенту
    nice_date = datetime.strptime(data["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
    await callback.message.answer(
        "✅ *Вы успешно записаны!*\n\n"
        f"💇 Мастер: {data['master']}\n"
        f"🧾 Услуга: {data['service']}\n"
        f"📅 {nice_date} в {time}",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

    # ✅ сообщение админу
    await callback.bot.send_message(
        ADMIN_ID,
        f"📌 Новая запись:\n"
        f"👤 {callback.from_user.id}\n"
        f"💇 {data['master']}\n"
        f"🧾 {data['service']}\n"
        f"📅 {nice_date} {time}"
    )

    await state.clear()


# ------------------- Удаление записей -------------------
@router.message(F.text == "Отменить запись")
async def show_bookings_to_delete(message: Message):
    bookings = await get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("Нет записей")
        return

    buttons = []
    for b in bookings:
        booking_id = b[0]
        # Преобразуем дату в ДД.ММ.ГГГГ
        nice_date = datetime.strptime(b[3], "%Y-%m-%d").strftime("%d.%m.%Y")
        # Текст кнопки: дата + время
        btn_text = f"{nice_date} {b[4]}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"delete_{booking_id}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите запись для удаления:", reply_markup=kb)




@router.callback_query(F.data.startswith("delete_"))
async def delete_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    bookings = await get_user_bookings(callback.from_user.id)

    nice_date = None
    for b in bookings:
        if b[0] == booking_id:
            nice_date = datetime.strptime(b[3], "%Y-%m-%d").strftime("%d.%m.%Y")
            break

    if nice_date:
        await delete_booking_by_id(booking_id)
        await callback.message.answer(f"❌ Запись на {nice_date} удалена")
    else:
        await callback.message.answer("❌ Ошибка удаления")


@router.message(F.text == "Мои записи")
async def my_bookings(message: Message):
    bookings = await get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет записей 😢")
        return

    text = "📋 *Ваши записи:*\n\n"
    for b in bookings:
        nice_date = datetime.strptime(b[3], "%Y-%m-%d").strftime("%d.%m.%Y")
        text += (
            f"🆔 {b[0]}\n"
            f"💇 {b[1]}\n"
            f"🧾 {b[2]}\n"
            f"📅 {nice_date} {b[4]}\n\n"
        )

    await message.answer(text, parse_mode="Markdown")

MASTER_ALIASES = {
    "юлия": "Юлия",
    "юле": "Юлия",
    "юлю": "Юлия",
    "юли": "Юлия",

    "мария": "Мария",
    "марие": "Мария",
    "маше": "Мария",
    "машу": "Мария",
    "маша": "Мария",
}
MASTERS = ["Юлия", "Мария"]
@router.message(F.text & ~F.text.in_([
    "CRM",
    "Записаться",
    "Мои записи",
    "Отменить запись",
    "старт"
]))
async def ai_booking_handler(message: Message):

    text = message.text

    data = parse_simple_booking(text)
    # 🔥 если AI не нашёл мастера — ищем сами в тексте
    if not data.get("master"):
        text_lower = text.lower()

        for key, value in MASTER_ALIASES.items():
            if key in text_lower:
                data["master"] = value
                break

    # если нет даты — не обрабатываем
    if not data["date"]:
        return

    from database import add_booking, get_booked_times
    from services.booking_service import get_free_slots

    master = data.get("master")
    service = data["service"] or "Стрижка"  # по умолчанию
    date = data["date"]
    time = data["time"]


    # если мастер не указан — берём любого
    if master:
        master_lower = master.lower().strip()

        found = None

        for key, value in MASTER_ALIASES.items():
            if key in master_lower:
                found = value
                break

        if found:
            master = found
        else:
            await message.answer("Такого мастера нет 😢")
            return

    if not master:
        for m in MASTERS:
            slots = await get_free_slots(date, m)
            if slots:
                master = m
                break


        if not master:
            await message.answer("Нет свободных мастеров 😢")
            return

    # если время не указано — предлагаем слоты
    if not time:
        slots = await get_free_slots(date, master)

        if not slots:
            await message.answer("Нет свободного времени 😢")
            return

        await message.answer(
            f"Свободное время у {master}:",
            reply_markup=get_slots_kb(slots)
        )
        return

    # проверка занятости
    booked_times = await get_booked_times(date, master)

    if time in booked_times:
        await message.answer("Это время занято 😢")
        return

    # запись
    await add_booking(
        message.from_user.id,
        master,
        service,
        date,
        time
    )

    nice_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")

    await message.answer(
        f"✅ Записал:\n"
        f"💇 {master}\n"
        f"🧾 {service}\n"
        f"📅 {nice_date} {time}"
    )

