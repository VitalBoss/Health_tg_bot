from aiogram.types import Message
from aiogram import Router

router = Router()

@router.message()
async def handle_message(message: Message):
    await message.reply(f"Вы отправили: {message.text}")