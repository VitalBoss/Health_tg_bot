import asyncio
import aiohttp
from googletrans import Translator

async def fetch_weather_data(session, city_name, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"Error fetching weather data for {city_name}: {response.status}")


async def get_temp(city):
    api_key = 'e0ad4718aa5dbe6b4d4c37d9503b3337'
    cities = [city]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for city in cities:
            task = asyncio.create_task(fetch_weather_data(session, city, api_key))
            tasks.append(task)
        
        result = await asyncio.gather(*tasks)
        return result[0]['main']['temp']
    
def prepare_data(users:dict):
    cols = ['sex', 'city']
    print(users)
    for key, val in users.items():
        if not key in cols:
            users[key] = int(val)
    return users



async def calculate_water_norm(users:dict):
    users = prepare_data(users)
    base_norm = users['weight'] * 30
    additional_activity = int(users['activity'] / 30) * 500
    temperature_celsius = await get_temp(users['city'])

    if temperature_celsius > 25:
        additional_temperature = 500
    elif temperature_celsius >= 32:
        additional_temperature = 750
    elif temperature_celsius >= 40:
        additional_activity = 1000
    else:
        additional_temperature = 0

    if users['sex'] == 'Male':
        total_norm = base_norm + additional_activity + additional_temperature
    else:
        total_norm = 0.8 * (base_norm + additional_activity + additional_temperature)

    return total_norm


def calculate_calories_norm(users:dict):
    users = prepare_data(users)
    weight_kg, height_cm, age_years = users['weight'], users['height'], users['age']
    calories_base = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    
    if users['activity'] < 45:
        additional_calories = 200
    elif 45 <= users['activity'] <= 70:
        additional_calories = 300
    elif users['activity'] > 70:
        additional_calories = 400
    else:
        additional_calories = 0

    if users['sex'] == 'Male':
        total_calories = calories_base + additional_calories
    else:
        total_calories = 0.8 * (calories_base + additional_calories)
    
    return int(total_calories)


async def get_product_calories(product_name):
    api_key = 'GEtuGeSRrnI1VV1UuBOyY1ZvdkggmwvwQXVr9tNP'
    
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={product_name}'
    ans = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            for food in data['foods']:
                if food['description'].lower() == product_name.lower():
                    calories = food['foodNutrients'][0]['value']
                    ans.append(calories)
    return max(ans)

async def translate(word):
    translator = Translator()
    translation = await translator.translate(word, dest='en', source='ru')
    return translation.text

def calculate_calories_and_water(workout_type: str, duration: int):
    calories_per_minute = {
        'бег': 10,       
        'ходьба': 5,      
        'велосипед': 8, 
        'плавание' : 12,
        'фитнес' : 8
        }

    if not workout_type in calories_per_minute:
        return False, f"Нет подходящего вида деятельности. Выберите виде активности из списка\n {calories_per_minute.keys()}"
    base_calories = calories_per_minute.get(workout_type.lower(), 0)
    total_calories = base_calories * duration

    extra_water = (duration // 30) * 200  

    return total_calories, extra_water

