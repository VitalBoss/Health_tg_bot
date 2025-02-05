from aiogram.fsm.state import StatesGroup, State

class Person(StatesGroup):
    sex = State()
    age = State()
    height = State()
    weight = State()
    city = State()
    activity = State()
    calorie_goal = State()

# p = Person()
# print(p.sex.state)
