from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.client_kb import main_kb, get_masters_kb, get_slots_kb
from keyboards.calendar_kb import get_calendar
from services.booking_service import get_free_slots
from database import add_booking
from config import ADMIN_ID
from database import get_user_bookings
from database import delete_booking
from keyboards.client_kb import get_delete_kb
from database import get_user_bookings, delete_booking_by_id
from datetime import datetime
router = Router()


class Booking(StatesGroup):
    master = State()
    service = State()
    date = State()


@router.message(F.text == "старт")
async def start(message: Message):
    await message.answer(
        "💈 Добро пожаловать в барбершоп!\n\n"
        "Выберите действие 👇",
        reply_markup=main_kb
    )



@router.message(F.text == "Записаться")
async def choose_master(message: Message, state: FSMContext):
    await message.answer("Выберите мастера:", reply_markup=get_masters_kb())


@router.callback_query(F.data.startswith("master_"))
async def select_master(callback: CallbackQuery, state: FSMContext):
    master = callback.data.split("_")[1]
    await state.update_data(master=master)

    await callback.message.answer("Введите услугу:")
    await state.set_state(Booking.service)


@router.message(Booking.service)
async def get_service(message: Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("Выберите дату:", reply_markup=get_calendar())
    await state.set_state(Booking.date)


@router.callback_query(F.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    raw_date = callback.data.split("_")[1]  # 25.03

    year = datetime.now().year  # текущий год

    date_obj = datetime.strptime(f"{raw_date}.{year}", "%d.%m.%Y")
    date = date_obj.strftime("%Y-%m-%d")  # сохраняем правильно

    data = await state.get_data()

    slots = await get_free_slots(date, data["master"])

    await callback.message.answer(
        "Выберите время:",
        reply_markup=get_slots_kb(slots)
    )

    await state.update_data(date=date)


@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_")[1]
    data = await state.get_data()

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
    nice_date = datetime.strptime(data["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
    await callback.bot.send_message(
        ADMIN_ID,
        f"📌 Новая запись:\n"
        f"👤 {callback.from_user.id}\n"
        f"💇 {data['master']}\n"
        f"🧾 {data['service']}\n"
        f"📅 {nice_date} {time}"
    )

    await state.clear()

@router.message(F.text == "Отменить запись")
async def show_bookings_to_delete(message: Message):
    bookings = await get_user_bookings(message.from_user.id)

    if not bookings:
        await message.answer("Нет записей")
        return

    await message.answer(
        "Выберите запись для удаления:",
        reply_markup=get_delete_kb(bookings)
    )

@router.callback_query(F.data.startswith("delete_"))
async def delete_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])

    await delete_booking_by_id(booking_id)

    await callback.message.answer("❌ Запись удалена")

# @router.message(F.text == "Отменить все записи")
# async def cancel_booking(message: Message):
#     await delete_booking(message.from_user.id)
#     await message.answer("❌ Все записи отменены")

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



