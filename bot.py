from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Я могу ответить на команды /start и /help.")

# Основная функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())