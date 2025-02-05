from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from state import Person
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils import calculate_water_norm, calculate_calories_norm

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()
USERS = {}
sex = ['Male', 'Female']


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)



@router.message(Command("start"))
async def cmd_start(message: Message):
    global user_username
    user_username = message.from_user.username
    await message.answer(f"Добро пожаловать, @{user_username}! Я ваш бот, для помощи отправь /help в этот чат.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""Я могу ответить на команды:
                        /set_profile - настройка профиля
                        /get_norm - получение дневной нормы воды и калорий
                        /log_water <количество> - добавить запись о выпитой воде
                        /log_food <название продукта> - добавить запись о полученных калориях
                        /log_workout <тип тренировки> <время (мин)> - добавить запись о физической активности
                        /check_progress - посмотреть дневной прогресс
                        /plot_progress - построить график прогрессов по предыдущим дням
                        /recommendations - получить рекомендации по тренировкам или питанию """)

@router.message(Command("get_norm"))
async def cmd_start(message: Message):
    global WATER_NORM, CALLORIES_NORM, user_username
    if user_username in USERS:
        WATER_NORM, CALLORIES_NORM = await calculate_water_norm(USERS[user_username]), calculate_calories_norm(USERS[user_username])
        await message.answer(f"Ваша дневная норма воды = {WATER_NORM}")
        await message.answer(f"Ваша дневная норма калорий = {CALLORIES_NORM}")
    else:
        await message.answer("Прежде чем получить индивидуальную норму воды и калорий введите данные о о себе с помощью команды /set_profile")


@router.message(Command("set_profile"))
async def cmd_set(message: Message, state: FSMContext):
    user_username = message.from_user.username
    if not user_username in USERS:
        USERS[user_username] = dict()
    await message.answer("Начнем настройку вашего профиля!")  
    await message.answer(
        text="Введите ваш пол:",
        reply_markup=make_row_keyboard(sex)
    )
    await state.set_state(Person.sex)

@router.message(Person.sex, F.text.in_(sex))
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите ваш возраст:",
    )
    await state.set_state(Person.age)
    USERS[user_username]['sex'] = message.text
    

@router.message(Person.age)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите ваш рост (в сантиметрах):",
    )
    await state.set_state(Person.height)
    USERS[user_username]['age']= message.text

@router.message(Person.height)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите ваш вес (в килограммах):",
    )
    await state.set_state(Person.weight)
    USERS[user_username]['height'] = message.text

@router.message(Person.weight)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите ваш город:",
    )
    await state.set_state(Person.city)
    USERS[user_username]['weight'] = message.text

@router.message(Person.city)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите вашу среднюю активность в день (в минутах):",
    )
    await state.set_state(Person.activity)
    USERS[user_username]['city'] = message.text

@router.message(Person.activity)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer(
        text="Введите среднее кол-во потребляемых каллорий в день:",
    )
    await state.set_state(Person.calorie_goal)
    USERS[user_username]['activity'] = message.text

@router.message(Person.calorie_goal)
async def handle_message(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    USERS[user_username]['calorie_goal'] = message.text
    await message.answer("Ваши данные успешно записаны! Для получения индивидульной дневной нормы воды и каллорий отправьте /get_norm")


