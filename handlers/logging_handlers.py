from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import  handlers.handlers_start as hs # WATER_NORM, CALLORIES_NORM, user_username
from datetime import datetime
from utils import translate, get_product_calories, calculate_calories_and_water
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from aiogram.types import FSInputFile
from aiogram.types import BufferedInputFile
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

router2 = Router()
WATER = {}
CALLORIES = {}
TRAIN = {}
CALLORIE = None



@router2.message(Command('log_water'))
async def log_water(message: Message):
    water = message.text.split()
    if len(water) < 2:
        await message.reply("Пожалуйста, укажите количество воды в миллилитрах.")
        return
    
    amount = int(water[1].replace("мл", ""))
    current_time = str(datetime.now().date())

    if hs.user_username not in WATER:
        WATER[hs.user_username] = dict()

    if not current_time in WATER[hs.user_username]:
        WATER[hs.user_username][current_time] = 0

    WATER[hs.user_username][current_time] += amount

    # Вычисляем остаток до нормы
    remaining = hs.WATER_NORM - WATER[hs.user_username][current_time]

    if remaining > 0:
        await message.reply(f"Данные добавлены! Вы выпили {amount} мл воды. "
                             f"Осталось {remaining} мл до выполнения нормы.")
    else:
        await message.reply(f"Данные добавлены! Вы выпили {amount} мл воды. "
                             f"Поздравляем, вы выполнили норму! 🎉")
        


@router2.message(Command('log_food'))
async def log_food(message: Message):
    global CALLORIE
    message_ = message.text.split()
    if len(message_) < 2:
        await message.answer("Введите название продукта")
    else:
        message_ = message_[1]
        en_message = await translate(message_)
        CALLORIE = await get_product_calories(en_message)
        CALLORIE *=100

        current_time = str(datetime.now().date())
        if not hs.user_username in CALLORIES:
            CALLORIES[hs.user_username] = dict()
        if not current_time in CALLORIES[hs.user_username]:
            CALLORIES[hs.user_username][current_time] = 0

        await message.answer(f"{message_} — {CALLORIE} ккал на 100 г. Сколько грамм вы съели?")


@router2.message(lambda message: message.text.isdigit())
async def handle_number(message: Message):
    global CALLORIE
    number = int(message.text.strip())  
    current_time = str(datetime.now().date())
    CALLORIES[hs.user_username][current_time] += number*CALLORIE // 100
    await message.answer(f"Записано {number*CALLORIE // 100} ккал.")


@router2.message(Command("log_workout"))
async def log_workout(message: Message):
    if len(message.text.split()) != 3:
        await message.reply("Пожалуйста, укажите тип тренировки и время (в минутах) в формате: /log_workout <тип тренировки> <время (мин)>")
        return
    _, activity, minute = message.text.split()

    try:
        duration = int(minute)
    except ValueError:
        await message.reply("Время должно быть числом (в минутах).")
        return

    if duration <= 0:
        await message.reply("Время должно быть положительным числом.")
        return

    total_calories, extra_water = calculate_calories_and_water(activity, duration)

    #---------------------------logging----------------------------
    current_time = str(datetime.now().date())
    if not hs.user_username in TRAIN:
            TRAIN[hs.user_username] = dict()
    if not current_time in TRAIN[hs.user_username]:
            TRAIN[hs.user_username][current_time] = 0
    TRAIN[hs.user_username][current_time] += total_calories


    #-------------------------------------------------------------

    response_message = f"{activity.capitalize()} {duration} минут — {total_calories} ккал. "
    if extra_water > 0:
        response_message += f"Дополнительно: выпейте {extra_water} мл воды."

    await message.answer(response_message)


@router2.message(Command("check_progress"))
async def check_progress(message: Message):
    current_time = str(datetime.now().date())
    if hs.user_username in WATER:
        if current_time in WATER[hs.user_username]:
            cur_water = WATER[hs.user_username][current_time]

            await message.answer(f"📊 Прогресс:\n \
                                    Вода:\n \
                                    - Выпито: {cur_water} мл из {hs.WATER_NORM}. \n\
                                    - Осталось: {hs.WATER_NORM - cur_water}.")
        else:
            await message.answer("Нет данных о воде по сегодняшнему дню(")
    else:
        await message.answer("Вы еще не создали профиль(")
        
    if hs.user_username in TRAIN:
        if current_time in CALLORIES[hs.user_username]:
            calorries_sum = CALLORIES[hs.user_username][current_time]
            total_calories = TRAIN[hs.user_username][current_time]
            await message.answer(f"Калории:\n \
                                - Потреблено: {calorries_sum} ккал из {hs.CALLORIES_NORM} ккал. \n\
                                - Сожжено: {total_calories} ккал. \n\
                                - Баланс: {calorries_sum-total_calories} ккал.")
        else:
            await message.answer("Нет данных о калориях по сегодняшнему дню(")


# Функция для построения графиков прогресса по воде и калориям (TelegramNetworkError)
@router2.message(Command("plot_progress"))
async def check_progress(message: Message):
    def plot(x, y, title=""):
        plt.figure()
        plt.plot(x, y)
        plt.title(title)
        plt.xlabel('x')
        plt.ylabel('y')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()  
        buf.seek(0)  
        photo = BufferedInputFile(buf, filename='plot.png')
        return photo

    lst = [WATER, CALLORIES, TRAIN]
    title = ['воды', 'калорий', 'тренировок']
    for elem in lst:
        keys = list(elem[hs.user_username].keys())
        values = [val for key, val in elem[hs.user_username].items()]
        photo = plot(keys, values, f"График прогресса {title}")
        await message.answer_photo(photo=photo)


from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton

@router2.message(Command("recommendations"))
async def recommendations(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Тренировки",callback_data="train"))
    builder.add(InlineKeyboardButton(text="Рацион",callback_data="eat"))
    await message.answer(
        "Выбери необходимую рекомендацию",
        reply_markup=builder.as_markup()
    )

@router2.callback_query(F.data == "eat")
async def rec_eat(callback: CallbackQuery):
    s = '''Пейте воду: Убедитесь, что вы пьете достаточное количество воды. Вода помогает контролировать аппетит.
    Избегайте переработанных продуктов: Старайтесь минимизировать потребление сахара и переработанных углеводов.
    Контролируйте порции: Следите за размерами порций, особенно при приеме более калорийных продуктов.
    Слушайте свой организм: Уважайте сигналы голода и сытости, не перекусывайте без необходимости.
        
    Ключ к успешному снижению калорий заключается в разнообразии рациона и выборе продуктов, насыщенных питательными веществами. '''

    await callback.message.answer(s)

@router2.callback_query(F.data == "train")
async def rec_train(callback: CallbackQuery):
    s = '''Плавание — это отличный способ тренировки всего тела. Рекомендуется плавать минимум 3-4 раза в неделю по 30-60 минут.
    Попробуйте плавать с переменной интенсивностью. Например, 1-2 минуты быстрой скорости чередовать с 1 минутой медленного плавания. Это может повысить ваш метаболизм и улучшить сердечно-сосудистую выносливость.
    
    В дополнение к плаванию, включите аэробные упражнения, такие как быстрая ходьба, бег, езда на велосипеде или занятия на эллиптическом тренажере. Это укрепит сердечно-сосудистую систему и поможет сжиганию калорий.
    '''
    await callback.message.answer(s)


    