from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция для клавиатуры Назад
async def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_foreign")]]
    )
    return keyboard

# Функция для клавиатуры подтверждения
async def get_confirm_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_foreign")],
            [InlineKeyboardButton(text="↩️ Главное меню", callback_data="start")]
        ]
    )
    return keyboard

# Функция для клавиатуры завершения отчета
async def get_finish_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, добавить новый расход", callback_data="next_point")],
            [InlineKeyboardButton(text="❌ Нет, завершить отчет", callback_data="skip")],
        ]
    )
    return keyboard


start = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]]
    )