import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers.client import router as client_router
from handlers.admin import router as admin_router
# from utils.reminder import reminder
from services.notifier import notifier

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(client_router)
    dp.include_router(admin_router)

    await init_db()

    asyncio.create_task(notifier(bot))

    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())