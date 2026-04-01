import asyncio
from datetime import datetime
from database import get_all_bookings


async def reminder(bot):
    while True:
        now = datetime.now().strftime("%H:%M")
        bookings = await get_all_bookings()

        for b in bookings:
            if b[4] == now:
                await bot.send_message(b[0], "🔔 Напоминание о записи!")

        await asyncio.sleep(60)