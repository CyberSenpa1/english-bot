from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изучение английского')],
    [KeyboardButton(text='Статистика')],
    [KeyboardButton(text='О нас')]
], resize_keyboard=True, one_time_keyboard=True
)

learn_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Старт")],
    [KeyboardButton(text="Сложность")],
    [KeyboardButton(text="Назад")],
], resize_keyboard=True, one_time_keyboard=True
)

difficult = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="1")],
    [KeyboardButton(text="2")],
    [KeyboardButton(text="3")],
    [KeyboardButton(text="4")],
    [KeyboardButton(text="5")]
], resize_keyboard=True, one_time_keyboard=True
)

statistic_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Назад")]
])