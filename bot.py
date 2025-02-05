from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.handlers_start import router
from handlers.logging_handlers import router2
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)
dp.include_router(router2)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())