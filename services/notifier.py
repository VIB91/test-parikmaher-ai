import asyncio
from datetime import datetime, timedelta
from database import get_upcoming_bookings, mark_as_reminded


async def notifier(bot):
    while True:
        now = datetime.now()

        bookings = await get_upcoming_bookings(days=2)

        for b in bookings:
            booking_datetime = datetime.strptime(
                f"{b['date']} {b['time']}",
                "%Y-%m-%d %H:%M"
            )

            diff = booking_datetime - now

            # ✅ строго около 2 часов (±5 минут)
            if 6900 <= diff.total_seconds() <= 7500:
                try:
                    nice_date = booking_datetime.strftime("%d.%m.%Y %H:%M")

                    await bot.send_message(
                        b["user_id"],
                        f"⏰ Напоминание!\n\n"
                        f"Вы записаны:\n"
                        f"🧾 {b['service']}\n"
                        f"📅 {nice_date}"
                    )

                    # ✅ помечаем, чтобы больше НЕ отправлять
                    await mark_as_reminded(b["id"])

                except Exception as e:
                    print("Ошибка уведомления:", e)

        await asyncio.sleep(60 * 5)  # каждые 5 минут