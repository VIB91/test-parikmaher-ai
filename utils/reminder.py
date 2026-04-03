# import asyncio
# from datetime import datetime, timedelta
# from database import get_upcoming_bookings, mark_as_reminded
#
# async def reminder(bot):
#     while True:
#         now = datetime.now()
#
#         # получаем записи на ближайшие 3 дня, у которых еще не было напоминания
#         bookings = await get_upcoming_bookings(days=3)
#
#         for b in bookings:
#             booking_datetime = datetime.strptime(f"{b['date']} {b['time']}", "%Y-%m-%d %H:%M")
#             diff = booking_datetime - now
#
#             # если до записи ~24 часа (±5 минут)
#             if 86000 <= diff.total_seconds() <= 87000:
#                 try:
#                     nice_date = booking_datetime.strftime("%d.%m.%Y %H:%M")
#                     await bot.send_message(
#                         b['user_id'],
#                         f"⏰ Напоминание!\n\n"
#                         f"Вы записаны завтра:\n"
#                         f"💇 {b['master']}\n"
#                         f"🧾 {b['service']}\n"
#                         f"📅 {nice_date}"
#                     )
#                     # помечаем как отправленное
#                     await mark_as_reminded(b['id'])
#                 except Exception as e:
#                     print("Ошибка отправки напоминания:", e)
#
#         await asyncio.sleep(60 * 10)  # проверяем каждые 10 минут